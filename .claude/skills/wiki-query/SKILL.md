---
name: wiki-query
description: Answer questions from the wiki by treating `wiki/` as the primary knowledge layer, using `raw/` only as supporting evidence when needed, and surfacing gaps, conflicts, and next-page improvements.
***

# Wiki Query

Use this skill to answer questions from the existing knowledge base.

## Purpose

- Answer from the compiled wiki whenever possible.
- Prefer canonical `wiki/` pages over raw notes or recent captures.
- Use `raw/` as supporting evidence when the wiki is incomplete or the user explicitly wants sources.
- Surface uncertainty, contradiction, and missing coverage instead of overclaiming.
- Turn important gaps discovered during querying into concrete follow-up improvements for the wiki.

## Scope

Use this skill when the question should be answered from the note system.

Primary targets:

- `wiki/` pages
- related project notes when they add necessary local context
- `raw/` notes only as evidence
- `inbox/` only when recent unprocessed context is clearly relevant

Do not use this skill as the default for unrelated coding or general research tasks.

## Retrieval order

1. Check `wiki/` for canonical pages about the topic.
2. Check related project folders for context-specific details.
3. Check `raw/` only if the wiki is incomplete, ambiguous, or needs evidence.
4. Check `inbox/` only if recent provisional material is directly relevant.

## Query rules

- By default, answer from `wiki/` first.
- Prefer fewer, stronger canonical pages over many scattered notes.
- Distinguish synthesized understanding from source evidence.
- Do not silently flatten conflicting notes into a single claim.
- If the wiki cannot fully answer the question, say what is missing.
- If the answer depends on weak or provisional notes, say so.

## Conflict handling

- When notes disagree, identify the disagreement explicitly.
- Point to the canonical page and the conflicting supporting notes.
- If one page is clearly more current or canonical, say that.
- If the conflict is unresolved, report it as unresolved instead of pretending consensus exists.

## Output format

Return:

- Short answer
- Canonical wiki pages used
- Supporting notes or raw sources consulted, if any
- Gaps or conflicts discovered
- Suggested wiki page to create or strengthen, if needed

## Follow-up improvement rule

A good query should improve future queries.

If answering the question exposes a missing, weak, or fragmented concept:

- name the page that should be created or improved
- say whether the missing material belongs in `wiki/`, `raw/`, or a project folder
- prefer improving an existing canonical page over creating a duplicate
