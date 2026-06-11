# cc-tools

Standard Claude Code toolset for PhenomML research projects.

## Before shipping any change

Read `DEPLOYING.md` — it lists every file that must be updated when adding a tool or skill. A tool not in `claude-md-section.md` will not be discovered by any Claude, regardless of what else was updated.

## Key files

| File | Purpose |
|---|---|
| `claude-md-section.md` | **Canonical** toolset + skills table; source for `/wiki-upgrade` |
| `~/.claude/CLAUDE.md` | Global context; must mirror `claude-md-section.md` |
| `pyproject.toml` | Entry points for all CLI tools |
| `templates/` | Wiki scaffolding templates |
| `DEPLOYING.md` | Deployment checklist |
| `SECURITY.md` | LaTeX execution security |

## Install

```bash
uv tool install --reinstall --force .
```

Always use `--reinstall --force` to keep entry points current.

## Tests

```bash
uv run pytest
```
