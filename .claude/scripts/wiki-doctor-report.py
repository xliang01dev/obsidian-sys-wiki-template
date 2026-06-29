#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent))
from wiki_libs import find_vault_root, load_env, get_vault_files, parse_wikilinks


def normalize_slug(target: str) -> str:
    return target.lower().replace(' ', '-')


def build_slug_index(files: list) -> dict:
    return {Path(path).stem: path for path, _ in files}


def build_link_graph(files: list) -> dict:
    return {path: parse_wikilinks(content) for path, content in files}


def check_broken_wikilinks(link_graph: dict, slug_index: dict) -> list:
    violations = []
    for source, links in link_graph.items():
        if not source.startswith('wiki/'):
            continue
        for target, line in links:
            slug = Path(target).stem if '/' in target else target
            if slug not in slug_index and normalize_slug(slug) not in slug_index:
                violations.append({'source': source, 'link': target, 'line': line})
    return violations


def check_stale_references(link_graph: dict, slug_index: dict) -> list:
    violations = []
    for source, links in link_graph.items():
        if not source.startswith('wiki/'):
            continue
        for target, line in links:
            slug = Path(target).stem if '/' in target else target
            if slug not in slug_index:
                norm = normalize_slug(slug)
                if norm in slug_index:
                    violations.append({'source': source, 'link': target, 'line': line, 'suggested': norm})
    return violations


def check_orphan_notes(files: list, link_graph: dict) -> list:
    wiki_files = {path for path, _ in files if path.startswith('wiki/') and path != 'wiki/index.md'}
    referenced = set()
    for source, links in link_graph.items():
        for target, _ in links:
            norm = normalize_slug(target)
            for wiki_path in wiki_files:
                stem = Path(wiki_path).stem
                if stem == target or stem == norm:
                    referenced.add(wiki_path)
    return sorted(wiki_files - referenced)


def check_missing_index_links(files: list, link_graph: dict) -> list:
    wiki_files = [path for path, _ in files if path.startswith('wiki/') and path != 'wiki/index.md']
    index_content = next((c for p, c in files if p == 'wiki/index.md'), '')
    missing = []
    for path in wiki_files:
        slug = Path(path).stem
        if f'[[{slug}]]' not in index_content and f'[[{slug}|' not in index_content:
            missing.append(path)
    return missing


def check_thin_pages(files: list, threshold: int = 150) -> list:
    return [
        {'file': path, 'word_count': len(content.split())}
        for path, content in files
        if path.startswith('wiki/') and path != 'wiki/index.md' and len(content.split()) < threshold
    ]


def check_oversized_pages(files: list, threshold: int = 4000) -> list:
    return [
        {'file': path, 'word_count': len(content.split())}
        for path, content in files
        if path.startswith('wiki/') and path != 'wiki/index.md' and len(content.split()) > threshold
    ]


def run_checks(files: list, link_graph: dict, slug_index: dict) -> dict:
    tasks = {
        'broken_wikilinks':    (check_broken_wikilinks,    (link_graph, slug_index)),
        'stale_references':    (check_stale_references,    (link_graph, slug_index)),
        'orphan_notes':        (check_orphan_notes,        (files, link_graph)),
        'missing_index_links': (check_missing_index_links, (files, link_graph)),
        'thin_pages':          (check_thin_pages,          (files,)),
        'oversized_pages':     (check_oversized_pages,     (files,)),
    }
    results = {}
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = {executor.submit(fn, *args): key for key, (fn, args) in tasks.items()}
        for future in as_completed(futures):
            results[futures[future]] = future.result()
    return results


CHECKLIST = [
    ('broken_wikilinks',         'broken wikilinks',   'script'),
    ('stale_references',         'stale references',   'script'),
    ('orphan_notes',             'orphan notes',       'script'),
    ('missing_index_links',      'missing index links','script'),
    ('thin_pages',               'thin pages',         'script'),
    ('oversized_pages',          'oversized pages',    'script'),
    ('duplicate_pages',          'duplicate pages',    'LLM'),
    ('conflicting_claims',       'conflicting claims', 'LLM'),
    ('weak_canonical_ownership', 'weak ownership',     'LLM'),
]


def print_checklist(violations: dict, access_mode: str, timestamp: str) -> None:
    print(f'\nwiki-doctor report — {timestamp}  [{access_mode}]\n')
    for key, label, mode in CHECKLIST:
        items = violations.get(key, [])
        count = len(items)
        checked = '[x]' if count == 0 else '[ ]'
        if mode == 'LLM':
            detail = '(LLM)'
        elif count == 0:
            detail = ''
        else:
            unit = 'violation' if count == 1 else 'violations'
            detail = f'{count} {unit}  (script)'
        print(f'- {checked} {label:<24} {detail}')
    print()


def main() -> None:
    vault_root = find_vault_root()
    env = load_env(vault_root)
    files, access_mode = get_vault_files(vault_root, env)

    link_graph = build_link_graph(files)
    slug_index = build_slug_index(files)
    results = run_checks(files, link_graph, slug_index)

    violations = {
        'broken_wikilinks':         results.get('broken_wikilinks', []),
        'stale_references':         results.get('stale_references', []),
        'orphan_notes':             results.get('orphan_notes', []),
        'duplicate_pages':          [],
        'conflicting_claims':       [],
        'missing_index_links':      results.get('missing_index_links', []),
        'thin_pages':               results.get('thin_pages', []),
        'oversized_pages':          results.get('oversized_pages', []),
        'weak_canonical_ownership': [],
    }

    deterministic_total = sum(
        len(v) for k, v in violations.items()
        if k not in ('duplicate_pages', 'conflicting_claims', 'weak_canonical_ownership')
    )

    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    report = {
        'vault_root': str(vault_root),
        'generated_at': timestamp,
        'access_mode': access_mode,
        'violations': violations,
        'summary': {
            'total_files_scanned': len(files),
            'deterministic_violations': deterministic_total,
            'probabilistic_violations': 0,
        },
    }

    report_path = vault_root / '.claude' / 'tmp-wiki-doctor-report.json'
    report_path.unlink(missing_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')

    print_checklist(violations, access_mode, timestamp)


if __name__ == '__main__':
    main()
