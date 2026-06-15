---
promoted_from: private memory (project_markdownnew_bug.md)
promoted: 2026-06-15
status: workaround shipped; upstream unresponsive
---

# markdown.new CF-to-CF Bug

**Issue filed:** 2026-05-04 on markdown-new/url-to-markdown-skill issue #1  
**Title:** "Cloudflare-to-Cloudflare blocking: markdown.new cannot fetch CF-protected sites (e.g. Google Scholar)"  
**Status:** OPEN, 0 comments as of 2026-06-15. No response from markdown.new team in 42 days.

## Root cause

markdown.new runs on Cloudflare Workers. CF bot-protection on other CF-hosted sites (Google Scholar, Semantic Scholar) blocks requests from known CF Worker IP ranges. Structural incompatibility — not a transient rate limit.

## Resolution

`_KNOWN_CF_BLOCKED` list in cc-webfetch skips markdown.new for these domains. Cross-referenced as PhenomML/cc-tools#3 (closed). Workaround is in production; we do not depend on an upstream fix.

If the upstream issue ever closes, the `_KNOWN_CF_BLOCKED` workaround in cc-webfetch can be re-evaluated.
