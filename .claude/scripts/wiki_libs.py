#!/usr/bin/env python3
from __future__ import annotations

import os
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import URLError


class VaultFile(NamedTuple):
    path: str
    content: str


class VaultFetchResult(NamedTuple):
    files: list[VaultFile]
    access_mode: str


class WikiLink(NamedTuple):
    target: str
    line: int


CHECKLIST = [
    ('broken_wikilinks', 'broken wikilinks', 'script'),
    ('stale_references', 'stale references', 'script'),
    ('orphan_notes', 'orphan notes', 'script'),
    ('missing_index_links', 'missing index links', 'script'),
    ('thin_pages', 'thin pages', 'script'),
    ('oversized_pages', 'oversized pages', 'script'),
    ('duplicate_pages', 'duplicate pages', 'LLM'),
    ('conflicting_claims', 'conflicting claims', 'LLM'),
    ('weak_canonical_ownership', 'weak ownership', 'LLM'),
]

CHECKLIST_ORDER = [key for key, _, _ in CHECKLIST]
LLM_ITEMS = {key for key, _, mode in CHECKLIST if mode == 'LLM'}

REPORT_FILENAME = 'tmp-wiki-doctor-report.json'
API_TIMEOUT = 5
FILE_READ_ERRORS = (OSError, UnicodeDecodeError)


def report_path(vault_root: Path) -> Path:
    return vault_root / '.claude' / REPORT_FILENAME


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def find_vault_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def safe_vault_path(vault_root: Path, rel_path: str) -> Path | None:
    target = (vault_root / rel_path).resolve()
    if not target.is_relative_to(vault_root.resolve()):
        return None
    return target


def atomic_write_text(path: Path, content: str) -> None:
    tmp_path = path.with_name(path.name + '.tmp')
    tmp_path.write_text(content, encoding='utf-8')
    tmp_path.replace(path)


def load_env_from_string(content: str) -> dict:
    env = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, _, value = line.partition('=')
            env[key.strip()] = value.strip()
    return env


def load_env(vault_root: Path) -> dict:
    env_file = vault_root / '.env'
    if not env_file.exists():
        return {}
    return load_env_from_string(env_file.read_text(encoding='utf-8'))


def _fetch_via_api(env: dict) -> VaultFetchResult | None:
    required = ('OBSIDIAN_PROTOCOL', 'OBSIDIAN_HOST', 'OBSIDIAN_PORT', 'OBSIDIAN_API_KEY')
    if not all(k in env for k in required):
        return None

    base = f"{env['OBSIDIAN_PROTOCOL']}://{env['OBSIDIAN_HOST']}:{env['OBSIDIAN_PORT']}"
    headers = {
        'Authorization': f"Bearer {env['OBSIDIAN_API_KEY']}",
        'Accept': 'application/json',
    }
    file_headers = {**headers, 'Accept': 'text/markdown'}

    def _list_dir(dir_path: str) -> list[str]:
        encoded = quote(dir_path, safe='/')
        url = f"{base}/vault/{encoded}"
        req = Request(url, headers=headers)
        with urlopen(req, timeout=API_TIMEOUT) as resp:
            data = json.loads(resp.read())
        md_paths = []
        for entry in data.get('files', []):
            if '..' in entry or entry.startswith('/'):
                print(f"  warning: skipping suspicious vault entry {entry!r}", file=sys.stderr)
                continue
            full = dir_path + entry
            if entry.endswith('/'):
                md_paths.extend(_list_dir(full))
            elif entry.endswith('.md'):
                md_paths.append(full)
        return md_paths

    def _fetch_one(path: str) -> VaultFile | None:
        encoded = quote(path, safe='/')
        req = Request(f"{base}/vault/{encoded}", headers=file_headers)
        try:
            with urlopen(req, timeout=API_TIMEOUT) as resp:
                content = resp.read().decode('utf-8')
            return VaultFile(path, content)
        except (URLError, *FILE_READ_ERRORS) as exc:
            print(f"  warning: could not fetch {path} via API ({exc})", file=sys.stderr)
            return None

    try:
        md_files = _list_dir('wiki/')
        if not md_files:
            return VaultFetchResult([], 'api')

        with ThreadPoolExecutor(max_workers=min(32, len(md_files))) as executor:
            fetched = executor.map(_fetch_one, md_files)
        files = [f for f in fetched if f is not None]
        return VaultFetchResult(files, 'api')
    except (URLError, OSError, json.JSONDecodeError) as exc:
        print(f"  warning: Obsidian API unreachable ({exc}), falling back to filesystem", file=sys.stderr)
        return None


def _fetch_via_filesystem(vault_root: Path) -> VaultFetchResult:
    wiki_root = vault_root / 'wiki'
    files = []
    for root, dirs, filenames in os.walk(wiki_root):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for filename in filenames:
            if not filename.endswith('.md'):
                continue
            full_path = Path(root) / filename
            rel_path = str(full_path.relative_to(vault_root))
            try:
                content = full_path.read_text(encoding='utf-8')
            except FILE_READ_ERRORS as exc:
                print(f"  warning: could not read {rel_path} ({exc})", file=sys.stderr)
                continue
            files.append(VaultFile(rel_path, content))
    return VaultFetchResult(files, 'filesystem')


def get_vault_files(vault_root: Path, env: dict) -> VaultFetchResult:
    result = _fetch_via_api(env)
    if result is not None:
        return result
    return _fetch_via_filesystem(vault_root)


def parse_wikilinks(content: str) -> list[WikiLink]:
    pattern = re.compile(r'\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]')
    code_span = re.compile(r'`[^`]*`')
    result = []
    for lineno, line in enumerate(content.splitlines(), 1):
        clean = code_span.sub('', line)
        for match in pattern.finditer(clean):
            target = match.group(1).strip()
            result.append(WikiLink(target, lineno))
    return result
