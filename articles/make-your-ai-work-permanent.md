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
mean. That narrative is saved alongside the notebook. The next person who opens the repo
has the interpretation in hand.

**Project documentation.** An agent reads a codebase and writes the documentation, or
reads meeting notes and writes the decision record. In each case the output is committed.
The repository tells a coherent story over time rather than silently accumulating code
that only the original author understands.

The thread connecting these: **the AI's assessment becomes part of the record.** Not the
chat history. The record.

## The tooling gap

For the pattern to work in practice, the agent needs to operate on real artifacts — PDFs,
notebooks, data files, web pages. Most agents can't do this natively. They can read text
you paste into the context; they can't open a file on disk, fetch a paper from arXiv, or
convert a notebook's outputs to readable text.

The pattern breaks at the ingestion step if the agent doesn't have the right tools.

What a research workflow actually requires:

- **PDF and document conversion** — papers are PDFs; the agent needs them as text.
  `cc-markitdown` handles PDFs, Office documents, and HTML, emitting clean markdown.
- **arXiv access** — most research papers live there before they live anywhere else.
  The `arxiv` library fetches metadata and PDFs by ID or search query, no API key needed.
- **Notebook conversion** — execute a notebook in your own environment, then convert it
  to markdown with `cc-nbconvert`. The agent gets the full output as readable text.
- **Table extraction** — results tables in PDFs lose column structure in naive conversion.
  `cc-pdfplumber` extracts them with layout precision.

These are not exotic requirements. They are the minimum for an agent doing real research
work. They need to be installed, versioned, and consistently available — not improvised
per session.

## A dedicated environment for the agent

The instinct is to install whatever the agent needs into your current project's
environment. This is the wrong instinct.

Your project environments are curated for your research. You want pinned dependencies,
reproducibility, isolation between projects. Every tool you install for the agent's
convenience erodes that discipline. And when you move to a new machine or a new project,
the agent's tools aren't there.

The right model: a dedicated, versioned environment for the agent, installed once per
machine, completely separate from any project environment. The tools live in their own
isolated location; binaries link to PATH; the agent invokes them from any project without
activating anything.

The agent's configuration — what tools exist, how to use them, what conventions to follow
— lives in a global config file that a setup script installs automatically on each
machine. The agent's capability set is consistent everywhere it works.

## Making the tools conversational

CLI tools handle the mechanical work. Skills — version-controlled prompt files that encode
your recurring workflows — make the tools conversational. Four general-purpose research
skills ship with the standard toolset:

- **`/arxiv-search <topic>`** — search arXiv and summarize the top results, with links
- **`/paper-summary <path>`** — read a PDF and produce a structured one-page summary
- **`/notebook-narrate <path>`** — execute a notebook and write a research narrative
- **`/math-review <path>`** — check markdown files against the `$...$` notation standard

Each skill encodes a workflow you'd otherwise describe from scratch every session. They
are symlinked from the toolset repository into the agent's command directory, so they
update automatically when you pull.

## The wiki as natural destination

The natural home for permanent AI work on a research topic is a wiki: a structured,
interlinked collection of markdown files that the agent writes and maintains. Drop a paper
into the source directory; the agent reads it, writes a summary, and updates the concept
pages it touches. Ask a question; the agent synthesizes across everything it has
previously written. The knowledge compounds.

The research wiki — its architecture, its multi-subject structure, and the skills that
maintain it — is the subject of a companion piece. The standard toolset includes full
wiki support; the rationale for why a personal research wiki takes the shape it does
deserves its own treatment.

## The reference implementation

[cc-tools](https://github.com/PhenomML/cc-tools) is a reference implementation of this
pattern for Claude Code. It packages the research tools described above, installs them in
an isolated environment via `uv tool install`, and deploys configuration and skills with
a single setup script. The wiki template and skills ship as part of the standard install.

The pattern itself is agent-agnostic. Every major AI coding agent has analogs for the
global config file, the skill library, and project-scoped service configuration. The
architecture transfers; only the syntax changes.

The article you are reading is itself an example of the pattern: written by Claude,
shaped through conversation, and committed to the cc-tools repository as a permanent
artifact. The next Claude instance that works on this project will find it here.

---

*Companion pieces: "The Multi-Subject Personal Research Wiki" covers the wiki architecture
and the skills that maintain it. "Jupyter and the MCP Trade-off" covers when live notebook
execution is worth its token cost and when shell-based conversion is sufficient.*
