---
promoted_from: private memory (project_transformers_adversary.md)
promoted: 2026-06-15
status: workspace built; AG pass likely complete
---

# transformers-adversary/ Scaffold

AG adversary workspace built 2026-05-17 for the xfmr (transformers) brief.

**Location:** `~/Research/Topics/transformers-adversary/`

## Key reference

`transformers-adversary/GEMINI.md` is the **canonical reference implementation** for future adversary workspace builds. It derives the five rules and Design Consultation Mode from the bootstrap templates. When building a new adversary workspace, use this as the model — not `compressed-sensing-adversary/`.

`bootstrap/adversary-workspace-setup.md` points here.

## Structure

- `cold-reads/`, `critiques/` — AG working directories
- `.claude/settings.local.json` — permissions + `agent_role: adversary` + `brief_root: ../transformers`
- Shared coordination: `~/Research/Topics/transformers/syntheses/`
