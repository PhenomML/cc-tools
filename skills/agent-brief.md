Instantiate a specialised agent from an operational brief: $ARGUMENTS

`$ARGUMENTS` is the path to an operational brief — a document that defines the agent's
role, scientific question, phase targets, boundaries, and log format. Written by a
theory Claude or researcher as a handoff document. Examples:

- `~/Research/Topics/transformers/syntheses/isatx-experiment-manager-brief.md`
- `~/Research/Topics/compressed-sensing/syntheses/steinsense-implementation-brief.md`

Run from inside `wiki/`. The code repo or work directory is at `../`.

## Navigation

All code, conda, git, and infrastructure operations run from `../`. Verify location
before every shell command.

```bash
pwd        # confirm you are in wiki/
ls ../     # confirm work directory contents
```

## Step 1 — Read the brief

Read the full operational brief at the path given in `$ARGUMENTS`. Do not skim —
the brief is the ground truth for your role, constraints, phase logic, and log format.

If `../CLAUDE.md` exists, read it too — it describes the repo layout and code conventions.

## Step 2 — Minimal scaffold

Create at the wiki root if not already present:
- `syntheses/` — shared blackboard for orientation, results, and agent handoffs
- `raw/` — for any documents fetched during work
- `.gitignore` containing `raw/`
- `log.md` — with a minimal header: `# <Project> Log\n\n<!-- entries appended below -->`
- `CLAUDE.md` — copy from `~/Projects/PhenomML/cc-tools/templates/experiment-wiki-CLAUDE.md`
  and fill in the title, date, and goal from the operational brief

Run:
```bash
bash ~/Projects/PhenomML/cc-tools/setup-claude.sh --project .
```

## Step 3 — Write orientation synthesis

Write `syntheses/agent-orientation.md` using standard wiki synthesis frontmatter.

Cover:
- **Role** — what you are responsible for, and explicitly what you are not
- **Current phase or goal** — what you are starting with this session
- **Pass/fail criterion** — what constitutes success or failure for the current phase
- **Key constraints** — what requires researcher approval before acting (plan edits,
  wiki promotion, compute commits, submitting PRs, etc.)
- **Theory sources** — where settled knowledge lives; where to file gaps as queue entries

This synthesis is the confirmation gate. Do not begin any work — no code, no environment
setup, no computation — until the researcher confirms the orientation is correct.

## Step 4 — Operate per the brief

After confirmation, follow the operational brief for all work. Append structured log
entries after each experiment, decision point, or result, using the log format specified
in the brief.

**Multi-agent convention** — when collaborating with another Claude instance through
`syntheses/`:
- Agent-authored files: `syntheses/<topic>-<agent-slug>.md`
- Questions for another agent: `## Questions for <Agent>` section at the end of a file
- Responses: new file `syntheses/<topic>-response-<agent-slug>.md`
- Never overwrite another agent's files — `syntheses/` is append-only shared state
