Initialise the wiki directory structure from the Sub-wikis table in CLAUDE.md: $ARGUMENTS

Run from the wiki root (the directory containing CLAUDE.md). Safe to re-run on an
existing wiki — skips files and directories that already exist without overwriting them.

## Step 1 — Read the Sub-wikis table

Read `CLAUDE.md` and extract every data row from the Sub-wikis table (skip the header
and separator rows). For each row record:
- Directory name (e.g. `tsa/`)
- Full scope string
- Related sub-wikis (may be empty)

## Step 2 — Scaffold each sub-wiki

For each sub-wiki, create the following if they do not already exist:

**Directories:** `<dir>/`, `<dir>/papers/`, `<dir>/concepts/`, `<dir>/methods/`,
`<dir>/projects/`

**`<dir>/index.md`:**
```markdown
# <dir> Index

<!-- Claude maintains this file. -->

## Papers

## Concepts

## Methods

## Projects
```

**`<dir>/CLAUDE.md`** — do not overwrite if it already exists:
```markdown
# <dir> Sub-wiki

**Scope:** <scope string from table>
**Related:** <related sub-wikis, or "none">

See the root `CLAUDE.md` for page conventions, frontmatter schema, math notation
standard, and workflow skills.
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
