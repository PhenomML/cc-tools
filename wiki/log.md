# Session Log

## [2026-06-15] pattern | INDEX.md + cc-wiki-grep navigation — field assessment
wiki/patterns/index-md-navigation.md created. First real-world evaluation by Cass (compressed-sensing wiki): useful for session-start orientation and long-tail page discovery; tag taxonomy is rough; high-frequency pages bypass it via memory; verdict "useful, not transformative." Design note on tag-miss backstop added.

## [2026-06-15] ingest | Zhang, Kraska, Khattab (2025) — Recursive Language Models
Sub-wikis: papers. Pages written: 1 (papers/zhang-2025-recursive-language-models.md). pipeline-status.md created.
Fetch: cc-arxiv --src failed (tex4ht exit code 1; pandoc stub useless — issue #42 filed). PDF+markitdown fallback: ✓ full text from line ~100.
Key concepts: RLM as REPL-environment paradigm; parallels to cc-tools wiki-as-active-memory architecture noted in paper page.

## [2026-06-15] memory-audit | /memory-audit — private memory triage
9 entries retired to wiki/memories/ (cs-onsager-pipeline, dd25-adjudication, icloud-sync-decision, version-policy, markdownnew-cf-bug, fc2-gate-design, research-memory-isolation, donoho-session-improvements, transformers-adversary). 2 entries updated (adversarial-review-discipline, fran — FC2-16 refs stripped; upstream-bug-filing — Michal validation added). pyproject.toml bumped to v0.2.0. wiki/memories/ directory established as public memory layer.

## 2026-06-14

Wiki initialized. Driving question: what are we learning about AI-assisted research tooling through building and using cc-tools?

Structure: `tools/`, `patterns/`, `upstream/`.

**Context:** This wiki was instantiated after a session covering:
- TEXMFCNF fix (make4ht Lua module path bug masking all failures)
- make4ht failure instrumentation (log tail surfaced to stderr)
- Operating Claude issue-filing rule on pandoc-latex fallback
- `/memory-audit` skill (stale memory detection, ORIENTATION.md size check, wiki/no-wiki context awareness)
- Issue #40 (wiki pages as steward working memory) and #41 (public memory type)
- Design decision: cc-tools wiki in-repo to demonstrate self-improvement loop for adopters

**Pending:** Memory consolidation — `/memory-audit` to promote private memory content into this wiki. Run in a fresh session.
