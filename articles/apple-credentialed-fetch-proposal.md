# Credentialed Content Access for Local AI Agents: A Safari API Proposal

## The Problem

Local AI agents — including Apple Intelligence — increasingly need to fetch web content on
behalf of the user. Much of the content users care most about is behind authentication:
paywalled journalism, institutional research access, personal dashboards, subscriber
newsletters. Today, there is no safe, sanctioned way for a local AI agent to retrieve
authenticated content. Developers are working around this absence with mechanisms that are
genuinely dangerous.

The most common workaround on macOS is Apple Events. Enabling "Allow JavaScript from Apple
Events" in Chrome opens a machine-wide remote code execution surface: any process on the
machine can drive the browser and execute arbitrary JavaScript in any open tab — including
tabs with active banking sessions, email, and OAuth tokens. The permission is not scoped to
the requesting application, the requesting domain, or the current session. It is a
blanket capability that cannot be safely left enabled. Developers enable it, do their fetch,
and hope they remembered to disable it. The auto-disable logic we attempted to implement
relies on writing to Chrome's Preferences JSON while Chrome is running — a race condition
with no reliable outcome.

Chrome's DevTools Protocol (CDP) is the other common approach: launch Chrome with
`--remote-debugging-port=9222`, connect over a local TCP port. This is better scoped but
requires the user to close their running browser (profile lock), and exposes a local port
that any process on the machine can connect to for the duration of the session.

Both approaches share the same structural failure: **they give the AI agent access to the
full credential surface, not just the content it needs.** The agent that needs the text of
a Stratechery article also gets, incidentally, the ability to read the user's Gmail, submit
forms on their behalf, and exfiltrate session tokens.

---

## The Abstraction That Is Missing

What is actually needed is a clean separation between:

- **Credential custody** — held by the browser, in the secure credential store, never
  exposed to the requesting application
- **Content delivery** — the rendered text of the page the user authorized, returned to
  the agent

This separation exists in principle in Apple's platform. Face ID/Touch ID separates
biometric data from the application requesting authentication — the app never sees the
fingerprint or face geometry, only a cryptographic confirmation. ASWebAuthenticationSession
handles OAuth flows without exposing tokens to the calling app. SFSafariViewController
renders authenticated content in a Safari-managed view without giving the host app cookie
access.

What does not exist is the equivalent for **content extraction**: a way to say "fetch this
URL using Safari's authenticated session and return me the text, without giving my app
access to the underlying session."

---

## Proposed API: `SAAuthenticatedFetch`

A new system API, scoped to applications that the user has explicitly granted "Authenticated
Web Fetch" access (via a TCC permission — the same model as microphone, camera, and
contacts):

```swift
import SafariServices

// Request authenticated content from a URL
let request = SAAuthenticatedFetchRequest(
    url: URL(string: "https://www.stratechery.com/2026/article")!,
    extracting: .bodyText          // .bodyText | .structuredData | .markdown
)

let result = try await SAAuthenticatedFetch.fetch(request)
// result.content: String — the page's text content
// result.domain: String — confirmed origin
// result.credentialSource: .safariKeychain | .iCloudKeychain | .passkey
// Credentials: never exposed to the calling application
```

The key properties:

**Credential isolation.** Safari performs the fetch inside its own process, using its own
session store. The requesting application receives only the extracted content — never a
cookie, token, or session identifier. The credential surface is strictly smaller than what
the user's browser session already holds.

**TCC-gated, per-application.** The user grants "Authenticated Fetch" to specific
applications in System Settings, the same way they grant microphone access. The grant can
be revoked at any time. A malicious application cannot invoke the API without explicit user
consent.

**Per-domain allowlist.** The application declares in its entitlements or a user-approved
list which domains it may fetch. A research tool that needs Stratechery cannot silently
fetch the user's bank statement. The OS enforces this at the domain level before Safari
ever opens a connection.

**Audit log.** Every authenticated fetch is logged — application, URL, timestamp, content
size — accessible to the user in Privacy & Security settings. The user can see exactly
what their AI agent has been reading on their behalf.

**Content-only extraction.** The API returns rendered text (or structured data, or
markdown), not raw HTTP responses. There is no mechanism for the calling application to
inject JavaScript, read response headers, or observe redirects. The fetch is opaque at the
protocol level.

---

## Why Apple Is Uniquely Positioned

No other platform can build this correctly. The capability requires owning the full stack:

- **Browser + OS + credential store**: Apple controls Safari, WebKit, iCloud Keychain, and
  the Secure Enclave. The credential isolation guarantee is only credible when one vendor
  controls all three layers. A Google API for Chrome-authenticated fetching would be a
  Google API that gives Google visibility into what content users are accessing. Apple's
  privacy posture makes the trust model coherent.

- **On-device AI**: Apple Intelligence runs locally. A credentialed fetch that also runs
  locally — user's content, user's credentials, user's device, never leaving the device —
  is the natural complement. Cloud-based AI assistants (ChatGPT, Gemini) cannot make this
  promise because the content must leave the device to reach them.

- **iOS/iPadOS lock-in**: On iOS, WebKit is the only permitted browser engine. Apple
  already controls the entire authenticated web session for every user on the platform.
  The API already works conceptually — SFSafariViewController proves it. The missing piece
  is content extraction.

- **Regulatory positioning**: The EU AI Act, GDPR, and emerging AI regulation all require
  that AI systems handling personal data provide transparency and control. An OS-level
  authenticated fetch with a per-application TCC grant and a user-visible audit log is the
  compliance answer that no cloud AI provider can match.

---

## The Competitive Landscape Without This API

If Apple does not provide this API, the workarounds will proliferate. Apple Events will
continue to be used — by sophisticated developers who know the security tradeoff and accept
it, and by less sophisticated developers who do not. Chrome's CDP will be used on macOS
where Chrome is the primary browser. Browser automation frameworks (Playwright, Puppeteer)
will ship with persistent-profile modes that inherit credentials informally.

The consequence is that AI agents accessing authenticated content will continue to do so
through mechanisms that expose the full credential surface to the application, with no
audit trail, no user visibility, and no revocation mechanism.

Apple has the opportunity to define the right abstraction before these workarounds
calcify into de facto standards. The moment a major AI framework ships "just use CDP"
as its authenticated fetch story, the window for a better answer closes.

---

## Implementation Considerations

**Phase 1 — macOS, Safari only.** The API fetches through the running Safari process using
its existing session. Content is extracted via WebKit's internal rendering pipeline
(equivalent to `document.body.innerText`, but without the Apple Events attack surface).
No user-visible browser interaction; the fetch is entirely background.

**Phase 2 — iOS/iPadOS.** Identical API; the implementation is simpler because WebKit is
the only engine. The on-device AI use case is strongest here: Siri with authenticated web
access, Apple Intelligence summarizing subscriber content, shortcuts that pull authenticated
dashboards into workflows.

**Phase 3 — iCloud Keychain passkeys.** Extend credential sources beyond Safari session
cookies to include passkey-authenticated sites. As passkeys become the dominant
authentication mechanism, the API's reach grows automatically.

**Entitlement model.** Similar to `com.apple.developer.networking.networkextension`,
authenticated fetch would require a provisioning entitlement from Apple — ensuring that
only reviewed applications can request it, and providing a revocation mechanism if an
application abuses the capability.

---

## Summary

The gap is real, the workarounds are dangerous, and Apple is the only vendor with the
architectural position to close it properly. `SAAuthenticatedFetch` — credential-isolated,
TCC-gated, auditable, on-device — is the privacy-correct answer to a problem that local AI
agents are already solving incorrectly. The question is whether Apple defines the standard
or inherits the mess that fills the vacuum.
