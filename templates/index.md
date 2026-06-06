# templates index

For shared folder-index rules, follow `templates/index-common.md`.

This folder stores reusable note templates.
Templates define structure, not final content.

## What belongs here

- system design note templates
- comparison note templates
- case study templates
- deep dive templates
- maintenance and audit templates

## Local rules

- Keep templates generic and reusable.
- Do not store one-off notes here.
- Reuse an existing template before inventing a new structure.
- Add or revise templates only when repeated use justifies it.

## Key templates

- `index-common.md` — shared guidance for folder-level index files
- `template-maintenance.md` — structure for lint and repair reports
- `template-system-concept.md` — template for concept notes such as load balancers, rate limiting, replication, and other foundational ideas
- `template-system-pattern.md` — template for reusable system building blocks such as consistent hashing, fan-out, circuit breakers, and queue-based patterns
- `template-system-caching.md` — template for caching-focused patterns such as cache-aside, write-through, and write-back
- `template-system-case-study.md` — template for full end-to-end system design lessons and case studies
