---
promoted_from: private memory (project_fc2_gate_design.md)
promoted: 2026-06-15
status: shipped
---

# FC2 Gate Design — Option C Shipped

Five-state adjudication pipeline shipped to `/wiki-claim` skill (commit 9c48f9c, 2026-05-13).

## Pipeline states

`triage → rmc-draft → ag-draft → diff-routed → adjudicated`

State tracked in `claims/_index.md` with rmc-draft and ag-draft timestamps.

## Routing rules

- **Auto-accept (fast-pass):** both enumerate, both High confidence, matching normalized quotation
- **Surface to human-review:** all coverage divergences (regardless of confidence), all content disagreements, all confidence mismatches
- **conjectures.md:** human-promoted only — pipeline never auto-files
- Queue sorted by type: anchors → coverage → confidence mismatch → rival interpretations

Coverage divergences always surface regardless of confidence — they are the adversarial pipeline's primary diagnostic for operational bias.
