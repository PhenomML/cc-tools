---
promoted_from: private memory (project_cs_onsager_pipeline.md)
promoted: 2026-06-14
status: complete — all commissions closed
---

# CS Onsager Pipeline — Completed Record

Full adversarial pipeline run on Cass's Onsager Jacobian Lemma (compressed-sensing wiki). Both commissions complete as of 2026-05-15.

**Pipeline documents:** `~/Research/Topics/compressed-sensing/claims/`

## Final commission outcomes

- **COMM-001R:** COMPLETE + ACCEPTED (2026-05-12). C3 Medium, C4 High, C5 High (math+test) / documented JAX divergence at q=B-2 (JAX returns 0.5, closed-form returns 0.0). Environments: `envs/steinsense-proof.yml`, `envs/steinsense-verify.yml`.
- **COMM-002:** COMPLETE (2026-05-15). Stressed Σ test. Onsager CF = AD at machine precision for all κ ≤ 1e12; float32 safe for stable AMP regime; degenerates silently at κ > 1e8. C11 directional uncertainty closed. Findings in `~/Projects/PhenomML/SteinSense/docs/architecture-notes.md`.

## Key findings from v2 destroy

- **Fatal (P6):** "Resolves §1 open question" not supported — paper says "major computational bottleneck," never "unsolved."
- **Significant (P4):** Boundary non-differentiability at $q_i = B-2$; JAX subgradient convention now stated explicitly in v3.
- The formula itself is mathematically sound — machine epsilon verification stands.

## v3 falsifiability test: PASS

C7 (contribution framing) held at High with direct paper quotations from §6 and §8.

## Process lessons for cc-tools

- **Gemini template discipline:** Gemini departed from the Part 1–5 critique template in v3, writing its own structure. Content was sound but synthesis had to adapt. Future destroy briefings must explicitly reinforce the template.
- **Primary source gap:** Enumerating a synthesis without reading its cited primary sources allows the synthesis's own framing errors to propagate. C7 was rated High but the paper only called it a "major computational bottleneck." The Part 0 rule in the enumeration template prevents recurrence.
- **Cross-file memory consistency:** After COMM-002 completed, `project_cs_onsager_pipeline.md` and `project_dd25_adjudication.md` still showed it as pending. Stale cross-references are a recurring memory hygiene problem — the audit that caught this is the fix.
