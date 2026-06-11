# Deploying a New Tool or Skill

Complete every item on this checklist before closing the session. Each item is a hard requirement — a tool that skips any step is partially deployed and will silently fail to be discovered.

## New CLI Tool

- [ ] `cc_tools/<tool>.py` — implementation with a `main()` entry point
- [ ] `pyproject.toml` — entry point added under `[project.scripts]`
- [ ] Install: `uv tool install --reinstall --force .`
- [ ] Smoke test: run the tool and confirm it works
- [ ] `claude-md-section.md` — add a row to the toolset table
- [ ] `claude-md-section.md` — add an "Always prefer" rule if there is a risk of Claudes bypassing the tool (calling APIs directly, reading raw bytes, etc.)
- [ ] `~/.claude/CLAUDE.md` — mirror both changes above (table row + prefer rule)
- [ ] `README.md` — add tool to the command reference table

**`claude-md-section.md` is the canonical source.** `~/.claude/CLAUDE.md` is a copy — keep them in sync. When `/wiki-upgrade` runs in any wiki, it pulls from `claude-md-section.md`. A tool missing from `claude-md-section.md` will vanish from every wiki's context after the next upgrade, even if `~/.claude/CLAUDE.md` was updated.

## New Skill (`~/.claude/commands/<skill>.md`)

- [ ] Skill file written and tested
- [ ] `claude-md-section.md` — add a row to the Research Skills table
- [ ] `~/.claude/CLAUDE.md` — mirror the skills table row
- [ ] `README.md` — add skill to the skills reference

## After Any Change

- [ ] Commit with a message that names the tool/skill
- [ ] Push — other machines update via `cd $CC_TOOLS && git pull && bash setup-claude.sh`
