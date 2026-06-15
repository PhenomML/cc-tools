---
title: "Recursive Language Models"
type: paper
wikis: [papers]
sources: [../../raw/zhang-2025-recursive-language-models.md, ../../raw/pdf/zhang-2025-recursive-language-models.pdf]
related: []
created: 2026-06-15
updated: 2026-06-15
confidence: high
fetch_provenance: "PDF+markitdown | cc-markitdown raw/pdf/zhang-2025-recursive-language-models.pdf | 2026-06-15"
fetch_note: "cc-arxiv --src failed (tex4ht exit code 1, pandoc fallback produced 36-line stub). Issue #42 filed. PDF conversion usable from line ~100."
---

# Recursive Language Models

Zhang, Kraska, Khattab (2025). arXiv:2512.24601v3. MIT / Stanford.

## Research question

Can LLMs process arbitrarily long prompts without compaction, by treating the prompt as part of an external environment rather than feeding it directly into the context window?

## Core idea: the REPL as prompt environment

An RLM wraps a base LLM $M$ with a Python REPL. The user prompt $P$ is stored as a REPL variable — not in $M$'s context window. At each iteration, $M$ sees only constant-size metadata about the prompt (length, short prefix) and writes code to peek into, decompose, and recursively invoke itself over slices of $P$.

Three design choices distinguish RLMs from prior scaffolds (CodeAct, sub-agent delegation):

1. **Symbolic handle to $P$** — the prompt lives in the environment, not the context window. This breaks the compaction bottleneck entirely.
2. **Programmatic output** — results are stored as REPL variables, not verbalized autoregressively; outputs can be arbitrarily long.
3. **Symbolic recursion** — code inside the REPL can invoke the sub-LM in loops, enabling $\Omega(|P|)$ or $\Omega(|P|^2)$ semantic work over the prompt.

Only stdout metadata (truncated) is appended to $M$'s history — this is what prevents context pollution across iterations.

## Evaluation

Four tasks with different complexity scaling:

| Task | Complexity | Length |
|---|---|---|
| S-NIAH | $O(1)$ — needle constant | up to $2^{20}$ tokens |
| BrowseComp-Plus (1K docs) | $O(1)$ documents needed | 6M–11M tokens |
| OOLONG | $O(n)$ — every line needed | 131K tokens |
| OOLONG-Pairs | $O(n^2)$ — all pairs needed | 32K tokens |
| LongBench-v2 CodeQA | fixed file count | 23K–4.2M tokens |

Baselines: base model, CodeAct (+BM25, +sub-calls), compaction agent, OpenCode, Claude Code (Opus 4.1 + Claude Code v2.0.0).

## Key results

- **Median +26% over compaction** (GPT-5); **+130% over CodeAct with sub-calls** (GPT-5); **+13% over Claude Code** (median across benchmarks).
- On OOLONG-Pairs (quadratic complexity), base GPT-5 and Qwen3 score ≤0.1% F1; RLM(depth=1) scores 58.0% and 23.1% respectively.
- Costs comparable to or cheaper than baselines — recursive sub-calls often cheaper than ingesting the full prompt.
- **RLM-Qwen3-8B:** fine-tuned on 1,000 trajectories; +28.3% median improvement over base Qwen3-8B; approaches vanilla GPT-5 on three of four tasks.

## Key observation about Claude Code

Claude Code (+ context offloading) is the closest comparable to an RLM(depth=0) — both offload the prompt to the filesystem rather than the context window. On CodeQA, Claude Code with offloading scores 62.0 vs RLM(GPT-5, depth=1) at 64.0 — essentially comparable on $O(1)$ tasks. The gap opens on information-dense tasks (OOLONG, OOLONG-Pairs) where recursive sub-calling is needed.

## Relevance to cc-tools

The wiki-as-active-memory architecture in cc-tools is a manual, human-mediated version of the RLM pattern: relevant memory files are loaded selectively rather than feeding everything into one context window. Key parallels:

- **Symbolic handle to context** — `wiki/memories/`, `MEMORY.md` index, and selective `Read` calls are the human-readable equivalent of the REPL variable
- **Constant-size metadata first** — session start reads `ORIENTATION.md` (metadata) before loading specific wiki pages (content slices)
- **No compaction** — the goal of this wiki architecture is to avoid compaction by keeping context organized externally

The paper validates the intuition: compaction loses information that dense-access tasks need. The wiki-as-memory approach is the right direction; the paper suggests that infrastructure (not just conventions) is needed to make it reliable at scale.

## Limitations

- Recursive depth adds latency (all LM calls are sequential in their implementation)
- On simpler tasks (CodeQA, S-NIAH), RLM provides modest gains over plain context-offloading agents
- Post-training results are at small scale (8B); applicability to larger models needs study
- REPL environment introduces security considerations for production deployment
