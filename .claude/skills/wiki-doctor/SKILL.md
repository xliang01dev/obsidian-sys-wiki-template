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

- `wiki/` pages
- links between notes
- folder index files
- template references
- note overlap and contradiction

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

## Workflow

1. Inspect the target notes, links, and referenced pages.
2. Classify issues: broken link, stale reference, duplicate content, conflicting claim, orphaned page, or weak canonical ownership.
3. Repair obvious structural issues first.
4. Compare overlapping or conflicting notes.
5. Choose the canonical destination for each concept.
6. Update the canonical page, trim duplication, and preserve unresolved conflicts where needed.
7. Summarize what was repaired, merged, removed, or flagged.

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
