# The Authenticated Fetch Gap: An Opportunity for Apple

## The Harm — Today, at Scale

AI agents are accessing authenticated web content — paywalled journalism, institutional
research, personal dashboards — through mechanisms that grant full session access to
extract a single page.

Enabling "Allow JavaScript from Apple Events" in Chrome grants any process on the machine
the ability to drive the browser as the authenticated user in any open tab. Banking
sessions, email, OAuth tokens — not scoped, not auditable, not revocable. The permission
is blanket and machine-wide.

The structural failure is identical in every workaround: **the AI agent receives the
ability to act as the authenticated user across every open tab, when it needs the content
of one page.**

This is not a future risk. Microsoft's Playwright ships as a Model Context Protocol
server with first-class support in Claude Code, VS Code, Cursor, Windsurf, and most major
AI coding environments. Its Browser Extension mode connects to the user's running Chrome
instance and inherits every authenticated session in every open tab — banking, email,
OAuth tokens, subscriber content — not just the page the AI agent requested. With 31.7K
stars and growing adoption across the AI tooling ecosystem, the wrong abstraction has
arrived.

## Why Apple

Apple's privacy model already handles this correctly for every system capability: TCC
gating, process isolation, credential custody in the Secure Enclave. Microphone, camera,
contacts — the user grants access explicitly and can revoke it at any time.

The Chrome workaround bypasses all of it. Effective, but fraught. The ask is to extend
the model Apple has already built to cover authenticated web content.

## The Right Abstraction — Already Mostly Built

`SFSafariViewController` already isolates credentials — the host application cannot read
cookies, inject JavaScript, or observe the session. Reader View already extracts clean
readable content from any page. **The AI agent should receive the content, not the
session.** `SFAuthenticatedFetch` combines both under TCC gating. The missing piece is
the combination, not the technology.

## The Developer Story

Today, fetching public web content for AI agents requires a third-party service —
markdown.new extracts clean content from any URL but carries a 500-request daily limit.
`SFAuthenticatedFetch` on public pages eliminates that dependency: Reader View extraction,
on-device, no rate limit, no external service. For authenticated pages, the same API adds
credential isolation. One interface, both cases, nothing leaving the device.

## Why Now

If Apple does not define the right abstraction before these workarounds calcify into
de facto standards, the opportunity to offer a safer pattern closes. The window is not
approaching — it is open right now.
