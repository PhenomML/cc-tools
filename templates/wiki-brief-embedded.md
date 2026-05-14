# Embedded Mode

Use this procedure when `../CLAUDE.md` or `../.git` is detected — the wiki is a
subdirectory of a code repo, not a standalone research brief.

## Navigation

All code, conda, and git operations run from `../` (the repo root), not from `wiki/`.
Verify your working directory before every shell command — conda and git run silently
from the wrong directory without error.

```bash
pwd        # confirm you are in wiki/
ls ../     # confirm repo root contents before any code work
```

## Minimal scaffold

Create only what the experiment needs. Skip sub-wiki directories, biography/, products/,
and other standalone-brief structure.

Create at the brief root if not already present:
- `syntheses/` — shared blackboard for agent-authored files and handoffs
- `raw/` — for documents fetched during the experiment
- `.gitignore` containing `raw/`
- `log.md` — with a minimal header: `# <Project> Log\n\n<!-- entries appended below -->`
- `CLAUDE.md` — copy from `~/Projects/PhenomML/cc-tools/templates/experiment-wiki-CLAUDE.md`
  and fill in the title, date, and goal from the driving question

Run:
```bash
bash ~/Projects/PhenomML/cc-tools/setup-claude.sh --project .
```

Do not create standalone sub-wiki directories or index.md unless the operational brief
specifically calls for them.

## Orientation synthesis

Write the orientation synthesis to `syntheses/<slug>.md` using standard wiki synthesis
frontmatter before doing any other work. This is the confirmation gate — stop and wait
for the researcher to confirm the orientation is correct before starting any computation,
environment setup, or code work.

## Multi-agent convention

When two Claude instances collaborate through the same `syntheses/` directory, use these
conventions so each agent's contributions are traceable:

**File naming:** `syntheses/<topic>-<agent-slug>.md`
Examples: `syntheses/phase-minus1-results-emma.md`, `syntheses/sign-convention-response-xfmr.md`

**Asking questions:** append a `## Questions for <Agent>` section to any synthesis file.
The named agent responds in a new file: `syntheses/<topic>-response-<agent-slug>.md`.

**Routing:** the researcher relays files between sessions — there is no direct channel
between agents. Keep question sections short and unambiguous.

**Blackboard rule:** `syntheses/` is append-only shared state. Never overwrite another
agent's files; write responses and amendments as new files.
