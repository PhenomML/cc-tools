# cc-tools ORIENTATION

Standard Claude Code toolset for PhenomML research projects. This file is regenerated at the end of each session.

**Last updated:** 2026-06-12

## What this repo is

CLI tools and skills installed via `uv tool install --reinstall --force .` into every Claude Code session. Tools become available as `cc-*` commands. Skills become available as `/skill-name` commands. The canonical tool/skill manifest is `claude-md-section.md` — this is what `/wiki-upgrade` propagates to downstream CLAUDE.md files.

## Key files

| File | Purpose |
|---|---|
| `claude-md-section.md` | **Canonical** toolset + skills table; source for `/wiki-upgrade` |
| `~/.claude/CLAUDE.md` | Global context; must mirror `claude-md-section.md` |
| `pyproject.toml` | Entry points for all CLI tools |
| `cc_tools/arxiv_fetch.py` | `cc-arxiv` implementation including `--src` make4ht pipeline |
| `cc_tools/make4ht_configs/` | Upstream patches: `IEEEtran.4ht` (#189), `algpseudocode.cfg` (#190) |
| `DEPLOYING.md` | Checklist — update before any new tool/skill ships |
| `SECURITY.md` | LaTeX execution security (Tier-1 defenses, CVE-2023-32700) |

## Current state of the make4ht pipeline (cc-arxiv --src)

The `--src` path fetches an arXiv TeX tarball and runs:
1. `make4ht` (TeX → HTML) → pandoc (HTML → Markdown) — preferred, high math fidelity
2. Pandoc direct LaTeX → Markdown — fallback when make4ht produces no HTML

**Active upstream engagement with Michal Hoftich (michal-h21):**
- Issue #189: IEEEtran register overflow — patches incorporated (commit 884408c), but all three test papers (0907.3574, 1111.1041, 1610.03082) still fall back to pandoc. Last comment posted 2026-06-12 with corrected test results.
- Issue #190: algpseudocode nested spans — patch incorporated, not yet tested on 2505.00326.
- Protocol: Andrew relays upstream findings; never file make4ht issues without his go-ahead.

**Recent fixes (this session, 2026-06-12):**
- `TEXMFCNF=tmpdir` without trailing colon replaced kpathsea defaults, killing make4ht with Lua "module 'make4ht-logging' not found" before TeX ran. All prior make4ht tests were invalid. Fix: `tmpdir + ":" + existing_cnf` (trailing colon preserves built-in defaults). Commit e7eefcb.
- make4ht failure instrumentation: TeX `.log` tail + stdout now printed to stderr on failure.

**Fallback issue-filing rule (new, this session):**
Operating Claudes must file a `PhenomML/cc-tools` issue on every `pandoc-latex` fallback. Title: `cc-arxiv --src: make4ht fallback on <arxiv-id>`. This rule is in `claude-md-section.md` and `~/.claude/CLAUDE.md`.

**Known failure pattern — missing .xbb files:**
arXiv:2602.02385 fails in the tex4ht DVI→HTML step with "Cannot determine size of graphic" warnings followed by `tex4ht returned exit code 1`. The tarball omits `.xbb` bounding-box files. Separate from the IEEEtran register issue; not yet filed.

## Open issues (selected)

| # | Summary |
|---|---|
| 39 | cc-arxiv --src: figure files in tarball not extracted/embedded |
| 36 | cc-arxiv --src: pandoc silent near-empty output on 2605.22763 (multi-file LaTeX) |
| 31 | cc-arxiv --src: pandoc fails on \setlength in 2311.07361 |
| 27 | cc-arxiv --src: fallback chain HTML → tarball → PDF |
| 23 | cc-arxiv --src: test corpus, regression harness, upstream engagement |
| 21 | cc-webfetch --math: pandoc pipeline for math-heavy HTML pages |
| 19 | /wiki-orient skill |

## Pending work (not yet filed)

- Test algpseudocode.cfg patch on arXiv:2505.00326 (committed to Michal on #190)
- File issue for 2602.02385 tex4ht .xbb failure pattern
- Antigravity CLI migration (deadline 2026-06-18): templates/gemini-workspace.md rename, setup-claude.sh --adversary flag

## Install / test

```bash
uv tool install --reinstall --force .
uv run pytest
```

7 tests pass, 2 skipped (network). Always use `uv run pytest`, not `python -m pytest`.
