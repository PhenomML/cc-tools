# Wiki Index

One line per page. Tags are greppable: `grep "#memory" wiki/INDEX.md`, `grep "#paper" wiki/INDEX.md`.
Maintained by convention: add an entry whenever a page is created or promoted.
`raw/` files are not indexed here — they are source material, not knowledge.

## Patterns

- [index-md-navigation](patterns/index-md-navigation.md) #pattern #context-management — INDEX.md + cc-wiki-grep two-step navigation; field assessment by Cass (useful for long tail, not transformative)

## Papers

- [zhang-2025-recursive-language-models](papers/zhang-2025-recursive-language-models.md) #paper #inference #long-context #context-management #claude-code — RLM treats prompt as REPL variable; symbolic recursion outperforms compaction; +13% median over Claude Code on long-context tasks

## Memories (promoted from private)

- [version-policy](memories/version-policy.md) #memory #versioning — cc-tools version bump policy (minor=new tool/skill, patch=bug fix); history table; currently v0.2.0
- [research-memory-isolation](memories/research-memory-isolation.md) #memory #brief-isolation #cc-wiki-brief — per-subject directory pattern; cc-wiki-brief launches Claude from subject dir automatically; resolved
- [markdownnew-cf-bug](memories/markdownnew-cf-bug.md) #memory #cc-webfetch #upstream #cloudflare — CF-to-CF blocking on markdown.new; workaround shipped in cc-webfetch _KNOWN_CF_BLOCKED list; upstream unresponsive
- [icloud-sync-decision](memories/icloud-sync-decision.md) #memory #superseded — iCloud sync for research briefs; question abandoned; wiki-in-repo pattern supersedes it
- [fc2-gate-design](memories/fc2-gate-design.md) #memory #adversarial-pipeline #wiki-claim — Option C five-state adjudication pipeline shipped to /wiki-claim (commit 9c48f9c); routing rules documented
- [donoho-session-improvements](memories/donoho-session-improvements.md) #memory #cc-webfetch #cc-arxiv #wiki-brief — shipped: CF block detection, arxiv retry, raw/-first rule; three deferred items abandoned
- [dd25-adjudication](memories/dd25-adjudication.md) #memory #adversarial-pipeline #wiki-claim — first Option C pipeline run on Dey & Donoho 2025; 24 claims; math fidelity verified; FR-001 lesson
- [cs-onsager-pipeline](memories/cs-onsager-pipeline.md) #memory #adversarial-pipeline #compressed-sensing — completed adversarial pipeline on Onsager Jacobian Lemma; COMM-001R + COMM-002 closed; process lessons
- [transformers-adversary](memories/transformers-adversary.md) #memory #adversarial-pipeline #workspace — transformers-adversary/ scaffold; GEMINI.md is canonical reference for future adversary workspace builds
