# cc-tools ORIENTATION

Standard Claude Code toolset for PhenomML research projects. This file is regenerated at the end of each session.

**Last updated:** 2026-06-24

## What this repo is

CLI tools and skills installed via `uv tool install --reinstall --force .` into every Claude Code session. Tools become available as `cc-*` commands. Skills become available as `/skill-name` commands. The canonical tool/skill manifest is `claude-md-section.md` — this is what `/wiki-upgrade` propagates to downstream research wikis.

**Current version:** 0.2.0 (bumped 2026-06-15 — wiki/memories/ public layer + cc-wiki-grep)

## Key files

| File | Purpose |
|---|---|
| `claude-md-section.md` | **Canonical** toolset + skills table; source for `/wiki-upgrade` |
| `~/.claude/CLAUDE.md` | Global context; must mirror `claude-md-section.md` |
| `pyproject.toml` | Entry points for all CLI tools |
| `cc_tools/arxiv_fetch.py` | `cc-arxiv` implementation including `--src` make4ht pipeline |
| `cc_tools/wiki_grep.py` | `cc-wiki-grep` — token-efficient wiki search |
| `cc_tools/make4ht_configs/` | Upstream patches: `IEEEtran.4ht` (#189), `algpseudocode.cfg` (#190) |
| `templates/wiki-CLAUDE.md` | Template for new wiki CLAUDE.md files |
| `skills/wiki-upgrade.md` | `/wiki-upgrade` skill — includes Step 4 INDEX.md bootstrap |
| `DEPLOYING.md` | Checklist — update before any new tool/skill ships |
| `SECURITY.md` | LaTeX execution security (Tier-1 defenses, CVE-2023-32700) |

## Shell environment: cmux (assessed 2026-06-24)

The research group is running sessions inside **cmux** ([manaflow-ai/cmux](https://github.com/manaflow-ai/cmux)), a Ghostty-based macOS terminal with vertical tabs, multi-pane workspaces, and a built-in WKWebView browser pane. cmux is the candidate shell for the group's workflow.

**Key capabilities for the researcher pipeline:**

| Capability | Command | Use |
|---|---|---|
| Browser pane | `cmux browser open <url>` | SPA/JS-rendered pages; authenticated publisher sessions |
| Markdown viewer | `cmux markdown open <file>` | Live-reloading rendered view (no math yet — see issue below) |
| Notifications | `cmux notify --title ... --body ...` | Agent completion signals without screen-watching |
| Status bar | `cmux set-status <key> <value>` | Per-agent progress visibility |
| Screen read | `cmux read-screen --surface <id>` | Non-intrusive agent state verification |
| Multi-agent layout | `cmux tree` | Vera+Emma colocated in workspace:1; Tool+Fran in workspace:3 |

**Researcher pipeline synergies identified:**
- Vera and Emma colocated in the same workspace can share a browser surface for paper co-reading (one fetch, two readers)
- `cmux notify` at commission completion replaces screen-watching; human relay still intact
- `cmux set-status` gives Andrew progress visibility without interrupting agent sessions
- `cmux markdown open <synthesis-file>` with live reload lets Andrew watch synthesis documents update in real time

**cmux markdown viewer internals (read source 2026-06-24):**
- WKWebView + `marked.js` (not native renderer)
- Lazy-load pattern for heavy libs: Mermaid, Vega/Vega-Lite — loaded via `evaluateJavaScript` on first use
- Math NOT currently supported; sanitizer in `shell.html` strips `<math>` MathML elements
- KaTeX with `output: 'html'` avoids the sanitizer (emits `<span>` trees only)
- Font resolution blocker: `loadHTMLString(_:baseURL:)` uses user's file as base URL, so bundle-relative `fonts/KaTeX_*.woff2` paths don't resolve

**Upstream issue filed:** [manaflow-ai/cmux #6749](https://github.com/manaflow-ai/cmux/issues/6749) — KaTeX math rendering proposal. Awaiting maintainer response on font approach (data-URI CSS vs. URL scheme handler) before writing the implementation.

## Wiki navigation pattern (new in v0.2.0)

`cc-wiki-grep` + `INDEX.md` — token-efficient two-step wiki access. Load INDEX.md (small greppable tag index), then extract only the section needed. Deployed to Vera (geometry-of-truth) and Cass (compressed-sensing). Field assessment by Cass: useful for orientation and long-tail discovery, not transformative for high-frequency pages already in memory. Pattern documented in `wiki/patterns/index-md-navigation.md`.

`cc-wiki-grep` also works well on `log.md` files: section mode (`--section "2026-06-18"`) for a specific date entry; search mode (`cc-wiki-grep "COMM-020"`) for commission history across the full log.

`/wiki-upgrade` now includes Step 4 (bootstrap INDEX.md if missing) and Step 3 placeholder includes INDEX.md step 2. Pre-flight rule: `grep -n "^## " CLAUDE.md` before upgrading mature wikis — project-specific sections inside the managed block are silently clobbered.

## Agent session management (established 2026-06-18)

**Sessions are disposable, files are not.** ORIENTATION.md, log.md, and commission documents are the continuity layer — not the conversation context.

- **Each agent owns their own ORIENTATION.md** in their own workspace. Single-author → regenerate freely on close. Multi-agent workspaces need append (log.md style) or per-agent files.
- **Post-compaction process:** re-read ORIENTATION.md + last log entry, confirm current task against open items, narrate current state in one sentence before continuing.
- **Restart signal:** agent asks about something already resolved, or makes assumptions inconsistent with ORIENTATION.md.
- **Session length:** one session per deliverable/commission phase; clean close every time. Restart cost is low when externalization is good.

## Current state of the make4ht pipeline (cc-arxiv --src)

The `--src` path fetches an arXiv TeX tarball and runs:
1. `make4ht` (TeX → HTML) → pandoc (HTML → Markdown) — preferred, high math fidelity
2. Pandoc direct LaTeX → Markdown — fallback when make4ht produces no HTML

**Bug fixed 2026-06-16 (closes #42):** `-no-shell-escape` was passed as make4ht positional arg[2], which make4ht routes directly to the `tex4ht` binary — not to LaTeX. tex4ht exits 1 with "improper command line". Fixed by removing it: shell-escape is off by default; `openout_any=p` handles write security.

**Active upstream engagement with Michal Hoftich (michal-h21):**
- Issue #189: IEEEtran register overflow — patches incorporated. All three papers now tested with both pdfLaTeX AND LuaLaTeX (2026-06-24). All converge at register 65630 with LuaLaTeX, confirming overflow is from IEEEtran + tex4ht hooks (not paper content). Results posted; awaiting Michal's response.
- Issue #190: algpseudocode nested spans — patch incorporated, tested on 2505.00326 (2026-06-24), results posted. Keywords render as `<strong>`; line structure clean; math stays as MathJax spans. Config in daily use.
- Protocol: Andrew relays upstream findings; never file make4ht issues without his go-ahead.

**IEEEtran status:** All IEEEtran.cls papers (second most common arXiv class) still fall to pandoc-latex. Two failure modes: register overflow (Bad register code) and memory exhaustion. Upstream issue #189 open; no timeline.

**Known failure pattern — missing .xbb files:**
arXiv:2602.02385 fails in the tex4ht DVI→HTML step with "Cannot determine size of graphic" warnings. Not yet filed.

## Test corpus

8 papers, all passing. Run: `uv run pytest` (offline, ~1s from cache) or `uv run pytest --regenerate` (re-runs make4ht on all tarballs, ~73s).

| arXiv ID | Pipeline | Notes |
|---|---|---|
| 2505.00326 (SteinSense) | make4ht | |
| math/0409186 (Candès et al.) | make4ht | |
| 0906.2530 (Donoho & Tanner) | make4ht | |
| 0907.3574 (AMP) | pandoc-latex | IEEEtran register overflow |
| 1111.1041 (AMP minimax) | pandoc-latex | IEEEtran memory exhaustion |
| 1610.03082 (VAMP) | pandoc-latex | IEEEtran memory exhaustion |
| 2512.24601 (RLM, Zhang et al.) | make4ht | Added 2026-06-16; exposed #42 bug |
| 2211.00593 (IOI circuit, Wang et al.) | pandoc-latex | ICLR class / multi-file; fixed pandoc cwd bug (#45) |

## Open issues (selected)

| # | Summary |
|---|---|
| 39 | cc-arxiv --src: figure files in tarball not extracted/embedded |
| 36 | cc-arxiv --src: pandoc near-empty output on 2605.22763 (multi-file LaTeX) — may be fixed by #45 cwd fix |
| 31 | cc-arxiv --src: pandoc fails on \setlength in 2311.07361 |
| 27 | cc-arxiv --src: fallback chain HTML → tarball → PDF |
| 21 | cc-webfetch --math: pandoc pipeline for math-heavy HTML pages |
| 19 | /wiki-orient skill |

## Pending work (not yet filed)

- ~~Test algpseudocode.cfg patch on arXiv:2505.00326~~ done 2026-06-24
- File issue for 2602.02385 tex4ht .xbb failure pattern
- Antigravity CLI migration: templates/gemini-workspace.md rename, setup-claude.sh --adversary flag
- cmux KaTeX PR: implement once maintainer responds to issue #6749

## Install / test

```bash
uv tool install --reinstall --force .
uv run pytest
```

9 tests pass, 2 skipped (no-source papers with null arxiv_id). Always use `uv run pytest`, not `python -m pytest`.
