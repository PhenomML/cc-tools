## Standard Toolset (cc-tools)

`cc-tools` is installed on this machine and provides the following commands on PATH:

| Command | Usage | Purpose |
|---|---|---|
| `cc-markitdown` | `cc-markitdown <file>` | Convert PDFs, Office docs, HTML files → Markdown |
| `cc-webfetch` | `cc-webfetch <url>` | Fetch a public URL as clean Markdown (via markdown.new; 500 req/day) |
| `cc-md2pdf` | `cc-md2pdf [-o DIR] [-e ENGINE] file.md ...` | Convert Markdown → PDF via pandoc + XeLaTeX |
| `cc-nbconvert` | `cc-nbconvert --to markdown <notebook.ipynb>` | Convert Jupyter notebooks → Markdown |
| `cc-pdfplumber` | `cc-pdfplumber <file.pdf>` | Extract tables and text from PDFs |

`cc-md2pdf` requires `pandoc` (system package, not uv): `brew install pandoc`. LaTeX engine: use MacTeX if already installed; otherwise `brew install --cask basictex` (the two conflict). Preprocesses `<details>`/`<summary>` HTML blocks into visible text.

**Authoring standard for any `.md` file processed by cc-md2pdf or opened in Obsidian:** use `$...$` for all inline math and `$$...$$` for display math. Inside math delimiters, use LaTeX commands — never Unicode Greek or Unicode subscript digits. Examples: `$\theta_1$`, `$\sigma^2_w$`, `$\hat{x}_{n+1|n}$`, `$\sum_{j=0}^\infty \phi^j w_{t-j}$`. Unicode text outside math (∇, ×, —, ≥ in prose) is fine. Both cc-md2pdf and Obsidian use the same `$...$` syntax, so one source file serves both outputs. See cc-tools `AUTHORING.md` for the full reference.

The `arxiv` Python library is also available for fetching arXiv paper metadata:
```bash
uv run --directory ~/Projects/PhenomML/cc-tools python
```

## Jupyter and notebooks

For most notebook work, use the shell execution pattern — no MCP overhead:
```bash
jupyter nbconvert --to notebook --execute notebook.ipynb --output executed.ipynb
cc-nbconvert --to markdown executed.ipynb --stdout
```
This executes the notebook in the researcher's Conda environment and gives Claude the
full output as markdown.

For **interactive** notebook work (writing new cells, testing hypotheses iteratively),
the Jupyter MCP server (`uvx jupyter-mcp-server@latest`) provides two-way access but
adds ~1,000–4,000 tokens to every session context. Activate it project-scoped rather
than globally: add a `.mcp.json` at the project root (see cc-tools `mcp/jupyter.json`
for the config template). It is never registered globally.

## Research Skills

The following slash commands are installed in `~/.claude/commands/` and available in any session:

| Skill | Usage | Purpose |
|---|---|---|
| `/arxiv-search` | `/arxiv-search time series forecasting` | Search arXiv and summarize top results |
| `/paper-summary` | `/paper-summary path/to/paper.pdf` | Extract and summarize a research paper |
| `/notebook-narrate` | `/notebook-narrate path/to/analysis.ipynb` | Write a research narrative from a Jupyter notebook |
| `/math-review` | `/math-review path/to/notes.md` | Check .md files against the $...$ authoring standard |
| `/wiki-ingest` | `/wiki-ingest raw/paper.pdf` or `/wiki-ingest 2301.07608` | Ingest a source into the research wiki (multi-wiki routing) |
| `/wiki-query` | `/wiki-query <research question>` | Answer a question by synthesising across wiki pages |
| `/wiki-lint` | `/wiki-lint` or `/wiki-lint tsa` | Health-check wiki for orphans, broken links, stale pages |
| `/wiki-project` | `/wiki-project ../MyProject` | Add or update a project page in the wiki |

Skills are symlinked from the cc-tools repo — they update automatically on `git pull` without re-running setup.

## Research Wiki

Wiki skills follow the Karpathy LLM wiki pattern, adapted for multi-subfield research:
a shared `raw/` directory holds source PDFs (local only, never committed); individual
sub-wikis (`tsa/`, `bayes/`, etc.) hold Claude-maintained markdown pages. A paper
spanning multiple subfields is written into all relevant sub-wikis. Projects are
registered in the wiki with relative filesystem paths; the project repos carry no
wiki content.

To initialise a new wiki, copy `templates/wiki-CLAUDE.md` from the cc-tools repo to
your wiki root and edit the sub-wiki table to match your research domains.

Source and full docs: https://github.com/PhenomML/cc-tools

To update cc-tools after a `git pull`:
```bash
cd ~/Projects/PhenomML/cc-tools && git pull && uv tool upgrade cc-tools
```

## Environment Notes

- Research project dependencies are managed with **Conda** — do not use uv for researcher projects.
- `uv` is for Claude's own tooling only, installed at `~/.local/bin/uv`.
- GitHub access uses SSH (`git@github.com`) and the `gh` CLI under the `adonoho` account.
