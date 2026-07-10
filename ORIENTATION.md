# cc-tools ORIENTATION

Standard Claude Code toolset for PhenomML research projects. This file is regenerated at the end of each session.

**Last updated:** 2026-07-07

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

**Wiki-access behavioral rule (2026-07-07):** The root problem is not that agents can't access wikis — they have `cc-wiki-grep`. The problem is nothing tells them *when* to use it during a session. Fix: added a two-line rule to `templates/wiki-CLAUDE.md` and the `wiki-upgrade.md` Step 3 placeholder: "During any session turn — before asserting a factual claim about this domain: Run `cc-wiki-grep "TERM" .` first. Cite what you find, or mark `*[Imputed]*`." Step 3b in `/wiki-upgrade` patches this rule into existing wikis that already have a Session Start section. Deployed 2026-07-07: 11 wikis patched via Step 3b directly; beam-imaging-lotfi received full `/wiki-upgrade` (also rescued `## Sources` from inside the managed block where it would be silently clobbered on every upgrade). Transformers wiki already had the rule. Total: 12/12 sentinel-bearing research wikis updated.

**beam-imaging-lotfi /wiki-upgrade lesson (2026-07-07):** Pre-flight (`grep -n "^## " CLAUDE.md`) is essential on old wikis. This one had a project-specific `## Sources` section (Kalman Filter / Kalman 1960 references) inside the managed block. The upgrade script would have deleted it silently. Rescued by moving it above the sentinel before Step 2.

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

**Bug fixed 2026-07-02 (issue #44 — tikz-external grouping overflow):** Root cause: `tikz-hooks.4ht` inlines `\find:externalize` body into `\use@@tikzlibrary` via `\append:defI`. After the external library loads and defines `\tikzexternalize`, the code fires for every subsequent `\usetikzlibrary` call. The second fire does `\let\tikz:externalize\tikzexternalize` again — but `\tikzexternalize` has already been wrapped to call `\tikz:externalize`, so the `\let` creates a circular self-reference → infinite recursion → TeX grouping-levels=255 overflow. Fix: patched `tikz-hooks.4ht` in `make4ht_configs/` adds a one-time `\tikzext:wrap:done` guard around the wrapping block. The pipeline copies it to the tex working directory alongside the stub when tikz-external is detected (tex4ht searches current dir first). Verified on revtex4-1 (2507.07432 first pass: clean DVI) and IEEEtran (minimal test: clean HTML in ~2s); all 9 corpus tests pass.

**Active upstream engagement with Michal Hoftich (michal-h21):**
- Issue #189: IEEEtran register overflow — patches incorporated. All three papers now tested with both pdfLaTeX AND LuaLaTeX (2026-06-24). All converge at register 65630 with LuaLaTeX, confirming overflow is from IEEEtran + tex4ht hooks (not paper content). Results posted; awaiting Michal's response.
- Issue #190: algpseudocode nested spans — patch incorporated, tested on 2505.00326 (2026-06-24), results posted. Keywords render as `<strong>`; line structure clean; math stays as MathJax spans. Config in daily use.
- Protocol: Andrew relays upstream findings; never file make4ht issues without his go-ahead.

**IEEEtran status:** All IEEEtran.cls papers (second most common arXiv class) still fall to pandoc-latex. Two failure modes: register overflow (Bad register code) and memory exhaustion. Upstream issue #189 open; no timeline.

**IEEEtran register overflow root cause (2026-07-02):** The overflow is deterministic — all three test papers hit the same register number (65630) under LuaLaTeX, regardless of paper content. Root cause: IEEEtran.cls allocates many TeX registers natively (two-column layout, citation tracking, section formatting, biography environments). tex4ht's hook system allocates additional registers for every macro it wraps. Combined they exhaust the engine's register pool. The 65630 convergence means the overflow comes from the class + tex4ht infrastructure, not the papers. Fix path: IEEEtran.4ht would need to skip hooking IEEEtran-specific macros that tex4ht doesn't need for HTML output.

**tikz-external rarity (2026-07-02):** Sampled 40 recent arXiv papers (cs.SY + quant-ph) — 0 use tikz-external. Reason: tikz-external saves figures as sidecar PDFs; arXiv submissions must include those files, so most authors disable it before submitting. The GPTs paper (2507.07432) is unusual — tikz-external was embedded in a bundled group .sty (dynlearn.sty) and left active by oversight. No real end-to-end test case found; IEEEtran toy document (synthetic) is the only full-pipeline evidence for the fix.

**2507.07432 second-pass hang:** tex4ht second pass on 2507.07432 does not loop — it makes genuine progress through complex quantum math but is extremely slow (29+ hours observed). Orphaned process (GPTs_micro.tex, pid 79484) was killed 2026-07-02 after running since Thursday. This paper will always hit cc-arxiv's timeout and fall to pandoc-latex fallback — that is the correct behaviour, not a bug.

**Known failure pattern — missing .xbb files:**
arXiv:2602.02385 fails in the tex4ht DVI→HTML step with "Cannot determine size of graphic" warnings. Not yet filed.

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
| 39 | cc-arxiv --src: figure files in tarball not extracted/embedded |
| 36 | cc-arxiv --src: pandoc near-empty output on 2605.22763 (multi-file LaTeX) — may be fixed by #45 cwd fix |
| 31 | cc-arxiv --src: pandoc fails on \setlength in 2311.07361 |
| 27 | cc-arxiv --src: fallback chain HTML → tarball → PDF |
| 21 | cc-webfetch --math: pandoc pipeline for math-heavy HTML pages |
| 19 | /wiki-orient skill |

## NLP conference template failure class (diagnosis pending)

Issues #47 (ACL, 2305.13571) and #48 (COLING, 2501.00073) represent a new failure class: **both make4ht and pandoc-latex fail**, producing no output. These are the first `pdf-only` corpus entries.

**Root cause: unknown.** tex4ht exits 1 on both papers, but we have not captured verbose error output. The failure mode determines scope entirely:
- Missing `.4ht` file → moderate; write conference class hooks (AI coding makes this tractable)
- Register overflow variant → harder; structural upstream fix like IEEEtran
- Specific macro collision → possibly a small patch

**Why LaTeXML is not the answer:** Tested and rejected in issue #20. LaTeXML emits interleaved Unicode+LaTeX on math-heavy papers, producing garbage. make4ht executes actual TeX; that architecture is correct. The tex4ht hook layer is the failure point, not the choice of make4ht.

**Strategic scope:** ACL, COLING, EMNLP, NAACL, EACL all use bundled conference `.sty` files. This failure class covers most NLP papers on arXiv. A fix would benefit the entire tex4ht community and is worth upstream engagement with Michal once diagnosed.

**Diagnosis path (next session):** Run make4ht on cached tarballs with full verbose output:
```bash
cd /tmp && tar xf <cc-tools>/tests/corpus/tarballs/2305.13571.tar.gz
make4ht acl_latex.tex "mathjax" 2>&1 | tee /tmp/acl-make4ht.log
```
The error output will identify which category this falls into.

## Pending work (not yet filed)

- ~~Test algpseudocode.cfg patch on arXiv:2505.00326~~ done 2026-06-24
- File issue for 2602.02385 tex4ht .xbb failure pattern
- Draft upstream report for issue #44 (tikz-hooks.4ht self-ref bug) for Andrew to relay to Michal
- Diagnose ACL/COLING template failure (issues #47, #48) — run make4ht locally, capture error
- Antigravity CLI migration: templates/gemini-workspace.md rename, setup-claude.sh --adversary flag
- cmux KaTeX PR: implement once maintainer responds to issue #6749

## Install / test

```bash
uv tool install --reinstall --force .
uv run pytest
```

9 tests pass, 2 skipped (no-source papers with null arxiv_id). Always use `uv run pytest`, not `python -m pytest`.
