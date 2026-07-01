---
name: wiki-doctor
description: Maintain wiki integrity through linting and self-healing. Repair broken links, detect conflicting content, reduce duplication, and converge notes toward clear canonical pages.
---

# Wiki Doctor

Use this skill to keep the wiki structurally healthy and semantically coherent over time.

## Purpose

- Repair or remove broken links.
- Detect contradictory or overlapping claims across notes.
- Reduce duplication by converging content toward canonical pages.
- Preserve source evidence while improving synthesized wiki pages.
- Help the wiki evolve toward clearer, more internally consistent knowledge.

## Scope

This skill is for wiki maintenance, not general system debugging.

Primary targets:

- `wiki/` pages and the links between them
- `wiki/index.md` (for missing index link checks)
- note overlap and contradiction within `wiki/`

Out of scope: `maintenance/`, `templates/`, `raw/`, `inbox/`, configuration files.

Do not use this skill as the default tool for MCP, CLI, or unrelated configuration troubleshooting.

## Canonical rules

- `wiki/` contains canonical synthesized understanding.
- `raw/` contains source material, evidence, excerpts, transcripts, and references.
- `inbox/` contains unprocessed or provisional captures.
- When content overlaps, prefer updating an existing canonical wiki page over creating a parallel explanation.
- Do not rewrite or delete source material in `raw/` just because a canonical page has improved.

## Responsibilities

### Broken links

- Repair a broken wiki link when the intended target is obvious.
- If a note was renamed or moved, update stale links to the current path.
- If no valid target exists, remove the broken wiki-link syntax or replace it with plain text.
- Do not leave known broken links unresolved if a safe repair is available.

### Conflicting content

- Detect notes that make conflicting claims about the same concept.
- Distinguish evidence from synthesis.
- If one page is clearly canonical, update it to reflect the best-supported current consensus.
- If the conflict is unresolved, preserve the disagreement explicitly instead of flattening it.
- Add a short conflict note or TODO where necessary so the disagreement remains visible.

### Duplication and overlap

- Detect duplicate or near-duplicate notes.
- Merge overlapping wiki content into the strongest canonical page when safe.
- Convert weaker duplicates into stubs, redirects, links, or references where useful.
- Prefer one clear home per concept.

### Consensus and convergence

- Favor fewer, stronger canonical pages over multiple partial explanations.
- Keep supporting evidence in `raw/` and synthesized understanding in `wiki/`.
- When several notes partially overlap, converge them toward one maintained page.
- If true consensus is not possible, record the disagreement explicitly rather than pretending it does not exist.

## Lint checklist

Lint passes when all 9 items are resolved or explicitly deferred:

1. **Broken wikilinks** — links with no valid target (repair if intent is obvious, else strip the link syntax)
2. **Stale/renamed references** — links pointing to a note that moved or was renamed
3. **Orphan notes** — pages not linked from any index or related page
4. **Missing index links** — wiki pages not referenced from their folder's index.md
5. **Thin pages** — content too sparse to stand alone, candidate for merging into a canonical page
6. **Oversized pages** — content that's grown too large and should be split
7. **Duplicate or near-duplicate pages** — overlapping content that should converge to one canonical page
8. **Conflicting claims** — notes that disagree about the same concept (flagged explicitly if unresolved, not silently flattened)
9. **Weak canonical ownership** — a concept lacking one clear "home" page among several partial explanations

## Workflow

Repeat the following loop until the report is clean or all remaining issues are explicitly deferred.

### Step 1 — Collect data

- If the Obsidian MCP or local API is available: run `wiki_doctor_report.py` (in `.claude/scripts/`) against the vault document graph to collect link, orphan, duplicate, and coverage data.
- If the MCP/API is not available: fetch wiki markdown via filesystem calls and derive the same data manually.

### Step 2 — Generate report

Using the lint checklist as the template, produce a count of violations per category. Record which items are unresolved and which are deferred.

### Step 3 — Fix deterministic issues

Always run `wiki_doctor_fix.py` (in `.claude/scripts/`), even when the report shows zero violations. It applies rule-based fixes and always cleans up the temp report file on exit:
- broken wikilinks with an obvious target
- stale/renamed references
- missing index links
- dead link markup removal

### Step 4 — Re-run report

Re-run Step 1 and Step 2 to measure what was fixed. The remaining violations are those `wiki_doctor_fix.py` could not resolve.

### Step 5 — Fix probabilistic issues (LLM)

Remaining violations require judgment. Apply the rules in **Safe automatic actions** and **Ask before changing** to decide which to fix directly and which to escalate. Typical probabilistic issues:
- duplicate or near-duplicate pages (merge vs. keep depends on semantic overlap)
- conflicting claims (resolve or flag explicitly)
- thin pages (merge or expand)
- oversized pages (split)
- weak canonical ownership (choose canonical home)

### Step 6 — Re-run report

Re-run Step 1 and Step 2.

### Step 7 — Done or loop

- If violations remain: return to Step 1 and repeat.
- If the report is clean: done. Emit the output summary in the conversation.
  - If any `wiki/` pages were modified during this run, also write a dated `maintenance/YYYY-MM-DD-lint.md` report (using `templates/template-maintenance.md`) and update `maintenance/index.md`.
  - If only scripts or non-wiki files were changed, skip the maintenance file — no report needed.

## Fetching page content

Read only what you need — do not bulk-export all wiki pages.

1. **QMD search first** — for each concept or page being analyzed for duplicates, conflicts, or ownership, call `mcp__qmd__query` with semantic sub-queries describing the concept. Retrieve the top 3–5 results to identify which pages are semantically closest. Use `minScore: 0.5` to filter low-confidence matches.
2. **Targeted reads** — call `mcp__obsidian__vault_read` for pages surfaced as likely candidates by the search, and for any pages you already know are relevant from context.
3. **Single-file fetch** — if you need a specific page by name rather than by search, use `mcp__qmd__get` with the file path (e.g. `wiki/context-engineering.md`).

Do **not** call `mcp__qmd__multi_get` with `wiki/*.md` — this exports the entire wiki and will exceed context limits.

## Safe automatic actions

Apply directly when the change is local, low-risk, and reversible:

- fix broken links with obvious intended targets
- update renamed or moved note references
- remove dead link markup when no target exists
- merge trivial duplicate sections into a canonical page
- add conflict markers or TODOs for unresolved contradictions
- tighten index or template references when the intended file is clear

## Ask before changing

Stop and ask before:

- deleting substantial content
- merging notes with meaningful semantic differences
- changing the meaning of a canonical page without strong support
- resolving a disputed claim where evidence is ambiguous
- making large-scale structural reorganization across many notes

## Verification rules

Never stop at "fixed" without checking.

- If a link was broken, verify the new target exists.
- If a note was merged, verify the canonical page still reads cleanly.
- If a duplicate was reduced, verify useful context was not lost.
- If a conflict was flagged, verify the contradiction is now visible in the canonical location.
- If an index or template reference was updated, verify the file path resolves.

## Output format

Return:

- Issues found
- Broken links repaired or removed
- Conflicts flagged or reconciled
- Canonical pages chosen or updated
- Duplicate pages merged, linked, or left in place
- Remaining unresolved items
- Suggested preventive cleanup, if any
