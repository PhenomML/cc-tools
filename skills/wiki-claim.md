Enumerate FR-2 claims from an ingested source, or triage a source for the deep read queue: $ARGUMENTS

`$ARGUMENTS` is one of:
- `triage <source>` — lightweight relevance screen; no full paper read
- `deep <source>` — full cold read claim enumeration; requires prior human approval
- `adjudicate <source>` — present RMC/AG claim diff for human-guided adjudication

`<source>` is a path to a file, an arXiv ID, or a slug matching an already-ingested source in `raw/`.

---

## Agent Identity

Read `.claude/settings.local.json` in the current directory before any file operations:

```bash
python3 -c "
import json, pathlib
p = pathlib.Path('.claude/settings.local.json')
if p.exists():
    d = json.loads(p.read_text())
    print(d.get('agent_role', 'unknown'))
    print(d.get('brief_root', ''))
    print(d.get('adversary_root', ''))
else:
    print('unknown')
" 
```

- `agent_role: primary` → this is the RMC workspace (brief root)
- `agent_role: adversary` → this is the AG workspace; use `brief_root` to locate brief
- `agent_role: unknown` or file absent → stop and ask the human before proceeding

**Brief root resolution for AG:** if `agent_role` is `adversary`, all reads of source material
use `<brief_root>/raw/<source>`. All promotions to the shared channel use
`<brief_root>/syntheses/`. The `brief_root` value is a relative path from the adversary
workspace (e.g., `../compressed-sensing`).

**Never read the other agent's draft directory before the adjudication phase.**

---

## Pipeline Registry

The five-state pipeline is tracked in `claims/_index.md` under `## Pipeline Status`.

**States:** `triage` → `rmc-draft` → `ag-draft` → `diff-routed` → `adjudicated`
**Skipped sources** use state `skipped` (written at triage Skip decision, not on this path).

**Table format** (create section if absent):

```markdown
## Pipeline Status

| Source | Prefix | Status | Triage | RMC-Draft | AG-Draft | Diff-Routed | Adjudicated |
|--------|--------|--------|--------|-----------|---------|-------------|-------------|
```

**Update rules:**
- On approval at triage: add row with status `triage`, Triage date filled, others `—`
- On RMC deep completion: update status to `rmc-draft`, fill RMC-Draft date
- On AG deep completion: update status to `ag-draft`, fill AG-Draft date
- On diff routing complete: update status to `diff-routed`, fill Diff-Routed date
- On adjudication complete: update status to `adjudicated`, fill Adjudicated date, fill Prefix

If the source has no row and `ag-draft` state is needed (files already exist in syntheses/),
create the row with status `ag-draft` and fill known dates from file timestamps.

---

## TRIAGE mode

`/wiki-claim triage <source>`

**Purpose:** Abstract-level relevance screen. Cheap — no full paper read. Produces a
triage entry for the human to review before approving a deep read investment.

### Step 1 — Read abstract only

If source is an arXiv ID not yet fetched:
```bash
cc-arxiv <id>
```
Use the abstract from the metadata output. Do not fetch the full paper.

If source is a path or slug already in `raw/`, read the first 50 lines only.

For primary agent: `raw/<source>.md`
For adversary agent: `<brief_root>/raw/<source>.md`

### Step 2 — Write triage entry

Append to `syntheses/triage-queue.md` (create with header if absent). Primary agent
writes to `syntheses/` in the brief root. Adversary agent writes to `<brief_root>/syntheses/`.

```markdown
## [TRIAGE-<NNN>] <Author> (<Year>) — <Title>

**Source:** <arXiv ID / DOI / path>
**Driving question:** <verbatim driving question from wiki CLAUDE.md>
**Verdict:** Central | Peripheral | Tangential | Not relevant
**Reason:** <one sentence — specifically what this paper contributes or doesn't>
**Estimated yield:** High | Medium | Low
**Recommended action:** Deep read | Skim | Skip
**Fetch status:** Available | Paywalled | Queued
**Triaged:** <YYYY-MM-DD>
```

Increment TRIAGE-NNN from the last entry in the file.

### Step 3 — Present to human

Present the triage entry and wait for human decision:
- **Approve deep read** → add to `## Approved for Deep Read` section; proceed to Step 4
- **Skip** → write skip entry to `claims/_index.md` under `## Skip Log`; write registry
  row with status `skipped`; stop
- **Defer** → leave in triage queue for batch review; stop

Do not proceed to deep read without explicit human approval.

### Skip log entry format

Append to `claims/_index.md` under `## Skip Log`:

```markdown
| <YYYY-MM-DD> | <Author Year> | <Title fragment> | <one-sentence reason> |
```

### Step 4 — Update pipeline registry

On human approval for deep read, update `claims/_index.md` Pipeline Status:
- Add row (or update existing row) for this source
- Set Status to `triage`, Triage date to today, all other date columns to `—`
- Prefix column: `—` (assigned at adjudication)

---

## DEEP mode

`/wiki-claim deep <source>`

**Purpose:** Full cold read claim enumeration. Costs significant tokens. Requires
prior human approval (triage entry must exist in Approved queue, or human must
explicitly confirm in session).

**Cold read discipline:** Do not read the other agent's outputs before completing
your own enumeration. If the other agent's output is already in `syntheses/`,
do not open it until the adjudication phase.

### Step 1 — Confirm approval

Check `syntheses/triage-queue.md` for an approved entry matching this source.
If not found, ask the human to confirm before proceeding. Do not proceed without
confirmation.

### Step 2 — Read the full source

**Primary agent:** read from `raw/<source>.md` in the brief root.
**Adversary agent:** read from `<brief_root>/raw/<source>.md`.

For large files (>256KB), read in sections using offset and limit — read the full source,
not just the abstract.

### Step 3 — Enumerate claims

Work through the source in **reading order** — not importance order. Surface every
claim that bears on the wiki's driving question. Do not pre-filter by importance;
the human adjudicates importance during the diff phase.

For each claim, construct a claim block:

```markdown
## [<PREFIX>-<NNN>]

**Statement:** <claim in your own words, precisely and falsifiably>

**Quotation:**
> "<minimal verbatim passage that grounds this claim>"
> (<section reference, e.g. §4, Table 1, p.12>)

**Relevance:** <why this claim matters to the driving question — be specific>

**Confidence:** High | Medium | Low

**Math:** <LaTeX if relevant, using $...$ notation>
```

**Discipline:** a claim is a falsifiable assertion grounded in the source. It is not
a paraphrase of the abstract or your interpretation of what the source implies. If you
cannot find a minimal quotation that grounds it, it is not a claim from this source —
flag it as `*[Imputed]*` instead.

**Prefix derivation:** author surname initial(s) + 2-digit year + sequence.
Examples: `DON23-001`, `TR17-003`, `LEM24-007`.
Check `claims/_index.md` for the assigned prefix — use existing prefix if the source
has been partially processed before. If no prefix exists, propose one and confirm
with the human before filing.

### Step 4 — Write to agent workspace

**Primary agent:** write to `claims/drafts/<source>-claims-rmc.md` in the brief root.
**Adversary agent:** write to `cold-reads/<source>-claims-ag.md` in the adversary workspace.

File header:
```markdown
---
source: <author-year-slug>
agent: rmc | ag
role: primary | adversary
session: <YYYY-MM-DD>
status: draft — not yet adjudicated
driving_question: "<verbatim from wiki CLAUDE.md>"
---

# Claims: <Title>

*Cold read by <agent>. Do not share with other agent before adjudication.*
```

### Step 5 — Structural gaps

After all claims, add a gaps section:

```markdown
## Structural Gaps

**Excluded results:** <name any results you chose NOT to enumerate and why>

**Contradictions with wiki:** <any claims that conflict with existing wiki claims>

**Most important contribution:** <single most important thing this source contributes,
independent of the current hypothesis>

**Low-confidence claims requiring elevation:**

| Claim | What is needed to raise confidence |
|---|---|
| <PREFIX-NNN> | |
```

### Step 6 — Promote to shared channel

When enumeration is complete, promote to the shared coordination channel:

**Primary agent:** copy to `syntheses/<source>-claims-rmc.md` (in brief root)
**Adversary agent:** copy to `<brief_root>/syntheses/<source>-claims-ag.md`

Append to `log.md` in the brief root:
```
## [<YYYY-MM-DD>] claim-deep | <Author Year> — <Title>
Agent: <rmc|ag>. Role: <primary|adversary>. Claims enumerated: <N>.
Promoted to syntheses/ for adjudication.
```

Do not notify the other agent directly — the human coordinates the diff phase.

### Step 7 — Update pipeline registry

Update `claims/_index.md` Pipeline Status for this source:

- **Primary agent:** set Status to `rmc-draft`, fill RMC-Draft date to today
- **Adversary agent:** set Status to `ag-draft`, fill AG-Draft date to today

If the row does not exist (triage step was skipped), create it with available dates filled
and unknown dates as `—`.

---

## ADJUDICATE mode

`/wiki-claim adjudicate <source>`

**Purpose:** Present the RMC/AG claim diff for human-guided adjudication. Run only
after both agents have promoted their cold reads to `syntheses/`. Run by either agent
or by Tool at human direction.

### Step 1 — Registry gate check

Read `claims/_index.md` Pipeline Status for `<source>`:

- Status `ag-draft` → proceed
- Status `rmc-draft` → report: "AG draft is outstanding. AG deep read must complete
  before adjudication." Stop.
- Status `triage` or no row → check `syntheses/` directly for both files. If both
  exist, create/update registry row to `ag-draft` and proceed. Otherwise report which
  file(s) are missing and stop.
- Status `diff-routed` → report current status; ask if re-adjudication is intended
  before proceeding.
- Status `adjudicated` → report: already adjudicated. Show final file location. Stop
  unless human confirms re-adjudication.

### Step 2 — Load and route claims

Read both claim sets:
- `syntheses/<source>-claims-rmc.md`
- `syntheses/<source>-claims-ag.md`

Build four queues by comparing claims across both sets. Matching is by quotation
proximity: two claims are about the same result if their supporting quotations share
a key phrase from the same paper section (normalize: strip whitespace, treat curly/straight
quotes as equivalent, treat `...`/`…` as equivalent).

**Queue A — Anchor candidates:**
Claims where both agents enumerated the same result, quotations match after normalization,
and **both** assigned High confidence. These are high-agreement anchors for fast-pass review.

**Queue B — Coverage divergences (always surface):**
- B1: Claims RMC enumerated that AG did not
- B2: Claims AG enumerated that RMC did not
Coverage divergences are the primary diagnostic for operational bias — never suppress them.

**Queue C — Confidence mismatches:**
Claims both agents enumerated (quotation match) but with different confidence levels.

**Queue D — Rival interpretations:**
Claims both agents enumerated from the same passage but with materially different statements.

**conjectures.md is never written by this pipeline.** The human may direct filing a
specific item to conjectures during adjudication; the pipeline does not auto-file.

### Step 3 — Present anchor fast-pass list

Present Queue A:

```
### Anchor Fast-Pass Candidates
Both agents enumerated these claims with matching quotations and High confidence.

1. <one-line statement>
   > "<quotation>" (<§ref>)
   RMC: High | AG: High

2. ...

Decision: Accept all as anchors? Or name specific items to review individually.
```

Wait for human decision. "Accept all" or list of individual exceptions (each exception
drops to the human-review queue at the appropriate type).

### Step 4 — Present human-review queue

Work through queues B, C, D in order. Present one item at a time; wait for human
decision before presenting the next.

**Coverage divergences (Queue B) — present first:**

```
### Coverage Divergence [B1/B2]: <brief description>
Enumerated by: RMC only | AG only
Statement: <claim statement from the enumerating agent>
> "<quotation>" (<§ref>)
Relevance: <why this matters to the driving question>
Decision: Accept | Drop | Escalate (defer to focused session)
```

**Confidence mismatches (Queue C) — after all B items:**

```
### Confidence Mismatch: <brief description>
RMC: <statement> [High/Medium/Low]
AG: <statement> [High/Medium/Low]
> "<shared quotation>" (<§ref>)
Decision: Use RMC rating | Use AG rating | Assign: H / M / L | Escalate
```

**Rival interpretations (Queue D) — after all C items:**

```
### Rival Interpretation: <paper section / topic>
RMC version: <statement>
> "<RMC quotation>"
AG version: <statement>
> "<AG quotation>"
Decision: Accept RMC | Accept AG | Merge (provide merged statement) | Escalate
```

**Escalate** means defer to a focused session — it does not auto-file anywhere.
Record escalated items at the end of the diff session as open questions in `log.md`.

### Step 5 — Update registry: diff-routed

After all queue items have been decided, update `claims/_index.md` Pipeline Status:
- Set Status to `diff-routed`
- Fill Diff-Routed date to today

### Step 6 — Write final claim document

Assemble the final claim set from all accepted and merged decisions.
Write to `claims/<source>-claims.md` in the brief root:

```markdown
---
source: <author-year-slug>
prefix: <PREFIX>
adjudicated: <YYYY-MM-DD>
session: <session reference>
rmc_draft: syntheses/<source>-claims-rmc.md
ag_draft: syntheses/<source>-claims-ag.md
driving_question: "<verbatim>"
---

# Claims: <Title>

*Adjudicated claim set. Grounded claims are citable as [[<source>-claims#PREFIX-NNN]].*
*Imputed statements are flagged inline with *[Imputed]* or *[Imputed — [[source#ID]]]*.*

<adjudicated claim blocks>
```

### Step 7 — Update prefix registry

Update `claims/_index.md` Prefix Registry:

```markdown
## Prefix Registry

| Prefix | Source | File | Adjudicated |
|---|---|---|---|
| <PREFIX> | <Author Year Title> | [[<source>-claims]] | <YYYY-MM-DD> |
```

### Step 8 — Update registry: adjudicated + log

Update `claims/_index.md` Pipeline Status:
- Set Status to `adjudicated`
- Fill Adjudicated date to today
- Fill Prefix column

Append to `log.md`:
```
## [<YYYY-MM-DD>] claim-adjudicate | <Author Year> — <Title>
Claims accepted: <N>. Rejected: <N>. Escalated: <N>.
Final file: claims/<source>-claims.md
```

Report every file created or modified.

---

## The `*[Imputed]*` Convention

Use `*[Imputed]*` inline after any statement that is not grounded in an enumerated
claim with a quotation. Two forms:

**Unlinked** — no known grounding claim exists:
```
A sub-quadratic approximation may be viable. *[Imputed]*
```

**Linked** — a specific claim would ground this if extended:
```
This generalizes to the noisy case. *[Imputed — [[donoho-2023-claims#DON23-004]]]*
```

An imputed statement is a work order, not a finding. High imputed density in output
signals the session wandered off-wiki.
