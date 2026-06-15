---
promoted_from: private memory (project_version_policy.md)
promoted: 2026-06-14
status: active policy
---

# cc-tools Version Policy

## Bump triggers

- `0.x.0` minor — new tool or skill added (user-visible environment change)
- `0.x.y` patch — bug fix to existing tool, no new entrypoints
- `1.0.0` — tool set stable enough for downstream pinning (e.g., cc-code-tools)

**Heuristic:** if running `setup-claude.sh` produces a different installed environment (new entrypoint, new skill, changed CLAUDE.md section), it's a minor bump. Pure doc fixes or internal refactors are not.

## Version history

| Version | Date | What shipped |
|---|---|---|
| 0.1.0 | initial | baseline toolset |
| 0.2.0 | 2026-06-14 | cc-safari-fetch, cc-semantic-scholar, LaTeX security (SECURITY.md, pre-scan, openout_any=p), cc-arxiv --src (make4ht+mathjax), wiki-as-active-memory (/memory-audit, wiki/memories/) |

## Secondary value

Agents can query `uv tool list` to check installed version — useful for orientation ("does this agent have cc-semantic-scholar?").
