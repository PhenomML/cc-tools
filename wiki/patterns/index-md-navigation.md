---
title: "INDEX.md + cc-wiki-grep Navigation Pattern"
type: pattern
wikis: [cc-tools]
sources: []
related: []
created: 2026-06-15
updated: 2026-06-15
confidence: medium
---

## Pattern

Maintain `INDEX.md` at the wiki root as a one-line-per-page greppable tag index. Use
`cc-wiki-grep` for section-aware extraction. Load INDEX.md first (small), then read only
the section needed — never load full pages unless the whole page is required.

```bash
grep "#tag" INDEX.md                              # find pages by topic
cc-wiki-grep "term" .                             # search with section context
cc-wiki-grep --section "Results" papers/foo.md   # extract one section
cc-wiki-grep --frontmatter papers/               # all paper metadata at once
```

Entry format: `- [slug](path) #type #topic-tag — one sentence`

## Motivation

Session start requires orientation without loading the full wiki into context. Blind
`find` calls return filenames but not relevance. Full-page reads load content that isn't
needed. INDEX.md + cc-wiki-grep provides a two-step path: identify the right page cheaply,
then extract only the relevant section.

## Field Assessment (Cass, 2026-06-15)

First real-world evaluation after deploying to the compressed-sensing wiki.

**What works:** Session start orientation. Replaces blind `find` calls with a single cheap
read. Earns its keep for the long tail — finding the right iSATx version or the right
COMM-009 document without scanning 60 filenames.

**Limitations identified:**

1. **Tag taxonomy is rough.** Judgment calls at index-time create latent miss risk. A page
   like `steinsense-computational-profile.md` could plausibly carry `#onsager`,
   `#hardware`, or `#steinsense` depending on what the searcher needs. Tags are a fast-path
   hint, not a guarantee.

2. **High-frequency pages bypass it entirely.** Pages touched in 80% of sessions (patent
   brief, active lemma, current claims document) are already loaded from memory at session
   start. INDEX.md adds nothing for that core set.

3. **Pre-step risk.** If a tag miss forces fallback to `cc-wiki-grep` search, the net cost
   is a pre-step rather than a saving. The pattern only wins when tag lookup succeeds or
   section extraction replaces a full-file read.

**Verdict:** Useful, not transformative. Worth maintaining because the overhead is low —
one line per ingest — but it does not replace reading current brief sections at session
start for high-stakes work.

## Design note

Tag misses are mitigated by the search path: `cc-wiki-grep "term" .` finds the page
regardless of how it was tagged. Tags are a fast-path optimization; the search mode is the
backstop. This lowers the latent miss risk Cass identified, though it doesn't eliminate the
pre-step cost when tags are wrong.

## Maintenance rule

Add one INDEX.md entry per page at ingest time. This is enforced by Step 5b of
`/wiki-ingest` and the Session End checklist in `wiki/CLAUDE.md`.
