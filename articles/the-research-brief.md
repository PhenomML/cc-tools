# The Research Brief

The research wiki described in ["The Multi-Subject Personal Research Wiki"](https://github.com/PhenomML/cc-tools/blob/main/articles/multi-subject-personal-research-wiki.md) was designed for long-term accumulation: a paper comes in, gets routed into every relevant sub-wiki, updates the concept pages it touches, and the knowledge compounds over months. The trigger is a new source. The timescale is a research career.

Not all knowledge work operates that way.

## The accidental discovery

A Claude instance was given an empty directory, the wiki template, and a time-sensitive prompt: a researcher had a chance to meet Ilya Sutskever and needed background. Without further instruction, Claude read the template, adapted the Sub-wikis table to the subject — biography, research, ai-safety, ventures — fetched sources via `cc-webfetch`, and produced a structured, cross-linked research wiki in a single pass. It then answered the driving question: why would a Stanford signal processing mathematician interest a superintelligence researcher?

This was not the intended use case. What emerged was something faster and more opportunistic: a research brief — structured, citable, and persistent — assembled in minutes from public sources, purpose-built around a specific question.

The output was not a chat summary that disappears into history. It was a wiki: navigable, citable, and still there when the next meeting comes.

## What makes a brief different from a research wiki

A research wiki is domain-organized. Sub-wikis represent research areas: time series analysis, Bayesian methods, scientific computing. Sources are papers, primarily from arXiv. The accumulation is open-ended.

A brief is subject-organized. Sub-wikis represent orthogonal dimensions of a single subject: biography, research, views, ventures for a person; history, products, strategy, team for a company. Sources are the public record: Wikipedia, company sites, interview transcripts, recent news. The brief is purpose-built around a trigger — an upcoming meeting, a new collaborator, an unfamiliar organization — and a driving question that gives the work its focus.

The schema that makes both work is the same. The wiki skills are the same. The difference is the decomposition: what the sub-wikis represent and where the sources come from.

## Subject types and dimensions

The pattern generalizes beyond people:

| Subject type | Sub-wiki dimensions |
|---|---|
| Person | biography, research, views, ventures |
| Company / organization | history, products, strategy, team |
| Conference / event | program, speakers, themes, papers |
| Topic / debate | positions, evidence, key figures, history |
| Policy / legislation | text, sponsors, arguments, status |

The dimensions are not prescribed — they follow from the subject. A person without public ventures gets three sub-wikis instead of four. A company brief for a startup may weight strategy over history. The wiki template is a starting point; the agent adjusts for the subject at hand.

## The `## Purpose` field

Every brief has a Purpose section at the top of its `CLAUDE.md`, above the Sub-wikis table:

```markdown
## Purpose

**Subject:** Ilya Sutskever (person)
**Created:** 2026-04-26
**Occasion:** Upcoming meeting
**Question:** Why would a Stanford signal processing mathematician interest
a superintelligence researcher?
```

The Purpose field does three things. First, it focuses the initial ingest — sources are selected and concept pages are written with the driving question in mind, not general coverage. Second, it makes the synthesis page's existence and placement obvious: the brief was built to answer that question, and `syntheses/signal-processing-relevance.md` is where the answer lives. Third, it makes the brief self-documenting when you return to it six months later, when the occasion that motivated it is long past.

## The `/wiki-brief` workflow

Each brief is its own Claude Code session, anchored at the brief's root directory. This matters: Claude's memory is scoped to the working directory of the session that writes it. Running a brief from a parent directory like `~/Research/People/` causes its memory to merge with memory from other briefs in the same parent — each brief should be isolated. Create the directory first, open Claude inside it, then invoke the skill:

```bash
mkdir -p ~/Research/People/ilya-sutskever
# open Claude Code in ~/Research/People/ilya-sutskever/
/wiki-brief "Ilya Sutskever" "Why would Dave's signal processing work interest him?"
```

The skill:
1. Confirms the subject type and sub-wiki dimensions with the researcher
2. Creates `CLAUDE.md` with the Purpose field and Sub-wikis table (skips if already present)
3. Scaffolds the directory structure — sub-wiki directories, `raw/`, `index.md`, `log.md`, `.gitignore`
4. Fetches public sources and saves them to `raw/`
5. Writes initial concept pages, cross-linked across sub-wikis
6. If a driving question was provided, synthesizes an answer and files it in `syntheses/`

The researcher confirms the sub-wiki dimensions at step 1; everything after is automatic. The brief is usable in a single session.

## Lifecycle

A brief passes through recognizable phases.

**Creation.** One session, one command. The agent fetches, synthesizes, and files. The driving question is answered. The brief is complete enough to use.

**Use.** The meeting happens, the conversation occurs. The brief served its purpose.

**Staleness.** Web-sourced content ages. A person takes a new role; a company ships a product; a policy is amended. The `created:` date in the frontmatter is the signal — a brief that is six months old may need a refresh before the next use.

**Refresh.** Run `/wiki-ingest` on new sources — a recent interview, a new press release, an updated Wikipedia article. The agent updates the affected concept pages and logs the ingestion. The brief is current again without rebuilding from scratch.

**Archive.** Some briefs are used once and left. That is fine. A brief that answered its question is worth keeping exactly as it is — a record of what was known at a point in time, for a specific purpose. Unlike a chat summary, it does not need to be re-created.

## How briefs accumulate

Briefs are not isolated artifacts. Filed in a consistent location, they accumulate into something the researcher did not plan for but can navigate:

```
~/Research/
  wiki/          ← long-term research wiki
  People/
    Ilya Sutskever/
    Sam Altman/
  Companies/
    Anthropic/
  Topics/
    EU AI Act/
```

Before a new meeting, check whether a brief already exists. Before a conference, run `/wiki-ingest` on a recent keynote transcript to refresh the speaker brief. A brief built for one question can be queried for a different one — the wiki skills work identically in a brief and in the long-term research wiki.

The `## Purpose` field is what makes an old brief interpretable. Six months from now, the subject directory is not a mystery — the occasion and question that motivated it are right at the top of `CLAUDE.md`.

## The evolution of engagement

Users reach for the brief pattern in three stages.

**Stage one: two triggers.** The long-term research wiki handles papers and domain questions. The brief handles subjects and meetings. The researcher learns to distinguish the trigger and open a session in the right place — `~/Research/wiki/` for accumulation, `~/Research/People/` for a time-sensitive subject.

**Stage two: the collection.** After some months, `~/Research/` is no longer just a folder. It holds profiles on people the researcher has engaged with, companies they've evaluated, policy debates they've tracked. The value shifts from individual briefs to the collection — a navigable record of engagements, with the driving question preserved in each.

**Stage three: cross-pollination.** Insights from a brief begin to inform the long-term wiki. A person brief's analysis of a researcher's technical positions belongs in an `ai-safety/` sub-wiki. A company brief's strategy analysis belongs alongside the papers that define the relevant research agenda. The agent can carry insights across contexts because both use the same schema, the same skills, and the same file conventions.

## Getting started

The brief pattern requires no separate installation. `/wiki-brief` is part of the standard cc-tools skill library.

To build your first brief, create the subject directory, open a Claude session inside it, and run:

```bash
mkdir -p ~/Research/People/subject-name
# open Claude Code in ~/Research/People/subject-name/
/wiki-brief "Subject Name" "Your driving question"
```

The driving question is optional but valuable. It focuses the ingest, produces a synthesis you can act on immediately, and gives the brief a purpose that survives the occasion that created it.

---

*The long-term research wiki that briefs complement is described in ["The Multi-Subject Personal Research Wiki"](https://github.com/PhenomML/cc-tools/blob/main/articles/multi-subject-personal-research-wiki.md). The ingestion tools the wiki skills rely on are covered in ["Help Your AI Read Research — and Remember It"](https://github.com/PhenomML/cc-tools/blob/main/articles/help-your-ai-read-research.md).*
