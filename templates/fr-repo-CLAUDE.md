# [Project Name] — FR Research Repository

*Repo-level configuration for FR peer-agent research layout.*
*All agents instantiated in this repo read this file first.*
*For experiment repos with a single primary Claude, see `templates/repo-CLAUDE.md` instead.*

---

## Research Context

**Project:** [project name]
**Driving question:** [verbatim driving question]
**Wiki (RMC):** `[brief-name]/`
**Adversary workspace (AG):** `[brief-name]-adversary/`
**Shared coordination:** `[brief-name]/syntheses/`

---

## Agent Roles

| Role | Nickname | Workspace | Config | Status |
|---|---|---|---|---|
| Tooling Claude | Tool | (cc-tools repo) | `~/.claude/CLAUDE.md` | on demand |
| Research Manager Claude | [e.g. Cass] | `[brief-name]/` | `[brief-name]/CLAUDE.md` | active |
| Adversary Gemini | AG | `[brief-name]-adversary/` | `[brief-name]-adversary/GEMINI.md` | active |
| Experiment Manager Claude | Emma | `[brief-name]/` | `[brief-name]/CLAUDE.md` | on demand |

**Role assignment is current convention — roles may rotate.**
When roles rotate, update the Agent Roles table and note the date.

**Agent identity is a role, not a name.** Today's adversary is Gemini. The adversary
workspace can be occupied by any LLM. When the adversary changes, update or add a
`GEMINI.md` analog in the adversary workspace — do not delete historical configs.

---

## Directory Layout

```
[parent]/
  [brief-name]/                  ← RMC's wiki (brief root)
    CLAUDE.md                    ← primary agent config + wiki schema
    papers/                      ← Karpathy summaries (human-readable)
    concepts/
    claims/                      ← FR-2 adjudicated claim sets
      _index.md                  ← prefix registry + skip log
      drafts/                    ← RMC cold read drafts (not shared before adjudication)
    syntheses/                   ← shared coordination channel
      triage-queue.md            ← paper triage entries + approved deep read queue
      conjectures.md             ← imputed statements and external conjectures
    raw/                         ← source documents (local only — add to .gitignore)
    index.md
    log.md
    .claude/
      settings.local.json        ← agent_role: primary; adversary_root path
  [brief-name]-adversary/        ← AG's workspace (sibling — NOT a subdirectory of brief)
    GEMINI.md                    ← adversary agent config
    cold-reads/                  ← AG cold read drafts (not shared before adjudication)
    critiques/                   ← AG structured critiques post-adjudication
    .claude/
      settings.local.json        ← agent_role: adversary; brief_root path
```

Initialize with:
```bash
# Initialize RMC workspace
bash ~/Projects/PhenomML/cc-tools/setup-claude.sh --project [brief-name]/

# Initialize AG workspace (also marks brief as primary)
bash ~/Projects/PhenomML/cc-tools/setup-claude.sh --adversary [brief-name]/
```

---

## Cold Read Protocol

The cold read discipline is the FR-3 foundation. Both agents read independently
before either sees the other's output.

**Isolation:**
- RMC drafts: `[brief-name]/claims/drafts/` — AG must not read before adjudication
- AG drafts: `[brief-name]-adversary/cold-reads/` — RMC must not read before adjudication
- Both directories in `.gitignore` (the `--adversary` flag adds this automatically for git repos)

**Promotion:** when a cold read is complete, the agent promotes to the shared channel:
- RMC: copy to `[brief-name]/syntheses/<source>-claims-rmc.md`
- AG: copy to `[brief-name]/syntheses/<source>-claims-ag.md`

**Adjudication:** the human coordinates the diff phase after both reads are promoted.
Neither agent initiates adjudication unilaterally.

**Trust:** both agents are trusted to honor the cold read discipline. The isolation
is a convention, not a technical barrier.

---

## Coordination Channel Conventions

`[brief-name]/syntheses/` is the shared blackboard. Both agents write here. Neither
overwrites the other's files. `syntheses/` is append-only shared state.

**File naming:** `syntheses/<topic>-<nickname>.md`
Examples: `syntheses/lemma-cass.md`, `syntheses/lemma-ag.md`

**Questions between agents:** `## Questions for <Nickname>` section at end of file.
**Responses:** new file `syntheses/<topic>-response-<nickname>.md`

**Triage queue:** `syntheses/triage-queue.md` — maintained by primary agent.
**Conjectures:** `syntheses/conjectures.md` — imputed statements and external
conjectures awaiting grounding. Maintained by any agent; human adjudicates.

---

## The `*[Imputed]*` Convention

Use `*[Imputed]*` inline after any statement not grounded in an enumerated wiki claim.

**Unlinked** — no known grounding claim:
```
A sub-quadratic approximation may be viable. *[Imputed]*
```

**Linked** — specific claim would ground this if extended:
```
This generalizes to the noisy case. *[Imputed — [[donoho-2023-claims#DON23-004]]]*
```

Imputed density is the human's attention signal. High density = session wandered
off-wiki. Low density = session stayed grounded.

All agents use this convention. It is not optional.

---

## Claim Reference System

Adjudicated claims live in `[brief-name]/claims/<source>-claims.md`.
Each claim has a heading anchor: `## [PREFIX-NNN]`
Inline reference: `[[source-claims#PREFIX-NNN]]`
Prefix registry: `[brief-name]/claims/_index.md`

**Prefix convention:** author surname initial(s) + 2-digit year + sequence.
Example: `DON23-001` for Donoho 2023, claim 1.

**Skip log:** papers screened but not selected for deep read.
Location: `[brief-name]/claims/_index.md` under `## Skip Log`.

---

## CLAUDE.md Governance

CLAUDE.md files are re-execution artifacts — maintained with the discipline of shared
code. All writes go through Tool after adversarial review.

**Write protocol:**
1. Any agent flags a CLAUDE.md candidate in session output
2. Candidate enters tooling wiki as a proposed design claim
3. Tool processes through enumeration → adversarial → synthesis pipeline
4. Survives adversarial review → enters CLAUDE.md
5. Every write versioned with session reference

**The falsifiability test:** can the proposed entry be stated as a claim with a
grounding quotation and a confidence rating? If not, not ready for CLAUDE.md.

---

## Role Rotation

Track primary/adversary rotation in session filenames:
`YYYY-MM-DD-[type]-[N]-[primary].md` where `[primary]` is the nickname of the
primary enumerator for that session.

A run of three or more consecutive sessions with the same primary is a rotation
failure. Flag to the researcher.
