---
name: wiki-ingest
description: Ingest curated source files from `raw/` into the wiki. Read new or changed local source files, preserve them as evidence, and update the relevant canonical `wiki/` pages.
***

# Wiki Ingest

Use this skill to turn curated source material into maintained wiki knowledge.

## Purpose

- Read newly added or changed source files from `raw/`.
- Preserve source material as evidence instead of rewriting it in place.
- Update existing canonical `wiki/` pages whenever possible.
- Create new wiki pages only when the concept is truly new.
- Keep the wiki compounding over time instead of re-answering from raw material every time.

## Scope

Primary inputs:

- markdown files in `raw/`
- text exports in `raw/`
- transcripts, excerpts, clipped articles, and notes in `raw/`
- other local source files that Claude can read directly

Primary outputs:

- updated canonical pages in `wiki/`
- new wiki pages only when justified
- updated indexes or related note links when needed

This skill is for curated local inputs. It is not primarily for autonomous web crawling or broad internet discovery.

## Canonical rules

- `raw/` is the source layer. Do not replace it with summarized content.
- `wiki/` is the synthesized layer. Durable understanding belongs there.
- Prefer updating an existing `wiki/` page over creating a duplicate.
- One source may improve multiple wiki pages.
- If the source introduces conflict, preserve the evidence and surface the disagreement.

## Ingestion workflow

1. Identify the new or changed source file in `raw/`.
2. Read it fully before deciding what to update.
3. Extract concepts, entities, claims, comparisons, timelines, and terminology worth preserving.
4. Find the existing canonical wiki pages most related to the source.
5. Update those pages with the new material when overlap exists.
6. Create a new wiki page only if the concept does not already have a strong canonical home.
7. Add or repair links between related wiki pages when the new source reveals useful connections.
8. If the source conflicts with the current wiki, update the canonical page carefully and leave the disagreement visible when unresolved.
9. Summarize which wiki pages were updated and what remains uncertain.

## Content rules

- Do not copy raw sources into `wiki/` verbatim unless a short quote is necessary.
- Prefer synthesis over extraction.
- Keep claims tied to the evidence in `raw/`.
- Avoid parallel concept pages that say nearly the same thing.
- If a source is too weak, noisy, or provisional, keep it in `raw/` and note why it was not promoted into `wiki/`.

## Ask before changing

Stop and ask before:

- creating many new wiki pages from one source
- replacing large amounts of canonical content
- collapsing conflicting material into one conclusion when the evidence is weak
- promoting low-quality or unclear source material into canonical knowledge

## Output format

Return:

- Source file processed
- Canonical wiki pages updated
- New wiki pages created, if any
- Important links added or repaired
- Conflicts introduced or surfaced
- Material left only in `raw/`
- Suggested next follow-up, if needed
