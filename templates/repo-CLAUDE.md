# <Project Name>

## Purpose

<One paragraph: what this experiment tests and why it matters. State the core idea
in plain language — this is what future Claude instances read first when they open
this repo.>

## Repo layout

```
<repo>/
  CLAUDE.md           ← this file (repo-level orientation)
  wiki/               ← experiment brief and documentation (launch Claude here)
    CLAUDE.md         ← wiki/brief scope and page conventions
    index.md          ← brief index and running notes
    raw/              ← source documents (local only, never committed)
    queue.md          ← paywalled or pending sources
  <src>/              ← experiment code
  <data>/             ← datasets (local only — add to .gitignore)
  <notebooks>/        ← analysis notebooks
  README.md           ← public-facing summary
```

## Claude's scope

You have authority over both the wiki (`wiki/`) and the experiment code in this
repo. Wiki operations default to `wiki/`; code and infrastructure operations use
paths relative to this repo root.

When launched from `wiki/`, navigate to `../` for all code work.

## Theory sources

This experiment is grounded in:

- **<Brief 1 name>**: `<path/to/brief/index.md>` — <one sentence on what this brief contributes>
- **<Brief 2 name>**: `<path/to/brief/index.md>` — <one sentence on what this brief contributes>

Read these briefs when you need theoretical grounding. Do not re-derive what is
already settled there; file gaps as queue entries in `wiki/queue.md`.

## Hypothesis

<State the falsifiable claim this experiment tests.>

**Positive result looks like:** <what outcome confirms the hypothesis>
**Negative result looks like:** <what outcome disconfirms it, and what that implies>

## Success criteria

<Quantitative or qualitative criteria for calling this experiment complete enough
to promote findings to the wiki. Be specific — ambiguous criteria lead to scope creep.>

## Current phase

<!-- Update this as the experiment progresses -->
`<Planning | Implementation | Pilot | Full run | Analysis | Write-up>`

## Code conventions

- **Language:** <Python / R / Julia / ...>
- **Environment:** `conda activate <env-name>` — always activate before running
- **Entry point:** `<path/to/main.py or notebook>`
- **Results land in:** `<path/>`
- **Key dependencies:** <list or point to requirements file>

## Decision log

Record key design choices here as they are made. Rationale is more valuable than
the decision itself — future Claude instances need to know *why*.

```
- YYYY-MM-DD: <decision> — <rationale>
```
