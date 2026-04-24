# The Multi-Subject Personal Research Wiki

A [previous piece](https://github.com/PhenomML/cc-tools/blob/main/articles/make-your-ai-work-permanent.md) introduced the idea of making AI work permanent: instead of asking an agent to answer questions, ask it to write files and commit the outputs. The natural destination for this work, in a research context, is a wiki — the pattern Andrej Karpathy describes in his [LLM wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): a structured, interlinked collection of markdown pages that the agent writes and maintains over time.

This piece is about the shape that wiki should take.

## Why one wiki is not enough

The straightforward implementation is a single wiki directory. All your papers go in,
all your concept pages accumulate in one place. For a tightly focused research program
this works well. For the way most researchers actually think — across multiple methods,
multiple application domains, multiple levels of abstraction — it breaks down quickly.

A paper on the Kalman filter belongs in time series analysis. It also belongs in Bayesian
inference (it is a recursive Bayesian estimator), in state space methods (it is the
canonical example), and possibly in numerical methods (depending on your implementation
interests). In a single wiki, you file it once and build cross-references. Those
cross-references work if you maintain them. In practice, they drift.

The deeper problem is context contamination. When the agent is helping you think about
Bayesian hierarchical models, you do not want it searching through your time series
literature or your teaching notes. A focused context produces focused synthesis. A sprawl
of everything you've ever read produces generalities.

Multiple wikis — one per research domain — solve both problems. A paper gets written into
every sub-wiki it informs. Each sub-wiki has its own index, its own concept pages, its
own focused context. The agent working in one sub-wiki is not distracted by the others.

## The architecture

```
~/Projects/wiki/          ← single git repository
  .gitignore              ← excludes raw/
  CLAUDE.md               ← registry: lists sub-wikis and their scopes
  index.md                ← cross-wiki catalog (agent-maintained)
  log.md                  ← chronological record of all operations
  raw/                    ← source documents — local only, never committed
  tsa/                    ← Time Series Analysis sub-wiki
    CLAUDE.md             ← scope definition for this sub-wiki
    papers/
    concepts/
    methods/
    projects/
    index.md
  bayes/                  ← Bayesian Methods sub-wiki
    CLAUDE.md
    ...
  syntheses/              ← cross-wiki analysis pages
```

The key properties of this structure:

**Shared `raw/`.** Source documents live once, at the wiki root, regardless of how many
sub-wikis they inform. A paper on Kalman filtering has one PDF at `raw/kalman-1960.pdf`.
The agent writes summary pages into `tsa/papers/` and `bayes/papers/`. One source, two
(or more) summaries, no duplication.

**Single git repository.** All sub-wikis share one repo, one `.gitignore`, one commit
history. When a paper update touches concept pages in two sub-wikis, it is one atomic
commit. One repository to clone on a new machine; one backup.

**`raw/` is local only.** Source documents — papers, books, datasets — are frequently
copyrighted. The `.gitignore` excludes `raw/` entirely. The wiki repository contains only
what the agent wrote: summaries, concept pages, cross-links. That content is yours. You
can commit it, share it, publish it, without copyright concern.

## Multi-subject routing

The agent's job when ingesting a source is not just to summarize it — it is to determine
where the summary belongs and write it there.

When you run `/wiki-ingest raw/kalman-1960.pdf`, the agent:

1. Reads the source via `cc-markitdown`
2. Reads the top-level `CLAUDE.md` to understand each sub-wiki's scope
3. Identifies every sub-wiki this source informs
4. Writes a summary page into each — `tsa/papers/kalman-1960.md`,
   `bayes/papers/kalman-1960.md`
5. Updates the concept pages those summaries touch, with cross-links between sub-wikis
6. Updates each sub-wiki's `index.md` and appends to the root `log.md`

You do not file. The agent files, based on content analysis. A paper that spans three
subfields gets written into three sub-wikis in one pass. Cross-links are created
automatically: a concept page in `tsa/concepts/state-space.md` links to
`../../bayes/concepts/gaussian-update.md` when the connection is real.

## The wiki knows about projects; projects don't know about the wiki

Research wikis and code projects are related but distinct. A code project applies methods
and tests hypotheses; the wiki records the understanding that informs those choices. They
should not be coupled.

Project repos carry no wiki content. They do not reference the wiki. They are clean,
shareable, and free of personal research notes that might not be appropriate to publish
or share with collaborators.

The wiki registers projects. Each sub-wiki has a `projects/` directory. A project page
records the project's research goal, a relative filesystem path to the local repo, the
GitHub URL, and links to the papers and concepts that inform it. The agent can navigate
from the wiki to the project directly using the stored path.

```yaml
---
title: Time Series Analysis — Spring 2026
type: project
path: ../../../Projects/TSAnalysis-S26
github: https://github.com/PhenomML/TSAnalysis-S26
wikis: [tsa, methods]
---
```

This one-way relationship has a practical consequence: you can share or publish the
project repo without exposing your personal research wiki. The wiki is yours; the project
is the work product.

## The schema: teaching the agent to be disciplined

The Karpathy pattern's key insight is that the schema — the document that tells the agent
how the wiki is structured and what workflows to follow — matters more than any individual
prompt. A disciplined agent produces a coherent wiki; an undisciplined one produces a mess
that gradually becomes useless.

The top-level `wiki/CLAUDE.md` carries the schema: the sub-wiki table, the page
conventions, the frontmatter format, the math notation standard, the naming conventions.
Each sub-wiki has its own `CLAUDE.md` defining its scope and its relationship to siblings.

A starting template for the schema is at `templates/wiki-CLAUDE.md` in the cc-tools
repository. Copy it to your wiki root, edit the sub-wiki table to match your research
domains, and refine it over time as you learn what produces the most useful pages.

## The wiki skills

Four slash commands maintain the wiki:

**`/wiki-ingest <source>`** — the core ingest loop. Accepts a path in `raw/` or an
arXiv ID (fetched automatically). Reads the source, routes it to the relevant sub-wikis,
writes summary and concept pages, updates indexes, appends to the log.

**`/wiki-query <question>`** — reads relevant pages across sub-wikis, synthesizes an
answer with citations, and offers to file the result as a new page in `syntheses/`.
Valuable answers should not disappear into chat history — filing them back makes them
part of the permanent record.

**`/wiki-lint`** — health-checks the wiki: orphaned pages, broken cross-wiki links,
concepts mentioned but lacking their own page, pages whose content may have been
superseded by more recently ingested sources. Run periodically; the wiki stays coherent
because someone does the maintenance, and that someone is the agent.

**`/wiki-project <path>`** — creates or updates the project page for a code repository,
recording the local path, GitHub URL, and links to the papers and concepts that inform
the project.

## Getting started

1. Create `~/Projects/wiki/` as a git repository
2. Copy `templates/wiki-CLAUDE.md` from the cc-tools repo to `wiki/CLAUDE.md`
3. Edit the sub-wiki table to reflect your research domains
4. Create subdirectories for each sub-wiki, each with its own `CLAUDE.md` defining scope
5. Create `raw/`, add it to `.gitignore`
6. Create empty `index.md` and `log.md` at the root
7. Run `/wiki-ingest` on your first paper

The wiki grows from there. Add sub-wikis as new domains become relevant. The agent learns
the structure from the schema and maintains consistency across sessions without being told
twice.

---

*The tools that support the ingest workflow — `cc-markitdown`, the arXiv library,
`cc-nbconvert`, `cc-pdfplumber` — are part of the standard cc-tools install, described
in ["Make Your AI's Work Permanent"](https://github.com/PhenomML/cc-tools/blob/main/articles/make-your-ai-work-permanent.md).
Live Jupyter notebook execution, when it is needed beyond what `cc-nbconvert` provides,
is covered in ["Jupyter and the MCP Trade-off"](https://github.com/PhenomML/cc-tools/blob/main/articles/jupyter-and-the-mcp-tradeoff.md).*
