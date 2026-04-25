# Help Your AI Read Research — and Remember It

Research literature lives in PDFs. Most of it arrives from arXiv before it lives anywhere else. Before an AI agent can reason about a paper, someone has to get it off the page and into readable text — preserving the math, the tables, and the structure that make the argument followable.

That ingestion step is where most research workflows break down.

## The ingestion problem

A PDF is not text. Naive extraction loses column alignment in results tables, garbles mathematical notation, and strips the structure that makes a paper coherent. An agent handed a badly converted PDF produces shallow summaries at best and confidently wrong ones at worst.

Four tools solve the ingestion problem:

- **[markitdown](https://github.com/microsoft/markitdown)** — converts PDFs, Office documents, and HTML files on disk to clean markdown. The workhorse for local files.
- **[markdown.new](https://markdown.new)** — fetches any public URL as clean markdown via a three-tier pipeline (native markdown → AI conversion → headless browser). The right tool when a paper or document is available at a URL rather than as a local file. 500 requests/day free, no API key.
- **[arxiv](https://github.com/lukasschwab/arxiv.py)** — fetches paper metadata and PDFs from arXiv by ID or search query, no API key required. The agent can retrieve a paper directly from `2301.07608` without a browser step.
- **[pdfplumber](https://github.com/jsvine/pdfplumber)** — extracts tables from PDFs with layout precision. Results tables in papers lose their column structure in naive conversion; pdfplumber preserves it.
- **[nbconvert](https://github.com/jupyter/nbconvert)** — converts executed Jupyter notebooks to markdown, including all outputs. A notebook without its outputs is a script; with outputs it is a record.

These are not exotic requirements. They are the minimum for an agent doing real research reading. They need to be installed once, versioned, and consistently available — not improvised each session.

cc-tools installs these under prefixed names (`cc-markitdown`, `cc-webfetch`, `cc-pdfplumber`, `cc-nbconvert`) to avoid collisions with any versions already in your project environments.

## A call for AI-friendly source formats

The ingestion tools above work around a problem that authors can largely eliminate.

When you submit to arXiv, you submit LaTeX source. ArXiv compiles it to PDF and archives both. The LaTeX source is publicly available for nearly every paper on the platform. `pandoc -f latex -t markdown` converts it to clean markdown with math preserved — `$...$` notation survives the round-trip almost perfectly, because LaTeX already uses it. A reader with the source gets a dramatically better ingestion result than one working from the PDF alone.

The ask is small: **link to your arXiv source, and mention it in your README or repository**. If you distribute a paper alongside code, include the `.tex` files. If you post notes or a preprint, publish the source alongside the PDF.

HTML is the other underused format. Several journals and preprint services offer HTML versions of papers. HTML converts cleanly to markdown, preserves hyperlinks, and handles tables well. When an HTML version exists, it is frequently the best ingestion path — better than either the PDF or the LaTeX source. `cc-webfetch` fetches it directly: `cc-webfetch https://arxiv.org/html/2301.07608`.

The research community has been generating machine-readable source for decades — it just hasn't thought of it in those terms. AI-assisted reading is now a routine part of research workflows. Publishing the source is a small act with compounding benefits for every reader who comes after you, human or otherwise.

## Mathematical notation

Research papers are dense with mathematics. Conversion that survives the notation is essential for the agent to reason correctly about the content.

The standard that works across all tools in this stack is `$...$` for inline math and `$$...$$` for display math, with LaTeX commands inside — never Unicode Greek or Unicode subscript digits. `$\theta_1$` not `θ₁`. This renders correctly in the PDF output from `cc-md2pdf`, in Obsidian's preview, and as readable source text for the agent in the same file.

The `/math-review` skill checks any markdown file against this standard, flagging notation that will render incorrectly in downstream outputs. Run it before filing a summary or committing a page.

## What the agent can do with good ingestion

Once a paper is readable text, the questions you can ask — and get useful answers to — expand significantly.

**Summarize a paper.** The `/paper-summary` skill reads a PDF and produces a structured one-page summary: problem statement, methods, key results, limitations, and relationship to prior work. The summary is written to a file, not the chat window. It persists.

**Search the literature.** The `/arxiv-search` skill queries arXiv for a topic and returns the top results with abstracts and links — a first literature scan without leaving the session.

**Narrate a notebook analysis.** The `/notebook-narrate` skill reads an executed notebook and writes a research narrative: what question the analysis addresses, what the methods are, what the results mean. The code captures the computation; the narrative captures the interpretation.

Each of these is useful in isolation, independent of any larger system. A researcher who wants to quickly assess a paper, survey a subfield, or document an analysis has everything they need at the skill level. The tools do the mechanical work; the skills encode the workflow; the agent provides the reasoning.

## The permanence pattern

There is a further step that multiplies the value of all of this.

Most AI interactions are ephemeral. You ask a question, you get an answer, the conversation scrolls away. Even a careful, nuanced paper summary disappears into chat history. The next session starts from scratch.

The fix is simple: instead of asking the AI to *answer*, ask it to *write*. Commit the output. The work accumulates.

A paper summary written to `papers/kalman-1960.md` is there next session, next month, for your collaborators, for future agents working in the same project. The agent's assessment becomes part of the record — not the chat history, the record.

This is the core insight behind [Andrej Karpathy's LLM wiki idea](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), but it applies to every output the agent produces. Ask for a file. Commit it. The habit is the practice.

## The wiki as amplifier

The permanence pattern produces individual artifacts. The wiki combines them into something that compounds.

Karpathy's pattern: the agent reads a paper, writes a summary page, and updates the concept pages the paper touches — cross-linking the summary to related ideas, appending to the index, logging the ingestion. Ask a question later; the agent synthesizes across everything it has previously written. The knowledge doesn't reset between sessions because it was written down.

The ingestion tools and the wiki pattern were made for each other. `cc-markitdown` gets the paper into readable text. `/paper-summary` produces the summary. Four wiki skills carry it from there:

**Ingest a paper.** `/wiki-ingest` routes a paper into all the relevant sub-wikis, writes a structured summary page, updates the concept pages it touches, and maintains the index. One command does the full filing.

**Query across the wiki.** `/wiki-query` takes a research question and synthesises an answer from everything the agent has previously written — not a web search, but a synthesis of your own accumulated notes.

**Register a project.** `/wiki-project` adds a research project to the wiki, linking it to the papers and concepts that inform it, so the wiki reflects not just what you've read but what you're building.

**Keep the wiki healthy.** `/wiki-lint` checks for orphaned pages, broken links, and stale summaries — the hygiene work that keeps accumulated knowledge navigable as it grows.

The multi-wiki extension — one paper filed into all the sub-wikis it informs, from a shared source directory — is the subject of a companion piece. The key point here is that the wiki is where the permanence pattern reaches its full expression: not a collection of disconnected files, but a structured, interlinked body of knowledge that grows with every paper you read.

## A dedicated environment for the agent

The instinct is to install these tools into whatever project environment is active. Resist it.

Research project environments are curated for reproducibility. Pinned dependencies, isolation between projects, clean conda environments. Every tool installed for the agent's convenience erodes that discipline. And when you move to a new project or a new machine, the tools aren't there.

The right model: a dedicated environment for the agent, installed once per machine, completely separate from any project. The agent's tools live in their own isolated location managed by `uv tool`; binaries link to PATH; the agent invokes them from any project without activating anything.

The agent's configuration — what tools exist, how to use them, what conventions to follow — lives in a global config file that a setup script installs automatically. The agent's capability set is consistent everywhere it works, and it does not touch your research environments.

## The reference implementation

[cc-tools](https://github.com/PhenomML/cc-tools) packages everything described here. It installs the ingestion tools in an isolated environment via `uv tool install`, deploys configuration and skills with a single setup script, and includes the wiki template and wiki skills as part of the standard install.

The pattern itself is agent-agnostic. Every major AI coding agent has analogs for the global config file, the skill library, and project-scoped service configuration. The architecture transfers; only the syntax changes.

---

*Companion pieces: ["The Multi-Subject Personal Research Wiki"](https://github.com/PhenomML/cc-tools/blob/main/articles/multi-subject-personal-research-wiki.md) covers the wiki architecture and the skills that maintain it. ["Jupyter and the MCP Trade-off"](https://github.com/PhenomML/cc-tools/blob/main/articles/jupyter-and-the-mcp-tradeoff.md) covers when live notebook execution is worth its token cost and when shell-based conversion is sufficient.*
