# <Experiment Name> Wiki

## Purpose

**Subject:** <Experiment or project name>
**Created:** <YYYY-MM-DD>
**Goal:** <driving goal — read the operational brief in ../CLAUDE.md for full context>

## Log format

Append an entry to `log.md` after every experiment, decision, or synthesis. Format:

```
## [YYYY-MM-DD] <operation> | <description>
```

**Operations:**

| Operation | When to use |
|---|---|
| `experiment` | A computation or code run with a quantitative result |
| `commission` | Starting a new phase or assigning work to an agent |
| `synthesis` | Writing a synthesis page from accumulated results |
| `review` | Reviewing a paper, result, or another agent's output |
| `decision` | A design or methodology choice with recorded rationale |
| `query` | Answering a specific research question from the evidence |

**Worked examples:**

```markdown
## [2026-05-10] experiment | Phase -1: DT boundary computation
Result: δ*(ε̂) = 0.31, within factor-of-two of 0.25. PASS.
Implication: CS-native framing has quantitative grounding. Proceed to Phase 0.

## [2026-05-10] synthesis | Phase -1 results filed
Synthesis: syntheses/phase-minus1-results-emma.md
Key finding: masking ratio 0.25 aligns with DT boundary within factor of two.

## [2026-05-10] review | xfmr sign-convention response
Reviewed: syntheses/sign-convention-response-xfmr.md
Resolution: sign discrepancy was a coordinate convention, not a bug. Finding documented.

## [2026-05-10] commission | Phase 0 started
Hardware: GB10 Blackwell. First task: Onsager Jacobian validation at <10⁻⁶ FP32 error.

## [2026-05-10] decision | Use luma channel only for Phase -1 wavelet analysis
Rationale: chroma channels less compressible; luma is the canonical CS benchmark.
Approved by researcher before computation began.
```

## Multi-agent convention

This wiki may be shared between multiple Claude instances with the researcher as relay.
Each agent has a separate context — discrepancies between agents are findings, not errors.

**File naming:** `syntheses/<topic>-<agent-slug>.md`
Examples: `syntheses/phase-minus1-results-emma.md`, `syntheses/sign-convention-response-xfmr.md`

**Asking questions:** append `## Questions for <Agent>` to any synthesis file.
**Responding:** write a new file `syntheses/<topic>-response-<agent-slug>.md`.
**Blackboard rule:** `syntheses/` is append-only. Never overwrite another agent's files.

## Scope

This is not a research literature wiki. The following do not apply here:
- `/wiki-ingest`, `/wiki-lint`, cross-wiki linking — research-wiki workflows
- arXiv, bioRxiv, CrossRef fetching — use `raw/` only for experiment-supporting documents

For the full operational brief, read the document referenced in `../CLAUDE.md`.
