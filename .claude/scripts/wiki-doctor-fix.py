#!/usr/bin/env python3
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))
from wiki_libs import find_vault_root

CHECKLIST_ORDER = [
    'broken_wikilinks',
    'stale_references',
    'missing_index_links',
    'orphan_notes',
    'duplicate_pages',
    'conflicting_claims',
    'thin_pages',
    'oversized_pages',
    'weak_canonical_ownership',
]

LLM_ITEMS = {
    'orphan_notes',
    'duplicate_pages',
    'conflicting_claims',
    'thin_pages',
    'oversized_pages',
    'weak_canonical_ownership',
}


def _rewrite_file(path: Path, replacements: list) -> None:
    content = path.read_text(encoding='utf-8')
    for old, new in replacements:
        content = content.replace(old, new)
    path.write_text(content, encoding='utf-8')


def fix_broken_wikilinks(violations: list, vault_root: Path) -> int:
    by_file: dict = {}
    for v in violations:
        by_file.setdefault(v['source'], []).append(v)
    count = 0
    for source, items in by_file.items():
        replacements = [(f"[[{v['link']}]]", v['link']) for v in items]
        _rewrite_file(vault_root / source, replacements)
        count += len(items)
    return count


def fix_stale_references(violations: list, vault_root: Path) -> int:
    by_file: dict = {}
    for v in violations:
        by_file.setdefault(v['source'], []).append(v)
    count = 0
    for source, items in by_file.items():
        replacements = [(f"[[{v['link']}]]", f"[[{v['suggested']}]]") for v in items]
        _rewrite_file(vault_root / source, replacements)
        count += len(items)
    return count


def fix_missing_index_links(violations: list, vault_root: Path) -> int:
    if not violations:
        return 0
    index_path = vault_root / 'wiki' / 'index.md'
    content = index_path.read_text(encoding='utf-8').rstrip()
    stubs = '\n'.join(f'- [[{Path(p).stem}]]' for p in violations)
    index_path.write_text(content + '\n\n' + stubs + '\n', encoding='utf-8')
    return len(violations)


FIXERS = {
    'broken_wikilinks':    fix_broken_wikilinks,
    'stale_references':    fix_stale_references,
    'missing_index_links': fix_missing_index_links,
}


def main() -> None:
    vault_root = find_vault_root()
    report_path = vault_root / '.claude' / 'tmp-wiki-doctor-report.json'

    if not report_path.exists():
        print('No report found. Run wiki-doctor-report.py first.')
        sys.exit(1)

    report = json.loads(report_path.read_text(encoding='utf-8'))
    violations = report['violations']

    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    summary: dict = {}

    for key in CHECKLIST_ORDER:
        if key in LLM_ITEMS:
            continue
        items = violations.get(key, [])
        if not items:
            continue
        fixer = FIXERS.get(key)
        if fixer:
            summary[key] = fixer(items, vault_root)

    report_path.unlink()

    print(f'\nwiki-doctor fix — {timestamp}\n')
    print(f'  stale references rewritten:  {summary.get("stale_references", 0)}')
    print(f'  broken links stripped:       {summary.get("broken_wikilinks", 0)}')
    print(f'  index entries added:         {summary.get("missing_index_links", 0)}')
    print()


if __name__ == '__main__':
    main()
