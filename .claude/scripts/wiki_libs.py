#!/usr/bin/env python3
import os
import json
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError
import socket


def find_vault_root() -> Path:
    return Path(__file__).parent.parent.parent


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


def _fetch_via_api(env: dict) -> 'tuple[list[tuple[str, str]], str] | None':
    required = ('OBSIDIAN_PROTOCOL', 'OBSIDIAN_HOST', 'OBSIDIAN_PORT', 'OBSIDIAN_API_KEY')
    if not all(k in env for k in required):
        return None

    base = f"{env['OBSIDIAN_PROTOCOL']}://{env['OBSIDIAN_HOST']}:{env['OBSIDIAN_PORT']}"
    headers = {
        'Authorization': f"Bearer {env['OBSIDIAN_API_KEY']}",
        'Accept': 'application/json',
    }

    def _list_dir(dir_path: str) -> list:
        """Recursively collect all .md file paths under dir_path."""
        encoded = dir_path.replace(' ', '%20')
        url = f"{base}/vault/{encoded}" if encoded else f"{base}/vault/"
        req = Request(url, headers=headers)
        with urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        md_paths = []
        for entry in data.get('files', []):
            if entry.endswith('/'):
                subdir = dir_path + entry
                if not subdir.startswith('.claude/'):
                    md_paths.extend(_list_dir(subdir))
            elif entry.endswith('.md'):
                full = dir_path + entry
                if not full.startswith('.claude/'):
                    md_paths.append(full)
        return md_paths

    try:
        md_files = _list_dir('')

        files = []
        for path in md_files:
            encoded = path.replace(' ', '%20')
            file_headers = {**headers, 'Accept': 'text/markdown'}
            req = Request(f"{base}/vault/{encoded}", headers=file_headers)
            try:
                with urlopen(req, timeout=5) as resp:
                    content = resp.read().decode('utf-8')
                files.append((path, content))
            except (URLError, OSError):
                print(f"  warning: could not fetch {path} via API", file=sys.stderr)
        return files, 'api'
    except (URLError, OSError, socket.timeout):
        return None


def _fetch_via_filesystem(vault_root: Path) -> 'tuple[list[tuple[str, str]], str]':
    claude_dir = str((vault_root / '.claude').resolve())
    files = []
    for root, dirs, filenames in os.walk(vault_root):
        root_path = Path(root)
        dirs[:] = [
            d for d in dirs
            if str((root_path / d).resolve()) != claude_dir and not d.startswith('.')
        ]
        for filename in filenames:
            if not filename.endswith('.md'):
                continue
            full_path = root_path / filename
            rel_path = str(full_path.relative_to(vault_root))
            content = full_path.read_text(encoding='utf-8')
            files.append((rel_path, content))
    return files, 'filesystem'


def get_vault_files(vault_root: Path, env: dict) -> 'tuple[list[tuple[str, str]], str]':
    result = _fetch_via_api(env)
    if result is not None:
        return result
    return _fetch_via_filesystem(vault_root)


def parse_wikilinks(content: str) -> 'list[tuple[str, int]]':
    pattern = re.compile(r'\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]')
    code_span = re.compile(r'`[^`]*`')
    result = []
    for lineno, line in enumerate(content.splitlines(), 1):
        clean = code_span.sub('', line)
        for match in pattern.finditer(clean):
            target = match.group(1).strip()
            result.append((target, lineno))
    return result
