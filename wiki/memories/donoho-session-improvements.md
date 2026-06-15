---
promoted_from: private memory (project_donoho_session_improvements.md)
promoted: 2026-06-15
status: shipped; deferred items abandoned
---

# Donoho Session Improvements — Shipped

Improvements shipped to main (commit 9d763b6) based on feedback from a David Donoho wiki-brief session:

- **cc-webfetch:** Cloudflare block detection (fingerprint + response-size threshold), auto Wayback Machine fallback, clear stderr reporting at each step
- **cc-arxiv:** 429 retry with 10s/20s exponential backoff
- **wiki-brief skill:** raw/-first verification rule — before writing any claim about a third party's actions, relationships, or funding, grep raw/ for their name; disclosure statements in fetched papers are the highest-yield source

## Deferred items — abandoned

- cc-pub-crawl: never reached a second use case beyond HDSR
- Session state scratch file: complexity not justified
- HDSR post-fetch slug awareness: never implemented
