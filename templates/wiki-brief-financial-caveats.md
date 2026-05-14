# Financial Figure Caveats for Company Briefs

Apply these rules whenever a concept page or synthesis uses financial figures
(valuation, revenue, ARR, growth rate, NRR) in a company brief.

## Two-tier caveat by filing status

First check EDGAR: if the company files a 10-K or 10-Q, it is public; otherwise private.

**Public companies** (10-K / 10-Q on EDGAR): cite the figure, note the filing period
(e.g., "FY2024 10-K"), and flag if it is revenue vs. ARR vs. deferred revenue. No
further caveat needed — EDGAR-filed figures are audited and subject to restatement risk
but are not run-rate estimates.

**Private companies** (no 10-K on EDGAR — press releases, funding announcements,
management commentary): figures are self-reported and unaudited. Add a note: "Figure is
[run-rate / ARR / annualized] as reported by the company; not audited under GAAP."
Company announcements frequently report a single quarter annualized rather than trailing
twelve months — and almost never note the distinction. A reader unfamiliar with this
convention can easily misread run-rate as trailing revenue, overstating actual
performance by 2–4×.

## Cross-company comparisons

When a table or paragraph places a public-company figure alongside a private-company
figure — e.g., "Snowflake NRR 126% (FY2024 10-K) vs. Databricks NRR >140% (company
announcement)" — note the asymmetry at the point of comparison, not only in a separate
caveat block. A reader scanning a table will treat both numbers as equivalent-quality
data unless told otherwise. Example inline note: "Databricks figure is self-reported and
unaudited; Snowflake figure is SEC-disclosed."

## Scope

Do not apply these caveats to non-financial figures (customer counts, product launch
metrics, headcount) — treating every press release citation as suspect trains researchers
to skip past the warning when it actually matters.
