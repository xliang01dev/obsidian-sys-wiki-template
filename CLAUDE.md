# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose
This vault is an isolated wiki for research and improvement.
Use it to turn rough inputs into durable notes about architecture, tradeoffs, failure modes, and design decisions.
Do not assume access to any other vault, repo, or personal context.

## Session rules
- Read this file first.
- Treat this vault as isolated.
- Read a folder's `index.md` before working deeply in that folder.
- Ask before deleting, renaming, moving files, or changing folder structure.
- Prefer updating existing notes over creating duplicates.
- Prefer concise markdown notes with links over long chat-only answers.
- Prefer to use the Obsidian local API MCP server instead of directly reading from the file system.

## Folder roles
- `raw/`: source material only; clipped articles, transcripts, paper notes, and rough evidence. Do not overwrite raw sources with conclusions.
- `inbox/`: temporary capture area for unprocessed ideas, snippets, and rough notes. Items here should eventually be triaged into `raw/` or `wiki/`. (Create this folder on first use if it doesn't exist.)
- `wiki/`: durable knowledge pages for concepts, patterns, tradeoffs, and architectures. This is the main long-term knowledge layer.
- `templates/`: reusable note templates — do not write content here, only structure.
- `maintenance/`: dated health reports, lint runs, repair logs, and unresolved wiki maintenance issues. Create one file per run and update `maintenance/index.md`.
- `output/`: generated summaries or exports requested by the user. Not the source of truth.

## Templates

| File | Use for |
|------|---------|
| `template-system-concept.md` | New wiki pages for a concept |
| `template-system-pattern.md` | Architectural patterns |
| `template-system-caching.md` | Caching strategy deep-dives |
| `template-system-case-study.md` | Real-world system breakdowns |
| `template-maintenance.md` | Vault health reports; use for all lint/repair runs in `maintenance/` |
| `index-common.md` | Shared structure for folder-level `index.md` files |

Always use the appropriate template when creating a new wiki page. Copy the template, fill it in, and place the result in `wiki/`.

## Ingest rules
When new material is added:
- check whether a canonical page already exists before creating a new one
- update existing pages first when possible
- create a new page only when the concept is truly new
- keep raw sources in `raw/`
- move durable synthesis into `wiki/`
- update the relevant `index.md` files

## Conflict handling
When new material conflicts with existing notes:
- do not silently overwrite prior conclusions
- update the canonical page and add a short `Conflict`, `Open Questions`, or `Changed Understanding` section when needed
- preserve uncertainty when sources disagree
- prefer one canonical page per concept
- if duplicates exist, identify the canonical page and mark the others for merge or redirect

## Self-healing rules
For wiki health reports, use @templates/template-maintenance.md.
When running a lint or repair pass:
- create a new dated markdown file in `maintenance/`
- name it like `YYYY-MM-DD-lint.md` or `YYYY-MM-DD-repair.md`
- fill it using the maintenance template
- update `maintenance/index.md` with a link and short summary

Check for:
- broken wikilinks
- orphan notes
- duplicate or near-duplicate pages
- stale claims
- conflicting claims
- missing index links
- thin pages that should be merged
- oversized pages that should be split

Auto-fix only obvious structural issues such as broken links with an unambiguous target or missing index links.
Ask before performing destructive merges, page deletions, or major restructures.

## Writing standard
For durable notes, prefer sections like:
- what it is
- why it matters
- when to use it
- when not to use it
- tradeoffs
- failure modes
- related concepts
- source links

## File rules
- Use `kebab-case.md` for durable notes.
- Use dated names for research logs when needed.
- Avoid vague filenames like `misc.md` or `notes.md`.
- Never operate outside this vault.
- Never publish or push changes unless asked.
