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
- **Approve deep read** → add to `## Approved for Deep Read` section
- **Skip** → write skip entry to `claims/_index.md` under `## Skip Log`
- **Defer** → leave in triage queue for batch review

Do not proceed to deep read without explicit human approval.

### Skip log entry format

Append to `claims/_index.md` under `## Skip Log`:

```markdown
| <YYYY-MM-DD> | <Author Year> | <Title fragment> | <one-sentence reason> |
```

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

---

## ADJUDICATE mode

`/wiki-claim adjudicate <source>`

**Purpose:** Present the RMC/AG claim diff for human-guided adjudication. Run only
after both agents have promoted their cold reads to `syntheses/`. Run by either agent
or by Tool at human direction.

### Step 1 — Verify both reads exist

Check that both files exist in `syntheses/` (in the brief root):
- `syntheses/<source>-claims-rmc.md`
- `syntheses/<source>-claims-ag.md`

If either is missing, report which agent's read is outstanding and stop.

### Step 2 — Compute the diff

Read both claim sets. Produce a structured diff:

```markdown
## Claim Diff: <Title>

### In both (high-confidence anchors)
<claims where both agents enumerated the same result>

### RMC only (check for hypothesis bias)
<claims RMC enumerated that AG did not — candidates for scrutiny>

### AG only (candidates for addition)
<claims AG enumerated that RMC did not — candidates for wiki addition>

### Confidence disagreements
<claims both enumerated but at different confidence levels>
```

### Step 3 — Human-guided adjudication

Present the diff to the human. Work through each divergence **one at a time**.

For each item, present:
- The claim statement
- The supporting quotation(s)
- Why each agent included or excluded it
- Proposed resolution

Wait for human decision before presenting the next:
- **Accept (RMC version)** → enters final claim document
- **Accept (AG version)** → enters final claim document
- **Accept (revised)** → human edits; revised version enters document
- **Reject** → discarded; optionally noted in structural gaps
- **Flag for further AG scrutiny** → enters `syntheses/conjectures.md`

Do not batch decisions. One claim at a time.

### Step 4 — Write final claim document

After all divergences are adjudicated, write to `claims/<source>-claims.md` in the brief root:

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

### Step 5 — Update prefix registry

Update `claims/_index.md`:

```markdown
## Prefix Registry

| Prefix | Source | File | Adjudicated |
|---|---|---|---|
| <PREFIX> | <Author Year Title> | [[<source>-claims]] | <YYYY-MM-DD> |
```

### Step 6 — Log and report

Append to `log.md`:
```
## [<YYYY-MM-DD>] claim-adjudicate | <Author Year> — <Title>
Claims accepted: <N>. Rejected: <N>. Flagged for AG: <N>.
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
