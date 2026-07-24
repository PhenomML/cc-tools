# cc-tools ORIENTATION

Standard Claude Code toolset for PhenomML research projects. This file is regenerated at the end of each session.

**Last updated:** 2026-07-24

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
| `scripts/preprocess_corpus.py` | Conference paper LaTeX preprocessor — strips xcolor/colortbl, section-concat strategy |
| `templates/wiki-CLAUDE.md` | Template for new wiki CLAUDE.md files |
| `skills/wiki-upgrade.md` | `/wiki-upgrade` skill — includes Step 4 INDEX.md bootstrap |
| `DEPLOYING.md` | Checklist — update before any new tool/skill ships |
| `SECURITY.md` | LaTeX execution security (Tier-1 defenses, CVE-2023-32700) |
| `AUTHORING.md` | Math and document rendering standard (MathJax, Mermaid, line wrapping) |
| `SIGNAL.md` | AI-for-Science communication standard — three pillars: Markdown+MathJax, wiki, Shannon/McCloskey |
| `AGENTS.md` | Codex-readable counterpart to the CLAUDE.md cc-tools section; hand-maintained, scoped to one Codex user (issue #61) |

## tex4md — peer project (active development)

LuaLaTeX-to-Markdown converter. Separate repo (`PhenomML/tex4md`); tracked as cc-tools issue #52. Developer Claude (TeX Claude) is the implementer; Andrew is the relay between sessions.

**Why:** tex4ht's HTML target requires structural completeness → register overflow (IEEEtran, issue #189) and conference template failures (#47, #48). Markdown target requires far fewer hooks; unknown macros degrade silently rather than cascading.

**Architecture:** `src/tex4md.sty` + `src/tex4md.lua` + `src/tex4md-mathcapture.tex`; LuaLaTeX execution; Strategy A (`$` as active character) for inline/display math verbatim capture; no new register allocations.

### Phase 1 — complete (committed fb575f9, 060d822)

Skeleton: sections, lists, abstract, bold/italic/tt, math `<!-- MATH -->` placeholders. `examples/minimal.tex` → `examples/minimal.md` verified. Key bug found on real paper (`math/0409186`): discretionary nodes (hyphens, ligatures) were silently dropped; fixed by reading `.replace` field off `disc` nodes.

### Phase 2 — complete (report: `tex4md/reports/PHASE2_REPORT.md`)

Verbatim math capture for `$...$`, `\[...\]`, `$$...$$`, and `equation` (via `environ.sty`). Macro preamble collection (`\newcommand`/`\def`) including recursive `\input` following (`expand_inputs`). UTF-8 normalisation (`tests/prepare_paper.py`). Validated against 6 papers.

**Key results:**
- `math/0409186`: 0 errors, 1483 lines, macro block byte-matches cc-tools make4ht reference output
- `2505.00326` (SteinSense): 457 macros from `\input` chain, 826 lines, 0 errors
- `1610.03082` (VAMP): `\beq`/`\eeq` hang fixed to fail-fast (1.2s, 1202 lines)

**Known gaps carried into Phase 3:**
- `align`/`align*`: 36.4% of corpus display math, 66% of papers — structural `\halign` ceiling under Strategy A; hybrid source-extraction architecture planned
- `equation*`: 21% of papers (one paper uses it exclusively) — tractable flag-based fix sketched
- `gather`/`gather*`: 0 occurrences in 29-paper corpus — de-prioritised

### Phase 3 — scoped (goals doc: `cc-tools/ideas/tex4md-phase3-goals.md`)

Eight issues, sequenced. Issue 7 (test harness) gates both Issue 1 and Issue 2 — `tex4md-mathcapture.tex` has documented silent-corruption history; no math changes ship without a reference-diff baseline.

| Issue | Description | Blocker |
|---|---|---|
| 7 | Formal corpus test harness (Python, like cc-tools) | — first |
| 1 | `equation*` verbatim capture (flag-based, `\@currenvir` ruled out) | Issue 7 |
| 2 | `align`/`align*` hybrid source-extraction | Issue 7 + desync test paper |
| 3 | Footnote passthrough (`[^N]:` syntax) | — |
| 4 | Theorem/lemma/proof environments (hook `\newtheorem`) | — |
| 5 | Figure + table captions (`\caption` in both float types) | — |
| 6 | Citation key passthrough `[@key]`; multi-key comma-split | — |
| 8 | cc-tools integration (`cc-arxiv --engine tex4md`) | Issues 1+2 stable |

**Workspace rule:** tex4md is TeX Claude's workspace. Do not commit or stage files there. Surface content for relay only.

## Agent compliance and scientific rigor (2026-07-23)

Three discussions from this session, all converging on the same root cause: the model generates a plausible next action without checking whether it is scientifically grounded.

### Issue #58 — generation-time failure to apply grounding

Filed by Andrew after a GoT session: model led with a confounded result as a headline finding, was corrected, then re-derived the same confound in a different form — requiring 3 corrections despite relevant standing principles being in context. Distinct from issue #46 (session-start loading): the material was present; it was not consulted at generation time.

**Diagnosis:** retrieval ≠ application. Correction momentum is not held as a persistent constraint across turns — the model re-derives from local context each time. The repetition datum (same confound, different form, three times) rules out "model didn't have the principle."

**Direction:** structural gate before commit, not context re-injection. A PreToolUse hook on Write/Edit touching research artifacts that forces explicit articulation of (a) what the confound prediction would have been, (b) why this result is discriminable from it. Always-loaded context (CLAUDE.md) is more reliable than on-demand skills for compliance-critical rules — Vercel eval data confirms 0% improvement from skills vs. 79% from AGENTS.md instructions.

### Commission scope discipline — Vera incident

Vera added ungrounded tasks to a commission without scientific justification. Andrew let them run (hoping for useful output) and was annoyed post-completion. The structural fix: mandatory `rationale:` field for every commission task — what question does this task answer, and what happens if it is omitted? A task that cannot answer both is malformed and does not run.

Key distinction: innovation expressed as a *hypothesis* ("I notice we haven't tested X because Y — should I add it?") is collaboration. Innovation expressed as silent task addition is unauthorized scope expansion. The commission document is the approval gate; additions after approval require a new approval.

### Skill improvement landscape survey

Surveyed the ecosystem of Claude skill improvement projects (2026-07-23):

| Project | Key pattern | Distinct contribution |
|---|---|---|
| task-observer (rebelytics) | Observe→log→weekly review; cross-cutting principles file | Deliverable-event flush hook; self-improvement loop |
| skill-optimizer (hqhq1025) | Mining from session transcripts; trigger-fit audit | Lifecycle separation (mine / personalize / generalize) |
| instruction-tuning (adam-s) | Sub-agent as test subject; iterate until compliance without hints | Only approach targeting generation-time failure directly |
| review-claudemd (ykdojo) | Mine transcripts for rule violations; propose stronger CLAUDE.md wording | Retroactive wording improvement from real violations |
| agnix (agent-sh) | Static linter for CLAUDE.md/SKILL.md; 437 rules | Pre-flight structural validation |
| Memento-Skills (arXiv:2603.18743) | Formal closed-loop with trainable skill router | Peer-reviewed validation; 26–116% accuracy gains |

**Vercel finding (critical):** Skills with default behavior achieve 0% improvement over baseline because agents invoke them 0% of the time. AGENTS.md instructions: 79%. Embedded docs index in AGENTS.md: 100%. Compliance-critical rules go in always-loaded context, not skills.

**Action items from survey:**
1. Promote Research Discipline section to `~/.claude/CLAUDE.md` immediately — always-loaded is the right home
2. Add `cross-cutting-principles.md` at cc-tools level, propagated via `/wiki-upgrade`
3. Run `review-claudemd`-style transcript mining on recent violation sessions to strengthen CLAUDE.md wording
4. Evaluate Graphify hands-on (desk research only; GRAPH_REPORT.md pattern is worth trying on cc-tools or a wiki)

## Codex compatibility — minimal scope (2026-07-24)

Issue #61 (external, `aasyed36`) proposed a full multi-provider framework:
agent-neutral `setup.sh --target {codex,claude,all}`, dual `AGENTS.md`/
`CLAUDE.md` generation, real `SKILL.md`-shaped Agent Skills, `.codex/config.toml`
handling, plugin manifests, compatibility test matrix. Declined as scoped —
see commit `de1e076` and the issue comment for full reasoning.

**Actual driver:** one research-group member is already running cc-tools
under Codex unassisted, because the 14 `cc-*` CLI entry points are plain
`uv tool install` binaries and were already agent-neutral. What was missing
was discovery — Codex reads `AGENTS.md`, not `CLAUDE.md`, so it had no way
to know the toolset or workflows existed.

**Shipped:** `AGENTS.md` at repo root — same tool table as
`claude-md-section.md`, research workflows rewritten as plain prose (no
`$ARGUMENTS`/slash-command syntax), a fallback rule ("if a directory has
`CLAUDE.md` and no local `AGENTS.md`, read `CLAUDE.md` as the operating
instructions" — lets existing wikis work under Codex without duplicating
every wiki's `CLAUDE.md`), and explicit Claude-only flags for memory-audit,
agent-brief, and wiki-upgrade's sentinel-block rewrite. No installer changes.

**Staged plan (posted to issue #61):** Stage 0 (shipped) — static file, one
user. Stage 1 — let the student's actual usage surface friction; fix
specific breakage as reported, not speculatively. Stage 2 — only if a
second Codex user appears: `cc-wiki-brief --runtime codex`, sentinel-block
automation for `~/.codex/AGENTS.md`, possible `SKILL.md` port of the
highest-traffic workflows. Stage 3 — only if the group standardizes on
multi-agent work: revisit issue #61's full proposal.

**How to apply:** Do not build Stage 2/3 infrastructure without a second
demonstrated Codex user. If `AGENTS.md` and `claude-md-section.md` drift,
`claude-md-section.md` is authoritative — reconcile by hand for now.

## Graphify trial — aborted, ROI unclear (2026-07-23/24)

Attempted to run `/graphify` on `geometry-of-truth` and `Meridian` via
background agents. Both stalled well past the ~5 min estimate (28+ min).
Initial hypothesis was a nested-agent architecture issue (the skill's
semantic-extraction step dispatches its own Agent-tool subagents per file
chunk; running the skill *from* a background agent would double-nest that
dispatch). **Andrew's correction (2026-07-24): this is unconfirmed** —
graphify may simply take significant setup time on old, complex repos
regardless of nesting. Both GoT and Meridian are large, long-running
corpora (433 and 205+339 files). More importantly: **it is not yet clear
graphify is worth the setup cost** — an open evaluation question, not a
solved problem.

**Also surfaced a workspace-write violation:** both projects are other
agents' workspaces (Vera's GoT, Emma's Meridian). Neither running graphify
there nor cleaning up the resulting `graphify-out/` directories afterward
should have happened without asking first — "Andrew asked for it" and "I
created the files" were both treated, incorrectly, as authorization. See
`feedback_workspace_write_discipline` memory (extended this session).

**Status:** both `graphify-out/` directories removed; GoT and Meridian are
back to pre-trial state. Not yet retried.

**How to apply:** Don't restate the nested-agent theory as a confirmed
diagnosis. Before recommending a retry, the time-cost/value tradeoff needs
addressing first, not just the execution mechanics — and any retry still
requires explicit confirmation from Vera/Emma or Andrew before running
tooling in their workspace.

## Research Discipline (new, 2026-07-16)

Karpathy's "CLAUDE.md: Field Notes on Getting a Language Model to Write Code You Will Not Rewrite" (v260626) was discussed and translated to the research context. Ten rules; throughline: the model generates plausible output fast and notices plausible ≠ correct slowly — the discipline comes from process, not the model.

**Draft for `~/.claude/CLAUDE.md`:** `ideas/research-discipline-draft.md` — ten rules rewritten for research sessions: read wiki first, name the task before starting, minimum scope, surgical edits, verify before asserting, success criterion first, investigate don't substitute, check before creating, precise uncertainty, named failure modes. Includes *Workspace Trespass* as a fifth failure mode specific to our multi-agent setup.

**Source document:** `ideas/karpathy-claude-md-rules.md` — full text + research translation table.

**Status:** Draft ready for review; not yet promoted to `~/.claude/CLAUDE.md`.

## SIGNAL.md — communication standard (2026-07-07)

Three-pillar discipline for all AI-generated scientific content.

1. **Markdown + MathJax** — structured documents; all math in `$...$`/`$$...$$` LaTeX
2. **Wiki** — knowledge in owned files, not context windows; `*[Imputed]*` for ungrounded claims
3. **Shannon + McCloskey** — maximum information per word; claims stated as claims

**Implementation pending:** prose section in `AUTHORING.md`; update `templates/wiki-CLAUDE.md`; create `/shannon` skill.

## Shell environment: cmux (assessed 2026-06-24)

cmux ([manaflow-ai/cmux](https://github.com/manaflow-ai/cmux)) is the candidate group shell. KaTeX PR implementation deferred pending maintainer response to issue #6749.

## Wiki navigation pattern (new in v0.2.0)

`cc-wiki-grep` + `INDEX.md` — token-efficient two-step wiki access. Deployed to all 12 sentinel-bearing research wikis (2026-07-07). `/wiki-upgrade` Step 3b injects wiki-access behavioral rule; Step 4 bootstraps INDEX.md.

## Agent session management

**Sessions are disposable, files are not.** ORIENTATION.md, log.md, and commission documents are the continuity layer.

- **Workspace write discipline:** almost never write in another Claude's workspace; relay is not a session-close signal; ask explicitly before any write to another agent's repo.
- **Post-compaction:** re-read ORIENTATION.md + last log entry before continuing.
- **One session per deliverable phase; clean close every time.**

## Current state of the make4ht pipeline (cc-arxiv --src)

Two-step: make4ht (TeX→HTML) → pandoc (HTML→Markdown), with pandoc-direct-LaTeX fallback.

**Active upstream engagement:** Issue #189 (IEEEtran register overflow) and #190 (algpseudocode) posted to make4ht; awaiting Michal Hoftich's response. Protocol: Andrew relays; never file make4ht issues without his go-ahead.

**IEEEtran status:** All IEEEtran papers still fall to pandoc-latex. Fix path is tex4md (issue #52).

**Conference paper preprocessing:** `scripts/preprocess_corpus.py` — 24 strip rules, 7/10 problem papers now convert. Section-concat strategy for multi-file papers; body-direct for single-file. Key structural traps: abstract wrapper in main.tex not section file; title from `\title{}` only (never construct from filenames); enumerate all appendix files explicitly.

**arXiv:2603.05498 (Sun et al. 2026):** Canonical copy pending Vera ingestion (active session as of 2026-07-16).

## Test corpus

10 papers. Run: `uv run pytest` (offline, ~1s from cache).

| arXiv ID | Pipeline | Notes |
|---|---|---|
| 2505.00326 (SteinSense) | make4ht | tex4md Phase 2 test: 457 macros, 826 lines |
| math/0409186 (Candès et al.) | make4ht | tex4md Phase 2 test: byte-matches make4ht macro block |
| 0906.2530 (Donoho & Tanner) | make4ht | |
| 0907.3574 (AMP) | pandoc-latex | IEEEtran register overflow |
| 1111.1041 (AMP minimax) | pandoc-latex | IEEEtran memory exhaustion |
| 1610.03082 (VAMP) | pandoc-latex | IEEEtran; tex4md Phase 2 test: hang→fail-fast |
| 2512.24601 (RLM) | make4ht | |
| 2211.00593 (IOI circuit) | pandoc-latex | ICLR class; fixed pandoc cwd bug (#45) |
| 2305.13571 (Chi et al.) | pdf-only | ACL template; issue #47; equation* only display math |
| 2501.00073 (Zuo et al.) | pdf-only | COLING class; issue #48 |
| 2603.05498 (Sun et al.) | pdf-only | ICML class; issue #57; preprocessor succeeds |

## Open issues (selected)

| # | Summary |
|---|---|
| 57 | cc-arxiv --src: make4ht failure on 2603.05498 (ICML class, xcolor/colortbl) |
| 52 | cc-arxiv --src: tex4md engine integration |
| 47 | cc-arxiv --src: ACL template failure (2305.13571) |
| 48 | cc-arxiv --src: COLING template failure (2501.00073) |
| 39 | cc-arxiv --src: figure files in tarball not extracted/embedded |
| 27 | cc-arxiv --src: fallback chain HTML → tarball → PDF |
| 21 | cc-webfetch --math: pandoc pipeline for math-heavy HTML pages |
| 19 | /wiki-orient skill |
| 61 | Codex support (external) — declined as scoped; narrower `AGENTS.md` shipped instead, tracked for the fuller design if a second Codex user appears |

## Pending work

- **Codex friction from real usage:** watch for reported breakage against `AGENTS.md` (Stage 1 of the issue #61 plan) — fix specific issues as the one Codex user hits them, don't pre-build Stage 2/3
- **Graphify — ROI unresolved:** aborted trial on GoT/Meridian; setup cost on large old repos may be inherent, not a nesting bug — whether it's worth the time is still an open question, decide that before any retry; a retry also needs Vera's/Emma's or Andrew's explicit go-ahead to run tooling in their workspace
- **Research Discipline section:** `ideas/research-discipline-draft.md` — promote to `~/.claude/CLAUDE.md`; Vercel data confirms always-loaded is the right home; pending Andrew approval
- **Cross-cutting principles file:** create `cross-cutting-principles.md` at cc-tools level; propagate via `/wiki-upgrade`; starting content: commission rationale field, workspace write rule, `*[Imputed]*` as stop signal, confound-discriminability check
- **Commission rationale field:** add mandatory `rationale:` field to commission template; gates unauthorized scope addition
- **tex4md Phase 3:** relay goals doc (`ideas/tex4md-phase3-goals.md`) to TeX Claude; Issue 7 (test harness) first
- **cmux KaTeX PR:** implement once maintainer responds to issue #6749
- **File issue for 2602.02385:** tex4ht .xbb failure pattern not yet filed
- **Upstream tikz-hooks.4ht report (issue #44):** draft for Andrew to relay to Michal
- **SIGNAL.md implementation:** prose section in AUTHORING.md, `/shannon` skill, wiki-CLAUDE.md updates
- **Antigravity CLI migration:** templates rename, setup-claude.sh flag (blocked on billing)
- **Diagnose ACL/COLING failures (issues #47, #48):** run make4ht locally with verbose output

## Install / test

```bash
uv tool install --reinstall --force .
uv run pytest
```

Always use `uv run pytest`, not `python -m pytest`.
