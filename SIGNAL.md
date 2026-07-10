# AI for Science: Communication Standard

The cc-tools system rests on three pillars for all AI-generated scientific content: structured documents (Markdown + MathJax), accumulated knowledge (the wiki), and disciplined prose (Shannon + McCloskey). Each pillar addresses a distinct failure mode of the default.

---

## The problem

Language models produce text fluently. Fluency is not precision. The default mode is verbose, hedged, and repetitive — qualities that signal effort while minimizing information density. Scientific communication requires the inverse: maximum information per word, zero redundancy, claims stated as claims.

Reviewing AI output is expensive. Every sentence a reviewer must read to find no new information is waste — waste of the human's time, and evidence that the system is not producing science. These three pillars reduce that waste.

---

## Pillar 1: Markdown + MathJax

All cc-tools output targets `.md` with MathJax math. The choice is structural.

Markdown enforces hierarchy. A document with no headings has no navigable structure; a reader must extract structure from prose flow. Headings are machine-readable and human-scannable; prose is neither. The two-level hierarchy (section, subsection) is sufficient for most scientific documents. Further nesting usually signals a document that should be split.

MathJax enforces precision. Unicode approximations (θ, σ²) resemble mathematics but are not. `$\theta$` and `$\sigma^2$` are parseable, renderable without loss across PDF and web, and unambiguous. The rule: all mathematical content inside `$...$` or `$$...$$`, with LaTeX commands only.

Specification-grade documents — preregistrations, commissions, methods sections — must be sufficient for an independent implementer to reproduce the experiment from the document alone, without reference to code. If a variable is introduced in prose but undefined in math, the specification is incomplete. This is not a style preference; it is a reproducibility requirement.

See `AUTHORING.md` for the rendering specification.

---

## Pillar 2: The wiki

Knowledge accumulates in owned files, not in context windows. Each claim has a source page. Each source page cites a file in `raw/`. Claims the agent cannot ground in an enumerated wiki entry carry `*[Imputed]*`; claims that name a specific gap carry `*[Imputed — [[claim-ref]]]*`, which is a work order.

The wiki answers one question: what does this project know, and how does it know it? An agent that answers from training priors when the wiki has a contrary or more precise claim is producing hallucination with citations deferred. The wiki makes this visible.

The operational discipline: before asserting a domain claim during any session turn, run `cc-wiki-grep` on the relevant term. Cite what you find. If you find nothing, mark the assertion imputed and note the gap.

The `*[Imputed]*` marker enforces epistemic hygiene at the sentence level. A reader can tell, without reading footnotes or weighing hedges, which sentences are wiki-grounded and which are inference. This is the unit of scientific accountability in AI-assisted research.

---

## Pillar 3: Shannon + McCloskey

Claude Shannon showed that information content is the reciprocal of predictability. A sentence that says only what the reader already knows carries no information. Redundancy wastes bandwidth. Deirdre McCloskey showed, in *Economical Writing*, that most academic prose violates this continuously — not from malice but from training on verbose models.

The rules:

**Structure**
- One idea per paragraph. Topic sentence first.
- Definitions precede use. Define once; use the same term throughout.
- Say it once. A sentence that restates the previous sentence should be deleted.

**Sentence level**
- Subject and verb early. "The estimator $\hat{\beta}$ minimizes…" not "It is the case that the minimizer is $\hat{\beta}$…"
- Active voice unless the agent is genuinely unknown or unimportant to the claim.
- Kill nominalizations: "the maximization of $f$" → "maximize $f$"; "the investigation of $X$" → "investigate $X$".
- Kill zombie sentences: "There are three conditions that must hold" → state the conditions.

**Eliminations**
- No throat-clearing: "In this section we will show that…" — show it.
- No content-free hedges: *very*, *quite*, *rather*, *it is worth noting that*, *it is interesting to observe*.
- No *the fact that*: rewrite the sentence.
- No *however* that substitutes for restructuring a paragraph.
- No apology for complexity: if the math is hard, write it correctly; do not apologize in prose.

**The deletion test:** remove the sentence. If nothing is lost, remove it.

---

## How the pillars interlock

Markdown provides the container. The wiki provides the content — which claims are established, with what evidence, at what confidence. Shannon + McCloskey provides the expression standard — how those claims are written.

A wiki page written to standard: each paragraph makes one claim, cites its source, uses active voice and exact mathematical notation. A reviewer extracts the claim in one pass. An agent running `cc-wiki-grep` against the same page gets a high-signal section with no filler to filter.

The `*[Imputed]*` convention closes the loop between Pillar 2 and Pillar 3. It makes the epistemic gap visible in the prose itself — not in a footnote, not in a hedge, but inline, exactly where the inference occurs.

---

## In practice

All cc-tools output — wiki pages, commission documents, synthesis reports, preregistrations — targets this standard. `/shannon` (planned) installs the prose discipline as a session-level skill for Claude agents. `/wiki-upgrade` propagates the structural rules and wiki-access instruction to every agent wiki. `AUTHORING.md` defines the math rendering specification.

The goal is not brevity for its own sake. It is the ratio of information to words. A 200-word section that makes three precise claims, cites each, and defines its terms outperforms a 600-word section that makes the same three claims buried in hedges, repetition, and throat-clearing — for the human reviewer reading it once, and for the agent reading it on every session start.

Science is hard. Prose need not add to the difficulty.
