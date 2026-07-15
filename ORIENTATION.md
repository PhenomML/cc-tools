# cc-tools ORIENTATION

Standard Claude Code toolset for PhenomML research projects. This file is regenerated at the end of each session.

**Last updated:** 2026-07-14

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
| `cc_tools/make4ht_configs/` | Upstream patches: `IEEEtran.4ht` (#189), `algpseudocode.cfg` (#190), `tikz-hooks.4ht` (#44) |
| `templates/wiki-CLAUDE.md` | Template for new wiki CLAUDE.md files |
| `skills/wiki-upgrade.md` | `/wiki-upgrade` skill — includes Step 4 INDEX.md bootstrap |
| `DEPLOYING.md` | Checklist — update before any new tool/skill ships |
| `SECURITY.md` | LaTeX execution security (Tier-1 defenses, CVE-2023-32700) |
| `AUTHORING.md` | Math and document rendering standard (MathJax, Mermaid, line wrapping) |
| `SIGNAL.md` | AI-for-Science communication standard — three pillars: Markdown+MathJax, wiki, Shannon/McCloskey |

## SIGNAL.md — communication standard (2026-07-07)

Three-pillar discipline for all AI-generated scientific content. Peer to `AUTHORING.md` and `SECURITY.md`.

1. **Markdown + MathJax** — structured documents; all math in `$...$`/`$$...$$` LaTeX; specification-grade reproducibility. Full rendering spec in `AUTHORING.md`.
2. **Wiki** — knowledge in owned files, not context windows; `*[Imputed]*` for ungrounded claims; `cc-wiki-grep` before asserting.
3. **Shannon + McCloskey** — maximum information per word; zero redundancy; claims stated as claims. Named after Claude Shannon (information density) + Deirdre McCloskey (*Economical Writing, Third Edition*).

**Implementation pending:**
- Add prose standard section to `AUTHORING.md`
- Update `templates/wiki-CLAUDE.md` Page conventions + `wiki-schema.md` (propagated by `/wiki-upgrade`)
- Create `/shannon` skill
- Add Shannon/McCloskey voice to `~/.claude/CLAUDE.md` as Tool's default voice

## tex4md — peer project (created 2026-07-14)

LuaLaTeX-to-Markdown converter. Separate repo (`PhenomML/tex4md`); tracked as cc-tools issue #52.

**Why:** tex4ht's HTML target requires structural completeness → register overflow (IEEEtran, issue #189) and conference template failures (#47, #48). Markdown target requires far fewer hooks; unknown macros degrade silently rather than cascading.

**Architecture:** `src/tex4md.sty` + `src/tex4md.lua`; LuaLaTeX execution; math verbatim passthrough via Strategy A (`$` as active character); no new register allocations; math preserved as `$...$`/`$$...$$` in output.

**Phase 1 goal:** skeleton (sections, lists, text formatting, math placeholder `<!-- MATH -->`). Deliverables: `src/tex4md.sty`, `src/tex4md.lua`, `examples/minimal.tex` compiles and produces correct `.md`. Developer Claude to be spun up in `~/Projects/PhenomML/tex4md/`.

**Do not implement Phase 2 (math verbatim capture) in Phase 1.** That requires prototyping the `$`-as-active-character trick separately first.

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

**cmux KaTeX PR (implementation deferred 2026-07-14):** Shell.html architecture fully read (1776 lines). KaTeX with `output: 'html'` avoids the sanitizer (emits `<span>` trees only). No fork needed — work directly in cloned repo at `~/Projects/manaflow-ai/cmux`. Blocked on maintainer response to issue #6749 (font approach: data-URI CSS vs. URL scheme handler).

**Upstream issue filed:** [manaflow-ai/cmux #6749](https://github.com/manaflow-ai/cmux/issues/6749) — KaTeX math rendering proposal.

## Wiki navigation pattern (new in v0.2.0)

`cc-wiki-grep` + `INDEX.md` — token-efficient two-step wiki access. Load INDEX.md (small greppable tag index), then extract only the section needed. Deployed to all 12 sentinel-bearing research wikis (2026-07-07).

`/wiki-upgrade` now includes Step 3b (inject wiki-access behavioral rule) and Step 4 (bootstrap INDEX.md if missing). Pre-flight rule: `grep -n "^## " CLAUDE.md` before upgrading mature wikis — project-specific sections inside the managed block are silently clobbered.

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

**Bug fixed 2026-07-02 (issue #44 — tikz-external grouping overflow):** Root cause: `tikz-hooks.4ht` inlines `\find:externalize` body into `\use@@tikzlibrary` via `\append:defI`. After the external library loads and defines `\tikzexternalize`, the code fires for every subsequent `\usetikzlibrary` call. The second fire does `\let\tikz:externalize\tikzexternalize` again — but `\tikzexternalize` has already been wrapped to call `\tikz:externalize`, so the `\let` creates a circular self-reference → infinite recursion → TeX grouping-levels=255 overflow. Fix: patched `tikz-hooks.4ht` in `make4ht_configs/` adds a one-time `\tikzext:wrap:done` guard around the wrapping block.

**Active upstream engagement with Michal Hoftich (michal-h21):**
- Issue #189: IEEEtran register overflow — patches incorporated. All three papers now tested with both pdfLaTeX AND LuaLaTeX (2026-06-24). All converge at register 65630 with LuaLaTeX, confirming overflow is from IEEEtran + tex4ht hooks (not paper content). Results posted; awaiting Michal's response.
- Issue #190: algpseudocode nested spans — patch incorporated, tested on 2505.00326 (2026-06-24), results posted.
- Protocol: Andrew relays upstream findings; never file make4ht issues without his go-ahead.

**IEEEtran status:** All IEEEtran.cls papers (second most common arXiv class) still fall to pandoc-latex. Two failure modes: register overflow (Bad register code) and memory exhaustion. Upstream issue #189 open; no timeline. tex4md is the long-term fix path.

**IEEEtran register overflow root cause (2026-07-02):** Deterministic — all three test papers hit register 65630 under LuaLaTeX regardless of content. Class + tex4ht infrastructure exhausts the register pool, not paper content. Fix path: IEEEtran.4ht would need to skip hooking IEEEtran-specific macros that tex4ht doesn't need for HTML output.

**Known failure pattern — missing .xbb files:**
arXiv:2602.02385 fails in the tex4ht DVI→HTML step with "Cannot determine size of graphic" warnings. Not yet filed.

## Conference paper preprocessing workaround (discovered 2026-07-14)

ICML/NeurIPS/similar papers with bundled `.sty` files fail make4ht via `\AltlDisplayDollars` + xcolor package interaction. Pandoc-latex also fails when xcolor commands appear in captions (`\colorbox{lime!10}` — the `!` in xcolor color specs confuses the pandoc LaTeX parser).

**Workaround for one-off papers:** strip xcolor commands, wrap abstract content in `\begin{abstract}...\end{abstract}`, concat section files directly with preamble stubs, then pandoc. Tested on arXiv:2603.05498 (Sun et al. 2026, ICML class) → 1000-line math-legible Markdown. Key strip operations: `\rowcolor`, `\columncolor`, `\cellcolor`, `\colorbox{COLOR}{CONTENT}` (replace with content), `\setlength{}{}`in captions.

**Structural traps in tarball concat:**
- Abstract: `sections/0_abstract.tex` contains bare text; `\begin{abstract}` wrapper is in `main.tex`. Must wrap explicitly.
- Appendices: enumerate all files in `appendices/` — don't assume `mathematical_proof.tex` is the only one.
- Title: always read `\title{}` from `main.tex` — do not construct from section filenames.

**arXiv:2603.05498 (Sun, Canziani, LeCun, Zhu 2026):** Preprocessed canonical copy at scratchpad path (ephemeral — pending Vera ingestion). 1000 lines: abstract + §1–6 + conclusion + Appendix A (experimental settings) + Appendix B (mathematical proofs) + Appendix C (per-model-family results). Macro preamble block at top (`\U`, `\S`, `\k`, `\q` etc.). Issue #57 tracks the make4ht failure.

## NLP conference template failure class (diagnosis pending)

Issues #47 (ACL, 2305.13571) and #48 (COLING, 2501.00073) represent a new failure class: **both make4ht and pandoc-latex fail**, producing no output. These are the first `pdf-only` corpus entries.

**Root cause: unknown.** tex4ht exits 1 on both papers, but verbose error output has not been captured. tex4md is the strategic fix path; manual diagnosis is worth one session if the failure is a missing `.4ht` file.

**Diagnosis path (next session):** Run make4ht on cached tarballs with full verbose output:
```bash
cd /tmp && tar xf <cc-tools>/tests/corpus/tarballs/2305.13571.tar.gz
make4ht acl_latex.tex "mathjax" 2>&1 | tee /tmp/acl-make4ht.log
```

## Test corpus

10 papers, 11 passing, 2 skipped. Run: `uv run pytest` (offline, ~1s from cache) or `uv run pytest --regenerate` (re-runs make4ht on all tarballs, ~73s).

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
| 2305.13571 (Chi et al.) | pdf-only | ACL template; tex4ht fails; pandoc times out; issue #47 |
| 2501.00073 (Zuo et al.) | pdf-only | COLING class; tex4ht fails; pandoc parse error; issue #48 |

## Open issues (selected)

| # | Summary |
|---|---|
| 57 | cc-arxiv --src: make4ht failure on 2603.05498 (ICML class, xcolor/colortbl interaction) |
| 52 | cc-arxiv --src: tex4md engine integration |
| 39 | cc-arxiv --src: figure files in tarball not extracted/embedded |
| 36 | cc-arxiv --src: pandoc near-empty output on 2605.22763 (multi-file LaTeX) — may be fixed by #45 |
| 31 | cc-arxiv --src: pandoc fails on \setlength in 2311.07361 |
| 27 | cc-arxiv --src: fallback chain HTML → tarball → PDF |
| 21 | cc-webfetch --math: pandoc pipeline for math-heavy HTML pages |
| 19 | /wiki-orient skill |

## Pending work

- Spin up tex4md developer Claude in `~/Projects/PhenomML/tex4md/` (Phase 1 scope in CLAUDE.md)
- cmux KaTeX PR: implement once maintainer responds to issue #6749
- File issue for 2602.02385 tex4ht .xbb failure pattern
- Draft upstream report for issue #44 (tikz-hooks.4ht self-ref bug) for Andrew to relay to Michal
- Diagnose ACL/COLING template failure (issues #47, #48) — run make4ht locally, capture error
- Antigravity CLI migration: templates/gemini-workspace.md rename, setup-claude.sh --adversary flag

## Install / test

```bash
uv tool install --reinstall --force .
uv run pytest
```

9 tests pass, 2 skipped (no-source papers with null arxiv_id). Always use `uv run pytest`, not `python -m pytest`.
