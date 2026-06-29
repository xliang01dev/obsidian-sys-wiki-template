#!/usr/bin/env python3
from __future__ import annotations

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from wiki_libs import (
    find_vault_root, load_env, get_vault_files, parse_wikilinks,
    report_path, utc_timestamp, atomic_write_text, CHECKLIST, LLM_ITEMS, VaultFile, WikiLink,
)


def normalize_slug(target: str) -> str:
    return target.lower().replace(' ', '-')


def slug_for(target: str) -> str:
    return Path(target).stem


def is_content_page(path: str) -> bool:
    return path.startswith('wiki/') and path != 'wiki/index.md'


def build_slug_index(files: list[VaultFile]) -> dict[str, str]:
    return {Path(path).stem: path for path, _ in files}


def build_link_graph(files: list[VaultFile]) -> dict[str, list[WikiLink]]:
    return {path: parse_wikilinks(content) for path, content in files}


def check_broken_wikilinks(link_graph: dict[str, list[WikiLink]], slug_index: dict[str, str]) -> list[dict]:
    violations = []
    for source, links in link_graph.items():
        if not source.startswith('wiki/'):
            continue
        for target, line in links:
            slug = slug_for(target)
            if slug not in slug_index and normalize_slug(slug) not in slug_index:
                violations.append({'source': source, 'link': target, 'line': line})
    return violations


def check_stale_references(link_graph: dict[str, list[WikiLink]], slug_index: dict[str, str]) -> list[dict]:
    violations = []
    for source, links in link_graph.items():
        if not source.startswith('wiki/'):
            continue
        for target, line in links:
            slug = slug_for(target)
            if slug not in slug_index:
                norm = normalize_slug(slug)
                if norm in slug_index:
                    violations.append({'source': source, 'link': target, 'line': line, 'suggested': norm})
    return violations


def check_orphan_notes(files: list[VaultFile], link_graph: dict[str, list[WikiLink]]) -> list[str]:
    wiki_files = {path for path, _ in files if is_content_page(path)}
    stems = {path: Path(path).stem for path in wiki_files}
    referenced = set()
    for links in link_graph.values():
        for target, _ in links:
            slug = slug_for(target)
            norm = normalize_slug(slug)
            for wiki_path, stem in stems.items():
                if stem == slug or stem == norm:
                    referenced.add(wiki_path)
    return sorted(wiki_files - referenced)


def check_missing_index_links(files: list[VaultFile], link_graph: dict[str, list[WikiLink]]) -> list[str]:
    wiki_files = [path for path, _ in files if is_content_page(path)]
    index_slugs = {normalize_slug(slug_for(target)) for target, _ in link_graph.get('wiki/index.md', [])}
    missing = []
    for path in wiki_files:
        if normalize_slug(Path(path).stem) not in index_slugs:
            missing.append(path)
    return missing


def check_thin_pages(files: list[VaultFile], threshold: int = 150) -> list[dict]:
    return [
        {'file': path, 'word_count': len(content.split())}
        for path, content in files
        if is_content_page(path) and len(content.split()) < threshold
    ]


def check_oversized_pages(files: list[VaultFile], threshold: int = 4000) -> list[dict]:
    return [
        {'file': path, 'word_count': len(content.split())}
        for path, content in files
        if is_content_page(path) and len(content.split()) > threshold
    ]


def run_checks(files: list[VaultFile], link_graph: dict[str, list[WikiLink]], slug_index: dict[str, str]) -> dict[str, list]:
    return {
        'broken_wikilinks': check_broken_wikilinks(link_graph, slug_index),
        'stale_references': check_stale_references(link_graph, slug_index),
        'orphan_notes': check_orphan_notes(files, link_graph),
        'missing_index_links': check_missing_index_links(files, link_graph),
        'thin_pages': check_thin_pages(files),
        'oversized_pages': check_oversized_pages(files),
    }


def print_checklist(violations: dict[str, list], access_mode: str, timestamp: str) -> None:
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


def build_report(vault_root: Path) -> dict:
    env = load_env(vault_root)
    files, access_mode = get_vault_files(vault_root, env)

    if not files:
        print(f'No wiki/ files found under {vault_root}; nothing to check.', file=sys.stderr)

    link_graph = build_link_graph(files)
    slug_index = build_slug_index(files)
    results = run_checks(files, link_graph, slug_index)

    violations = {
        key: [] if key in LLM_ITEMS else results.get(key, [])
        for key, _, _ in CHECKLIST
    }
    deterministic_total = sum(len(v) for k, v in violations.items() if k not in LLM_ITEMS)

    return {
        'vault_root': str(vault_root),
        'generated_at': utc_timestamp(),
        'access_mode': access_mode,
        'violations': violations,
        'summary': {
            'total_files_scanned': len(files),
            'deterministic_violations': deterministic_total,
            'probabilistic_violations': 0,
        },
    }


def main() -> None:
    vault_root = find_vault_root()
    report = build_report(vault_root)

    atomic_write_text(report_path(vault_root), json.dumps(report, indent=2))
    print_checklist(report['violations'], report['access_mode'], report['generated_at'])


if __name__ == '__main__':
    main()
