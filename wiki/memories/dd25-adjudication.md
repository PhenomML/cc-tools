---
promoted_from: private memory (project_dd25_adjudication.md)
promoted: 2026-06-14
status: complete — all claims adjudicated, math fidelity verified, COMM-002 closed
---

# DD25 Adjudication — First Option C Pipeline Run

First live run of the Option C five-state pipeline. Dey & Donoho 2025 (SteinSense). Cass (RMC) enumerated 25 claims; AG enumerated 7.

**Final adjudicated set:** 24 claims in `~/Research/Topics/compressed-sensing/claims/dey-donoho-2025-steinsense-claims.md`. Prefix DD25.

## Key outcomes

- **DD25-003q:** Parameter-free claim split into user-interface claim (High) + implementation qualification (High). Template for future splits — two clean claims beats one merged Medium. Fran's contribution.
- **DD25-016:** Merged claim (RMC neutral observation + AG internal-contradiction framing); COMM-002 live pointer added — Σ ill-conditioning. COMM-002 now complete (2026-05-15).
- **DD25-021:** Theorem 10.1 (BST minimax optimal at extreme sparsity ε→0) — bounds SteinSense's advantage; load-bearing for intellectual honesty.
- **DD25-022:** Dropped (imputed ratio, no direct quotation).

## Math fidelity — verified clean

Cass ran full spot-check of all 24 DD25 claims against `--src` version (2026-05-14). Verdict: no revisions needed. The `--src` text strengthens grounding on every claim that had noisy MathML in the HTML version. All 24 claims stand.

## Process lessons for cc-tools

- **Coverage divergence signal:** 25 vs 7 claims is large but not a quality problem — AG's selection criterion was genuinely different (headline results vs. mechanism-level claims). Coverage divergences are diagnostic, not a count problem.
- **FR-001:** Adjudication started twice without explicit researcher direction. Fix: CLAUDE.md directive clause + `/wiki-claim` pre-flight confirmation block (commit be2533e). Lesson: process gates need infrastructure, not just memory.
- **`--src` as adjudication tool:** HTML MathML was noisy throughout; `--src` grounding resolved every ambiguity without requiring claim revisions. Standard practice for math-heavy papers going forward.
