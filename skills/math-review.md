Review the file(s) at: $ARGUMENTS

Check for violations of the PhenomML math authoring standard (see AUTHORING.md in the cc-tools repo). The rule: all mathematical expressions must be inside $...$ (inline) or $$...$$ (display) with LaTeX commands inside — never bare Unicode math characters.

Flag each of the following, with line number and a suggested fix:

1. **Bare Unicode Greek in math context** — θ, σ, φ, β, γ, μ, ρ, λ, α, ε, δ, η, κ, π, τ, ω, Σ, Φ, Γ, Ω, Λ used as mathematical variables outside $...$
   Fix: replace with $\theta$, $\sigma$, etc.

2. **Unicode subscript/superscript digits** — ₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹ used in math notation
   Fix: replace with $x_{1}$, $x^{2}$, etc.

3. **Unicode combining characters for hats/tildes** — â, β̂, x̂, ê (Unicode combining hat U+0302) rather than $\hat{a}$
   Fix: replace with $\hat{\beta}$, $\hat{x}$, etc.

4. **Math expressions without delimiters** — expressions like x_t, w_{t-1}, sigma^2 written as plain text
   Fix: wrap in $...$

5. **GitHub inline math subscript conflict** — inline `$...$` expressions where `_` (subscript) is followed by additional content before the closing `$`, or where multiple subscripted inline math blocks appear on the same line. GitHub's Markdown parser treats `_` as italic markers before the math renderer runs, breaking the block and italicising surrounding text.
   Fix: convert to display math `$$...$$`.
   At-risk patterns: `$\hat{w}_t^2$`, `$\sum_{h=1}^H ...$`, `$\nabla^d x_t$` alongside other subscripted expressions on the same line.
   Safe inline: bare subscripted variables like `$x_t$`, `$\sigma_w^2$`.

Do NOT flag:
- Unicode used in prose (∇ as a name, ×, —, ≥, ∞, → in non-math context)
- Correctly formatted $...$ math, even if it contains Unicode inside (though LaTeX commands are preferred)
- Code blocks (backtick or indented)

After listing violations, offer to apply the fixes automatically.
