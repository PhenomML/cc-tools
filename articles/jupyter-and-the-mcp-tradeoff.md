# Jupyter and the MCP Trade-off

Jupyter notebooks occupy an unusual place in research computing. They are not static
documents — they are computations. A notebook without its outputs is a script; a notebook
with its outputs is a record of what happened when that script ran against specific data.
The outputs are the point.

This distinction matters when you are asking an AI agent to work with notebooks. The
right approach depends on what you need the agent to see.

## What static conversion gives you

The simplest path: execute the notebook in your own environment, convert it to markdown,
hand the result to the agent.

```bash
jupyter nbconvert --to notebook --execute notebook.ipynb --output executed.ipynb
cc-nbconvert --to markdown executed.ipynb --stdout
```

This gives the agent the complete notebook as readable text: all code cells, all outputs,
all markdown narrative, in order. For the majority of research use cases, this is
sufficient.

The agent can read a regression table, interpret a plot description, follow a derivation,
summarize the analysis, identify where assumptions may be violated, suggest follow-on
analyses. The `/notebook-narrate` skill does exactly this: converts the notebook and
writes a structured research narrative, saved alongside the notebook as a permanent record.

Static conversion has real limits, but they are narrower than they first appear. If the
notebook has already been executed and its outputs are current, you have everything the
agent needs.

## What static conversion misses

Three situations push past what static conversion can provide:

**The notebook is not yet executed.** A fresh notebook with no outputs is an empty shell.
You can execute it yourself and convert — but if the notebook requires interactive
choices, depends on external state that changes between runs, or takes hours to execute,
this gets complicated.

**You need iterative exploration.** Research analysis is rarely a straight path. You want
to try a different lag structure, refit the model with a subset of the data, plot the
residuals against a variable you didn't originally include. This is the natural habitat
of Jupyter: hypothesis, execution, observation, adjusted hypothesis. Static conversion
captures a snapshot; it cannot support the iteration.

**The outputs are dynamic or stateful.** Some notebooks produce outputs that depend on
session state — a model trained in cell 5 that is queried in cell 12. Converting a
partially-executed notebook, or one where cells were run out of order, may give the agent
a misleading picture.

## What the Jupyter MCP provides

The Jupyter MCP server (`uvx jupyter-mcp-server@latest`) gives the agent live, two-way
access to a running JupyterLab instance. The agent can read any cell, write new cells,
execute them, and capture the outputs — interactively, in sequence, in response to what
it observes.

This enables the iterative workflow that static conversion cannot: the agent fits a model,
reads the residuals, writes a diagnostic cell, executes it, reads the output, adjusts the
specification. It is closer to pair programming with a data scientist than to document
analysis.

The MCP server runs via `uvx` in its own isolated environment, separate from the
researcher's conda environment. It communicates with JupyterLab over HTTP. The
researcher's environment, packages, and data remain entirely under the researcher's
control — the agent gets access to the running kernel, not to the environment that
produced it.

## The token cost

Here is the trade-off: MCP servers inject their tool schemas into every Claude Code
session context, whether or not you use them. The Jupyter MCP exposes roughly ten to
twenty tools — execute cell, read cell, write cell, list notebooks, restart kernel, and
others. At one to three hundred tokens per tool schema, you are adding one to four
thousand tokens to the start of every session, in every project, permanently.

For a tool you use in every session, that cost is worth paying. For a tool you use in
one project out of ten, it is not. You are paying the ingestion cost of a service you
are not using.

## The right activation model

Register the Jupyter MCP at the project level, not globally. Claude Code supports a
`.mcp.json` file at the project root that activates MCP servers only for sessions in that
project. The token cost is incurred only where the capability is actually needed.

```json
{
  "mcpServers": {
    "jupyter": {
      "command": "uvx",
      "args": ["jupyter-mcp-server@latest"],
      "env": {
        "JUPYTER_URL": "http://localhost:8888",
        "JUPYTER_TOKEN": "${JUPYTER_TOKEN}",
        "ALLOW_IMG_OUTPUT": "true"
      }
    }
  }
}
```

Add this file to the project root when you need interactive notebook collaboration.
Remove it — or add it to `.gitignore` if the token is personal — when the work is done.

For `JUPYTER_TOKEN`: set a fixed token in `~/.jupyter/jupyter_server_config.py` and
export it from your shell profile once. Then no per-session token management is needed.

```python
# ~/.jupyter/jupyter_server_config.py
c.IdentityProvider.token = 'your-chosen-token'
```

```bash
# ~/.zshrc
export JUPYTER_TOKEN=your-chosen-token
```

## Which to use

| Situation | Approach |
|---|---|
| Notebook already executed, need summary or narrative | `cc-nbconvert` + `/notebook-narrate` |
| Notebook not yet executed, single run sufficient | `jupyter nbconvert --execute` then `cc-nbconvert` |
| Need to explore interactively, try variations, iterate | Jupyter MCP via `.mcp.json` |
| Long-running or stateful computation | Jupyter MCP — static conversion of partial state misleads |

The default is always static conversion. It costs nothing in token overhead, runs without
a JupyterLab instance, and handles most research analysis questions adequately. The Jupyter
MCP is for the cases where the iteration itself is the work — where you need the agent
to think with the data, not just read about it.

---

*The cc-tools repository includes a reference Jupyter MCP config at `mcp/jupyter.json`.
The full toolset, including `cc-nbconvert` and the `/notebook-narrate` skill, is described
in "Make Your AI's Work Permanent."*
