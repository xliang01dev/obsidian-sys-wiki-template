#!/usr/bin/env python3
from __future__ import annotations

import sys
import json
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).parent))
from wiki_libs import (
    find_vault_root, report_path, utc_timestamp, safe_vault_path, atomic_write_text,
    FILE_READ_ERRORS, CHECKLIST_ORDER, LLM_ITEMS,
)


def _group_by_source(violations: list[dict]) -> dict[str, list[dict]]:
    by_file: dict[str, list[dict]] = {}
    for v in violations:
        by_file.setdefault(v['source'], []).append(v)
    return by_file


def _rewrite_file(path: Path, replacements: list[tuple[str, str]]) -> int:
    try:
        content = path.read_text(encoding='utf-8')
    except FILE_READ_ERRORS as exc:
        print(f"  warning: could not read {path} ({exc}) — skipped", file=sys.stderr)
        return 0

    applied = 0
    for old, new in replacements:
        occurrences = content.count(old)
        if occurrences:
            content = content.replace(old, new)
            applied += occurrences
        else:
            print(f"  warning: {old!r} not found in {path} (likely has an alias/anchor) — skipped", file=sys.stderr)

    if applied:
        try:
            atomic_write_text(path, content)
        except OSError as exc:
            print(f"  warning: could not write {path} ({exc}) — skipped", file=sys.stderr)
            return 0
    return applied


def _fix_links(violations: list[dict], vault_root: Path, link_for: Callable[[dict], tuple[str, str]]) -> int:
    count = 0
    for source, items in _group_by_source(violations).items():
        target = safe_vault_path(vault_root, source)
        if target is None:
            print(f"  warning: refusing to write outside vault: {source!r} — skipped", file=sys.stderr)
            continue
        replacements = [link_for(v) for v in items]
        count += _rewrite_file(target, replacements)
    return count


def fix_broken_wikilinks(violations: list[dict], vault_root: Path) -> int:
    return _fix_links(violations, vault_root, lambda v: (f"[[{v['link']}]]", v['link']))


def fix_stale_references(violations: list[dict], vault_root: Path) -> int:
    return _fix_links(violations, vault_root, lambda v: (f"[[{v['link']}]]", f"[[{v['suggested']}]]"))


def fix_missing_index_links(violations: list[str], vault_root: Path) -> int:
    if not violations:
        return 0
    index_path = vault_root / 'wiki' / 'index.md'
    try:
        content = index_path.read_text(encoding='utf-8').rstrip()
    except FILE_READ_ERRORS as exc:
        print(f"  warning: could not read {index_path} ({exc}) — skipped", file=sys.stderr)
        return 0

    stubs = '\n'.join(f'- [[{Path(p).stem}]]' for p in violations)
    try:
        atomic_write_text(index_path, content + '\n\n' + stubs + '\n')
    except OSError as exc:
        print(f"  warning: could not write {index_path} ({exc}) — skipped", file=sys.stderr)
        return 0
    return len(violations)


FIXERS = {
    'broken_wikilinks': fix_broken_wikilinks,
    'stale_references': fix_stale_references,
    'missing_index_links': fix_missing_index_links,
}
# orphan_notes/thin_pages/oversized_pages are script-detected but intentionally
# have no fixer here: merging, splitting, and link-vs-delete calls need LLM judgment.


def apply_fixes(violations: dict, vault_root: Path) -> dict[str, int]:
    summary: dict[str, int] = {}
    for key in CHECKLIST_ORDER:
        if key in LLM_ITEMS:
            continue
        items = violations.get(key, [])
        if not items:
            continue
        fixer = FIXERS.get(key)
        if fixer:
            summary[key] = fixer(items, vault_root)
    return summary


def main() -> None:
    vault_root = find_vault_root()
    rpt_path = report_path(vault_root)

    if not rpt_path.exists():
        print('No report found. Run wiki_doctor_report.py first.', file=sys.stderr)
        sys.exit(1)

    try:
        report = json.loads(rpt_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        print(f'Could not parse report at {rpt_path}: {exc}', file=sys.stderr)
        sys.exit(1)

    summary = apply_fixes(report['violations'], vault_root)
    rpt_path.unlink()

    timestamp = utc_timestamp()
    print(f'\nwiki-doctor fix — {timestamp}\n')
    print(f'  stale references rewritten:  {summary.get("stale_references", 0)}')
    print(f'  broken links stripped:       {summary.get("broken_wikilinks", 0)}')
    print(f'  index entries added:         {summary.get("missing_index_links", 0)}')
    print()


if __name__ == '__main__':
    main()
