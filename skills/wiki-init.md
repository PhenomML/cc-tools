Initialise the wiki directory structure from the Sub-wikis table in CLAUDE.md: $ARGUMENTS

Run from the wiki root (the directory containing CLAUDE.md). Safe to re-run on an
existing wiki — skips files and directories that already exist without overwriting them.

Sub-wikis are not limited to research domains — they can represent any orthogonal
dimension of a subject. A person wiki might have biography, research, ai-safety, and
ventures. A company wiki might have history, products, strategy, and team. The structure
that emerges from the Sub-wikis table is whatever the researcher defined.

## Step 1 — Read the Sub-wikis table

Read `CLAUDE.md` and extract the directory name from every data row in the Sub-wikis
table (skip the header and separator rows).

## Step 2 — Scaffold each sub-wiki

For each sub-wiki, create the following if they do not already exist:

**Directories:** `<dir>/`, `<dir>/papers/`, `<dir>/concepts/`, `<dir>/methods/`,
`<dir>/projects/`, `<dir>/research/`

**`<dir>/index.md`:**
```markdown
# <dir> Index

<!-- Claude maintains this file. -->

## Papers

## Concepts

## Methods

## Projects
```

**`<dir>/research/index.md`:**
```markdown
# Research Threads

<!-- Claude maintains this file. -->

## Active

## Settled

## Archived
```

**`<dir>/CLAUDE.md`** — do not overwrite if it already exists:
```markdown
# <dir> Sub-wiki

This is the <dir> sub-wiki. Scope, related sub-wikis, page conventions, frontmatter
schema, math notation standard, and workflow skills are defined in the root `CLAUDE.md`.
```

## Step 3 — Scaffold the wiki root

Create the following if they do not already exist:

**`raw/`** directory.

**`.gitignore`** — if absent, create with `raw/`. If present but missing `raw/`, append it.

**`index.md`:**
```markdown
# Research Wiki Index

<!-- Claude maintains this file. -->

## Papers by sub-wiki

## Active projects
```

**`log.md`:**
```markdown
# Research Wiki Log

<!-- Claude appends to this file after every wiki operation. -->
```

## Step 4 — Report

List every directory and file created, grouped by sub-wiki. Note anything skipped
because it already existed.
