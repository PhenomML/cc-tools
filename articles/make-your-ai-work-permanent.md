# Make Your AI's Work Permanent

Most interactions with an AI agent are ephemeral. You ask a question, you get an answer,
the conversation scrolls away. Even when the answer is good — a careful synthesis of
several papers, a nuanced analysis of a dataset, a well-constructed problem set — it
disappears into chat history. The next session starts from scratch.

There is a better pattern. Instead of asking the AI to *answer*, ask it to *write*.
Commit the output. The work accumulates.

This is the core insight behind Andrej Karpathy's LLM wiki idea, but it extends well
beyond wikis. Once you see it, you find it everywhere.

## The pattern

Ask your AI agent to produce a file. Not a response — a file. A summary page, a problem
set, an analysis narrative, a project brief. Something with a path on disk that can be
version-controlled, shared, searched, and built on in future sessions.

The agent's output becomes a permanent artifact. The next session can read it. So can
your collaborators. So can you, six months later, when you've forgotten what that paper
was about.

A few concrete applications:

**Research knowledge base.** The Karpathy pattern in its original form: the agent reads
papers and writes interlinked wiki pages. Each ingested paper updates a handful of concept
pages, adds a summary to the index, appends a line to the log. The wiki gets richer with
every source. Ask a question today and the agent synthesizes across everything you've read
since the wiki was started — not because it remembers, but because it wrote it down.

**AI-resistant assignment generation.** A statistics course needs problem sets that
students can't trivially solve by pasting into a chatbot. The agent generates problems
using lightly-used datasets — real data from obscure sources that training corpora haven't
memorized. The problems, the datasets, and the solutions are committed to a course
repository. They become a permanent, version-controlled record that can be refined each
term. The AI did the creative work; the commit makes it durable.

**Notebook narratives.** A researcher runs an analysis in Jupyter. The notebook contains
the code and the outputs but not the interpretation. The agent reads the executed notebook
and writes a narrative: what question it addresses, what the methods are, what the results
mean. That narrative is saved alongside the notebook. The next person who opens the repo —
or the same person, eight months later — has the interpretation in hand.

**Project documentation.** An agent reads a codebase and writes the documentation. A
different agent reads meeting notes and writes the decision record. In each case, the
output is committed. The repository tells a coherent story over time rather than silently
accumulating code that only the original author understands.

The thread connecting these: **the AI's assessment becomes part of the record.** Not the
chat history. The record.

## The tooling gap

For the pattern to work in practice, the agent needs to operate on real artifacts — PDFs,
notebooks, data files, web pages. Most agents can't do this natively. They can read text
you paste into the context; they can't open a file on disk, fetch a paper from arXiv, or
execute a notebook and capture its output.

The pattern breaks at the ingestion step if the agent doesn't have the right tools.

What a research workflow actually requires:

- **PDF and document conversion** — papers are PDFs; the agent needs them as text
- **arXiv access** — most research papers live there before they live anywhere else
- **Notebook execution and conversion** — notebooks without outputs reveal little;
  executing them and converting to markdown gives the agent something to work with
- **Table extraction** — results tables in PDFs lose structure in naive text extraction;
  a proper extractor preserves it

These are not exotic requirements. They are the minimum for an agent doing real research
work. But they need to be installed, versioned, and available consistently — not
improvised per session.

## A dedicated environment for the agent

The instinct is to install whatever the agent needs into your current project's
environment. This is the wrong instinct.

Your project environments are curated for your research. You want pinned dependencies,
reproducibility, isolation from other projects. Every tool you install for the agent's
convenience erodes that discipline. And when you move to a new machine or a new project,
the agent's tools aren't there.

The right model: a dedicated, versioned environment for the agent, installed once per
machine, completely separate from any project environment. The tools live in their own
isolated location; binaries are linked to PATH; the agent can invoke them from any
project without activating anything.

The agent's configuration — what tools exist, how to use them, what conventions to follow
— lives in a global config file that a setup script installs automatically on each
machine. The agent's capability set is consistent everywhere.

## Skills: encoding the workflows

Beyond tools, the agent needs to know how to apply them. For the research wiki, that
means knowing what to do when you say "ingest this paper": read it, write a summary page,
update the concept pages it touches, update the index, append to the log.

This workflow lives as a skill — a markdown file that encodes the instructions — committed
to the same repository as the tools. Skills are prompt libraries that travel with the
toolbox. You refine them over time as you learn what works. The agent follows them
consistently across sessions and machines.

For the research wiki, four skills cover the core loop:

- **`/wiki-ingest`** — read a source, write to the wiki, update index and log
- **`/wiki-query`** — synthesize an answer from wiki pages, file valuable results back
- **`/wiki-lint`** — check for orphaned pages, broken links, stale content
- **`/wiki-project`** — register a code project in the wiki with its local path

The assignment generation workflow, the notebook narration workflow, any recurring pattern
of "agent reads X and writes Y" — each is a candidate for a skill.

## On MCP servers

Live service connections (Jupyter MCP, database MCPs, browser MCPs) extend what the
agent can do considerably. They also add thousands of tokens to every session context
whether used or not. For a toolset designed for sustained, focused work, global MCP
registration is the wrong default.

Activate MCP servers project-scoped — a `.mcp.json` at the project root — only for
projects that genuinely need live access. The rest of the time, shell-based execution
(`jupyter nbconvert --execute`, followed by conversion to markdown) gets you most of
what you need at zero ongoing cost.

## The reference implementation

[cc-tools](https://github.com/PhenomML/cc-tools) is a reference implementation of this
pattern for Claude Code. It packages the research tools described above, installs them in
an isolated environment via `uv tool install`, and deploys configuration and skills to the
right locations with a single setup script.

The pattern itself is agent-agnostic. Every major AI coding agent has analogs for the
global config file, the skill library, and the project-scoped service configuration. The
architecture transfers; only the syntax changes.

The article you're reading is itself an example of the pattern: it was written by Claude,
reviewed and shaped through conversation, and committed to the cc-tools repository as a
permanent artifact. The next Claude instance that works on this project will find it here.

---

*A companion piece discusses the multi-wiki pattern for research groups — routing a single
paper into multiple domain sub-wikis from a shared source directory, with projects
registered in the wiki rather than the reverse.*
