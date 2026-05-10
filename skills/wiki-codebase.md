Analyze a codebase and work on issues: $ARGUMENTS

`$ARGUMENTS` is an optional GitHub issue number, feature request, or goal. If omitted,
the skill builds the wiki only and stops at the end of Step 4.

Run from inside `wiki/`. The code repo is at `../`.

## Navigation

The wiki sits inside the code repo. All code reads, edits, git operations, and test
runs use `../` paths. Verify location before every shell command.

```bash
pwd        # confirm you are in wiki/
ls ../     # confirm repo root contents before any code work
```

## Step 1 — Survey the repo

Save a filtered directory tree to `raw/`:

```bash
find .. -not -path '*/.git/*' \
        -not -path '*/node_modules/*' \
        -not -path '*/vendor/*' \
        -not -path '*/.venv/*' \
        -not -path '*/target/*' \
        -not -path '*/__pycache__/*' \
        -not -path '*/build/*' \
        -not -path '*/dist/*' \
    > raw/directory-tree-<YYYY-MM-DD>.md
```

Detect the tech stack by reading key files if present:

| File | Indicates |
|---|---|
| `Gemfile` | Ruby / Rails |
| `package.json` | Node.js / React / TypeScript |
| `go.mod` | Go |
| `pyproject.toml` / `requirements.txt` | Python |
| `Cargo.toml` | Rust |
| `pom.xml` / `build.gradle` | Java / Kotlin |
| `mix.exs` | Elixir |

Read one or two entry-point files (e.g. `config/routes.rb`, `main.go`, `src/index.ts`)
to confirm the architecture before proposing sub-wikis.

## Step 2 — Determine sub-wiki structure

Propose sub-wikis that map to the code's natural domain boundaries. Starting points:

| Stack | Default sub-wikis |
|---|---|
| Rails | `architecture/`, `backend/`, `frontend/`, `api/`, `infrastructure/` |
| Python service | `architecture/`, `core/`, `api/`, `data/`, `workers/` |
| Go service | `architecture/`, `core/`, `api/`, `storage/` |
| Node / React | `architecture/`, `frontend/`, `backend/`, `api/` |
| Generic | `architecture/`, `core/`, `api/`, `data/` |

Add sub-wikis freely when the codebase warrants it (e.g. `federation/` for ActivityPub,
`ml/` for model serving). Drop defaults that have no corresponding code.

If the stack and structure are unambiguous, proceed without stopping to confirm.
Otherwise confirm with the researcher before scaffolding.

## Step 3 — Scaffold wiki

Write `CLAUDE.md` with three sections:

**Purpose:**
```markdown
# <Repo Name> Codebase Wiki

## Purpose

**Subject:** <Repo name> (codebase)
**Created:** <YYYY-MM-DD>
**Goal:** <driving goal or issue from $ARGUMENTS, or "initial codebase orientation">
```

**Sub-wikis table** (one row per sub-wiki, scope and related fields).

**Managed section:** insert current `~/Projects/PhenomML/cc-tools/templates/wiki-schema.md`
wrapped in sentinels:
```
<!-- cc-tools:wiki:begin -->
[wiki-schema.md content]
<!-- cc-tools:wiki:end -->
```

Create for each sub-wiki: the directory and `<dir>/index.md`.

Create at the wiki root if not present: `.gitignore` containing `raw/`, `log.md`.

Run:
```bash
bash ~/Projects/PhenomML/cc-tools/setup-claude.sh --project .
```

## Step 4 — Build initial concept pages

Write `architecture/concepts/system-overview.md` first — it is the anchor all other
pages cross-link to. Cover: component map, technology choices, request lifecycle,
and background job or real-time lifecycle if present.

For each remaining sub-wiki, identify the key structural files, save code snapshots
to `raw/` with date-stamped slugs, then write one concept page:

```bash
cat ../app/lib/feed_manager.rb > raw/feed-manager-<YYYY-MM-DD>.md
```

Concept page coverage by sub-wiki type:
- `backend/`: core models, services, workers, key data flows
- `frontend/`: SPA structure, state management, build system
- `api/`: endpoint groups, WebSocket streams, authentication
- `infrastructure/`: database schema, job queues, deployment topology
- `federation/`: protocol flow, inbox/outbox, delivery workers

Update each sub-wiki's `index.md` and append to `log.md`.

**If no issue or goal was provided in `$ARGUMENTS`, stop here and report.** The wiki
is the deliverable; offer to work an issue when the researcher is ready.

## Step 5 — Work on an issue

Fetch the issue:

```bash
gh issue view <number>
```

Read the full issue: description, reproduction steps, expected vs. actual behavior,
any linked code or prior comments.

Cross-reference with wiki concept pages to identify the likely code location. Read
the relevant files via `../` paths. Implement the fix.

Run existing tests if available:

```bash
cd .. && <test command>    # e.g. bundle exec rspec, go test ./..., pytest
```

## Step 6 — Update wiki

After a fix, update any concept pages whose description is now stale. Append to
`log.md`:

```
## [YYYY-MM-DD] issue #<N> | <one-line summary>
Fix: <what changed>. Concept pages updated: <list or none>.
```

## Step 7 — Report

List every wiki file created or modified. If an issue was worked: issue number, bug
summary, files changed in the codebase, test status. Flag any sub-wikis that warrant
deeper concept pages before the next session.
