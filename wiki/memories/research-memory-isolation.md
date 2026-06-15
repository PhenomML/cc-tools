---
promoted_from: private memory (project_research_memory_isolation.md)
promoted: 2026-06-15
status: resolved
---

# Research Directory Memory and Settings Isolation — Resolved

## Problem (discovered 2026-04-27)

Claude's memory namespace is determined by the working directory at launch. Brief Claudes launched from `~/Research/People/` or `~/Research/Companies/` shared a single namespace, causing cross-brief memory and settings pollution — prior subjects' analytical frames and accumulated permissions contaminated future briefs.

## Fix applied

- Per-subject directories with their own `.claude/settings.local.json`
- Parent `.claude/settings.local.json` holds only permissions shared across all briefs in that category
- Subject-specific URLs and permissions moved to the subject directory

## Mechanism

`cc-wiki-brief` (cc_tools/wiki_brief_start.py) creates the brief directory and launches Claude from it via `subprocess.run(["claude", prompt], cwd=brief_dir)`. The relaunch problem is handled pragmatically — no manual step required.

## Pattern

Each brief subject gets its own directory. `cc-wiki-brief` is the correct tool for creating and launching into it. Do not launch briefs from the parent `People/`, `Companies/`, or `Topics/` directory.
