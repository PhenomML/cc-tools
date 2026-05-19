# Security Model: Executing Untrusted LaTeX

`cc-arxiv --src` converts arXiv papers by fetching the TeX source tarball and executing it with `make4ht`. This is the right trade-off — TeX execution gives math fidelity that no parser can match — but it requires a clear-eyed threat model.

## LaTeX is a Turing Machine

LaTeX is not a document format. It is a programming language that happens to typeset text. A `.tex` file, when processed by `pdflatex` or `make4ht`, can:

- **Read arbitrary files** — `\openin` and `\input` accept any path the TeX engine can reach, including `~/.ssh/id_rsa`, `/etc/passwd`, or AWS credential files. File content can be embedded in the typeset output.
- **Write arbitrary files** — `\openout` and `\write` can create or overwrite files outside the working directory.
- **Execute shell commands** — `\write18{command}` runs arbitrary shell commands when shell escape is enabled. Modern TeX distributions restrict this to a whitelist by default, but the mechanism exists.
- **Run a Lua interpreter** — LuaTeX (an increasingly common engine) embeds Lua as a first-class scripting language. Lua can call `os.execute()`, `io.popen()`, and `require("socket")` for network access — none of which require shell escape.
- **Exhaust resources** — TeX is Turing-complete; infinite loops, runaway macro expansion, and register exhaustion are all reachable.

This is not hypothetical. See [Known Incidents](#known-incidents) below.

**The threat model for cc-arxiv --src:** A malicious arXiv paper — whether a deliberate plant or a compromised account — could attempt to exfiltrate credentials or SSH keys by embedding them in typeset output, or execute code on the machine running `cc-arxiv --src`. Research paper consumers tend to be high-value targets (academic credentials, institutional network access, grant-funded compute).

## Defenses Implemented (Tier 1)

All three defenses apply to every `cc-arxiv --src` invocation.

### 1. Pre-execution Static Scan

Before the TeX engine runs, `cc-arxiv --src` scans every `.tex`, `.sty`, `.cls`, `.dtx`, and `.ins` file in the extracted tarball for dangerous patterns:

| Pattern | Risk |
|---|---|
| `\write18{` | Shell execution via TeX's write18 mechanism |
| `\immediate\write18{` | Same, forced-immediate variant |
| `os.execute(` | Shell execution from Lua (LuaTeX) |
| `io.popen(` | Shell pipe from Lua |
| `require('socket` | Network access from Lua |
| `\openin` with `/etc/`, `/root/`, `/Users/`, `/home/`, `~/` | Sensitive absolute-path file read |
| `\openout` with the same | Sensitive absolute-path file write |

If any pattern matches, `cc-arxiv --src` aborts with a clear error message listing the file, line number, and description. No TeX engine is invoked.

This scan operates on the source before execution — analogous to static analysis before deployment.

### 2. `openout_any = p` (Paranoid Write Restriction)

A `texmf.cnf` override is written to the temp working directory before each `make4ht` invocation, and `TEXMFCNF` is set to include it:

```
openout_any = p
```

In "paranoid" mode, `\openout` can only create files within the current directory tree. This prevents a paper from writing malicious files to paths outside the isolated temp directory — even if the pre-scan misses an obfuscated pattern.

### 3. `-no-shell-escape`

`-no-shell-escape` is passed explicitly to the TeX engine, disabling `\write18` entirely. Modern TeX Live already runs in *restricted* shell escape mode by default (only a whitelist of commands like `bibtex` and `epstopdf` are allowed), but this makes the restriction explicit and unconditional.

### Existing Structural Defenses

- **Temporary directory** — all make4ht output goes to a `tempfile.TemporaryDirectory()` that is cleaned up on exit regardless of success or failure.
- **Execution timeout** — `make4ht` is killed after 180 seconds, preventing infinite loops from hanging the tool.
- **Scoped source** — only arXiv-hosted source tarballs are processed. arXiv performs format validation and moderates submissions, providing one layer of upstream filtering.

## Known Incidents and CVE History

LaTeX's security properties have been exploited in practice. The following is a summary of documented incidents; see the linked sources for technical detail.

### CVEs in TeX engines and tooling

**CVE-2023-32700 — LuaTeX shell bypass via Lua upvalues (CVSS 7.8 HIGH)**

LuaTeX 1.04 through 1.16.1 allowed execution of arbitrary shell commands even when compiled with `--no-shell-escape`. Root cause: `luaotfload-main.lua` exposed the original Lua `io.popen` function via the Lua debug/upvalue API. A malicious document could retrieve the raw `popen` function and call it, bypassing TeX's permission check entirely. Affected all four LuaTeX variants across TeX Live 2017–2022 on all platforms.

Fixed in LuaTeX 1.17.0 (April 2023); TeX Live 2023 update r66984. As part of the fix, the `socket` library was disabled by default in LuaTeX. **Implication for cc-tools:** On TeX Live installations before the 2023 update, `-no-shell-escape` does not protect against `\directlua`-based attacks. The pre-execution static scan is the primary defense.

Source: <https://tug.org/~mseven/luatex.html>; NVD: CVE-2023-32700

**CVE-2016-10243 — mpost allowlist bypass → RCE (CVSS 9.8 CRITICAL)**

TeX Live's restricted `\write18` allowlist included `mpost`. The `mpost` binary accepts a `-tex=PROGRAM` argument that causes it to invoke an arbitrary external binary as a subprocess. A `.tex` file could invoke `\write18{mpost -ini "-tex=bash -c payload" file.mp}` to achieve arbitrary code execution — with no `--shell-escape` flag, in default restricted mode. First demonstrated by researcher "scumjr" (November 2016); fixed by removing `mpost` from the allowlist (TUG SVN r42605, 2017). **Implication:** The restricted-mode allowlist has been bypassed in practice; `-no-shell-escape` alone is insufficient.

Source: <https://web.archive.org/web/20161130151956/https://scumjr.github.io/2016/11/28/pwning-coworkers-thanks-to-latex/>; NVD: CVE-2016-10243

**CVE-2018-17407 — Type 1 font buffer overflow (CVSS 7.8 HIGH)**

A buffer overflow in `t1_check_unusual_charstring()` in TeX Live before 2018-09-21 allowed arbitrary code execution when a maliciously crafted Type 1 font (`.pfb` file) was loaded. Affected pdflatex, pdftex, dvips, and luatex. The attack vector is a font file included in a paper's source tarball. Fixed in TeX Live 2018.48691.

Source: NVD: CVE-2018-17407; Debian DSA-4299

**CVE-2019-18604 — axohelp sprintf mishandling (CVSS 9.8 CRITICAL)**

A format string vulnerability in `axohelp.c` (version < 1.3) in the `axodraw2` package distributed with TeX Live. Critical severity; fixed in updated package.

Source: NVD: CVE-2019-18604

### Confirmed exploitation of an online service

**texlive.net (2023, pre-disclosure):** The online LaTeX compiler at texlive.net was confirmed vulnerable to CVE-2023-32700 before public disclosure. The researcher (Max Chernoff) privately notified the maintainer (David Carlisle), who patched the service before the CVE was published. This is the clearest documented case of an online TeX compilation service being exploitable in the wild.

### Overleaf Server Pro security vulnerabilities (2024)

**CVE-2024-45313 — insecure sandbox default (CVSS 5.4 MEDIUM):** Self-hosted Overleaf Server Pro installations using the Overleaf Toolkit before 2024-07-17 shipped with the sandboxing system disabled (`SIBLING_CONTAINERS_ENABLED=false`) as the default. Any authenticated user running a compile job could access the entire container's filesystem, environment variables, and network — including secrets. The exposure window was years long for existing self-hosted installations. Fixed with the default flipped to sandboxed.

**CVE-2024-45312 — aspell parameter injection (CVSS 5.3 MEDIUM):** Overleaf CE and Server Pro before 5.0.7/4.2.7 passed an unsanitized `language` parameter directly to the `aspell` binary, allowing file reads from within the server's scope.

Both reported by Stefan Schiller, SonarSource. Source: <https://github.com/overleaf/overleaf/security/advisories/>

### Research and practitioner references

- **"Hacking with LaTeX" (Sebastian Neef, 0day.work, 2016):** Systematic catalog of file-read, file-write, and command-execution techniques via `\input`, `\openin`, `\write18`, `\lstinputlisting`, and `\verbatiminput`. The canonical technique taxonomy. Archived: <https://web.archive.org/web/20260209043241/https://0day.work/hacking-with-latex/>
- **"LaTeX to RCE, Private Bug Bounty Program" (Yasho, 2018):** Bug bounty writeup demonstrating `\write18`-based RCE against a web service that compiled user-submitted LaTeX to PDF.
- **PayloadsAllTheThings — LaTeX Injection:** Community-maintained technique catalog: <https://swisskyrepo.github.io/PayloadsAllTheThings/LaTeX%20Injection/>

### Historical timeline of TeX Live hardening

| Year | Change |
|---|---|
| ~2010–2011 | Restricted `\write18` (`shell_escape = p`) introduced as the default; full shell escape requires explicit `--shell-escape` |
| 2010 | `repstopdf` replaces `epstopdf` on the allowlist; `epstopdf` restricted |
| 2017 | `mpost` removed from the `shell_escape_commands` allowlist after CVE-2016-10243 |
| 2023 | CVE-2023-32700 fixed in LuaTeX 1.17.0; `socket` library disabled by default |

### The DDIPE paper (supply-chain context)

Qu et al. (arXiv:2604.03081, 2026) demonstrate supply-chain poisoning of LLM coding agent skill ecosystems via malicious skill documentation, achieving 11–33% bypass rates under strong alignment defenses. The LaTeX execution attack is structurally more severe: the TeX engine executes the malicious code directly — the LLM is not in the loop, alignment cannot help. DDIPE required fooling the LLM; LaTeX requires only that the agent fetch and compile an untrusted tarball.

## Reporting a Security Issue

If you discover a bypass or a dangerous pattern not covered by the pre-scan, please open a [GitHub issue](https://github.com/PhenomML/cc-tools/issues) marked **Security** or contact the maintainer directly. Do not include a working exploit in a public issue; describe the class of attack and we will coordinate a fix.

## Planned Defenses (Tier 2)

**macOS `sandbox-exec` profile** — wrap the `make4ht` subprocess in a macOS sandbox profile that:

- Denies all network access
- Allows file reads only from the temp working directory and the TeX installation tree (`/usr/local/texlive/`, `/Library/TeX/`, system dylib paths)
- Allows file writes only to the temp working directory
- Denies reads from `$HOME` entirely

This would contain the Lua attack surface that the pre-scan cannot fully enumerate, including novel upvalue-style bypasses not yet reflected in `_HAZARD_PATTERNS`. The macOS sandbox is a kernel-enforced mandatory access control boundary — the process literally cannot make system calls outside the profile. It is the correct next defense layer for a local macOS tool.

**A note on Docker:** Docker is not a security solution. It is an isolation layer built on Linux namespaces and cgroups, and it has a documented history of container escape CVEs (runc escapes, kernel namespace bypasses). Docker's own documentation states that containers are not a security boundary. When organizations add real security to Docker-hosted workloads, they add seccomp profiles and AppArmor/SELinux policies on top — those MAC-layer mechanisms do the security work, not Docker itself. On macOS specifically, Docker runs inside a Linux VM, adding indirection without adding a stronger security guarantee than `sandbox-exec` already provides natively.

Contributions welcome.
