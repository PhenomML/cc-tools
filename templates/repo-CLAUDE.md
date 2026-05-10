# <Project Name>

## Role and scientific context

Read this before anything else:

**Experiment manager brief:** `<path/to/syntheses/experiment-manager-brief.md>`

It defines your role, the scientific question, phase falsification targets, theory
source references, promotion boundaries, and log format. Do not duplicate any of
that content here.

## Repo layout

```
<repo>/
  CLAUDE.md           ← this file
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

When launched from `wiki/`, navigate to `../` for all code and infrastructure work.

## Code conventions

- **Language:** <Python / R / Julia / ...>
- **Environment:** `conda activate <env-name>` — always activate before running
- **Entry point:** `<path/to/main.py or notebook>`
- **Results land in:** `<path/>`
