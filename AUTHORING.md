# Authoring Guide for cc-md2pdf

Documents processed by `cc-md2pdf` are rendered via **pandoc + XeLaTeX** and are
also intended to open in **Obsidian**. Both pipelines share the same LaTeX math syntax,
so a single source file works for both outputs.

---

## Math notation

**Rule: put all mathematical expressions in `$...$` (inline) or `$$...$$` (display).**

Use LaTeX commands inside math mode — never bare Unicode Greek letters or Unicode
subscript/superscript digits inside math delimiters.

### Correct

```markdown
The MA(2) process $x_t = w_t - 0.5 w_{t-1} + 0.25 w_{t-2}$ with $\sigma^2_w = 1$.

$\gamma(0) = (1 + \theta_1^2 + \theta_2^2)\sigma^2_w$

The OLS estimator $\hat{\beta} = (Z'Z)^{-1}Z'Y$ has $\text{Cov}(\hat{\beta}) = \sigma^2(Z'Z)^{-1}$.

ACF decays as $\rho^h$ with $\rho \approx 0.8$.
```

### Incorrect (will silently drop characters or appear as literal text in PDF)

```markdown
The MA(2) process x_t = w_t − 0.5 w_{t−1} + 0.25 w_{t−2} with σ²_w = 1.

γ(0) = (1 + θ²₁ + θ²₂)σ²_w          ← Unicode subscripts ₁ ₂ are absent from most fonts

β̂ = (Z′Z)⁻¹Z′Y                        ← combining-hat Unicode; subscript notation literal
```

### Common LaTeX commands

| Concept | Write | Renders as |
|---|---|---|
| Greek parameters | `$\theta_1$`, `$\phi_2$`, `$\sigma^2_w$` | θ₁, φ₂, σ²_w |
| Hat variables | `$\hat{x}_{n+1\|n}$`, `$\hat{\beta}$` | x̂_{n+1\|n}, β̂ |
| Summation | `$\sum_{j=0}^\infty \psi_j w_{t-j}$` | Σ expression |
| Fractions | `$\frac{1}{12}\sum_{h=0}^{11} B^h$` | fraction |
| Operators | `$\nabla^2 x_t$`, `$B^{12}$` | ∇²xₜ, B¹² |
| Distributions | `$\varepsilon \sim \text{iid } N(0,\sigma^2)$` | ε ~ iid N(0,σ²) |
| Named functions | `$\text{Cov}(\hat{\beta})$`, `$\text{SE}(r_h)$` | Cov(β̂), SE(rₕ) |
| Mod operator | `$s_{t \bmod 12}$` | s_{t mod 12} |
| Inequality | `$0 \leq \alpha_1 < 1$` | 0 ≤ α₁ < 1 |
| Chi-squared | `$\chi^2(H-p-q)$` | χ²(H−p−q) |

### GitHub rendering

GitHub's Markdown parser processes `_` (italic marker) before the math renderer processes `$...$` delimiters. **Inline math containing `_` where content follows the subscript before the closing `$` is a GitHub rendering risk** — the `_` is consumed as an italic marker, breaking the math block and italicising the surrounding text.

**Rule:** Any inline math more complex than a bare subscripted variable should use display math `$$...$$`.

| Expression | Inline `$...$` | Action |
|---|---|---|
| `$x_t$`, `$\sigma_w^2$` | ✓ safe | keep inline |
| `$\hat{w}_t^2$` | ✗ GitHub fails | use display math |
| `$\nabla^d x_t$` on a line with other subscripted math | ✗ GitHub fails | use display math |
| `$\sum_{h=1}^H \hat{\rho}^2(h)/(n-h)$` | ✗ GitHub fails | use display math |

Obsidian and cc-md2pdf render all inline math correctly; this limitation is GitHub-specific. When in doubt, display math is also better typography for any expression beyond a simple variable.

GitHub introduced a backtick workaround in May 2023 — `$`\hat{w}_t^2`$` — that passes inline math through the Markdown parser intact. It is documented here for reference only. **Do not use it in generated content:** it renders as code in Obsidian and other local viewers. Display math is the correct cross-platform fix.

### Why this matters

| Element | XeLaTeX (PDF) | Obsidian |
|---|---|---|
| `$\theta_1$` | ✓ proper math | ✓ MathJax |
| Unicode `θ` in text | ✓ (TeX Gyre Termes font) | ✓ |
| Unicode subscript `₁` (U+2081) | ✗ silently dropped | displays literally |
| `_t` in text mode | appears as literal `_t` | displays literally |
| `$...$` inline math | ✓ | ✓ MathJax |
| `$$...$$` display math | ✓ | ✓ MathJax |

**The `$...$` format is the intersection.** It is the only notation that renders
correctly as typeset math in both outputs.

Unicode text *outside* math is fine in prose: ∇ (as a name), ×, —, ≥, ∞.

---

## Collapsible answer blocks

Use HTML `<details>`/`<summary>` for instructor answer keys:

```markdown
<details>
<summary>Answer</summary>

**FALSE.** The PACF cuts off after lag p for AR(p); the ACF tails off.

</details>
```

- **PDF**: `cc-md2pdf` preprocesses these into visible bold text (`**Answer:**` heading
  followed by the content). Students receiving the PDF see all answers.
- **Obsidian**: renders as a native collapsible section — click to reveal. Useful for
  self-study.

If you want a student-facing PDF with no answers, generate a separate student `.md` file
that omits the `<details>` blocks entirely.

---

## Blockquote answers (fill-in-the-blank)

For short answers in Problem 2–style questions, use a Markdown blockquote immediately
after the blank:

```markdown
$\psi_j =$ \_\_\_ for $j = 0, 1, 2, \ldots$

> **$\psi_j = \phi^j$.**  
> From $x_t = (1 - \phi B)^{-1} w_t = \sum_{j=0}^\infty \phi^j w_{t-j}$.
```

Blockquotes render as indented text in both PDF and Obsidian.

---

## General tips

- **Blank lines for student space**: use `&nbsp;` on its own line between questions.
  Renders as a blank line in PDF; harmless in Obsidian.
- **Horizontal rules**: `---` between questions creates a visible separator in both outputs.
- **Bold answers**: wrap key numerical answers in `**...**` so they stand out in the PDF.
- **Avoid Unicode combining characters** for hats/tildes (â, β̂, ê): use `$\hat{a}$`,
  `$\hat{\beta}$`, `$\hat{e}_t$` instead.
