# ADR-0013: Use OpenRouter for opt-in transcription and protect worktree keys

- Status: superseded
- Date: 2026-11-04
- Owner: Project maintainer and implementing agent within task authority
- Evidence: [Issue 101 and plan v1](https://github.com/WilsonLe/agentic-workflows/issues/101), explicitly approved in Codex on 4 November 2026. [Synthetic Editonny verification](https://github.com/WilsonLe/agentic-workflows/issues/97#issuecomment-6623495339) proved the provider and native render boundary.
- Supersedes: none
- Superseded by: 0017

## Context

Video Editing already consumes timed Speech-to-Text output and can hand local
editing to Editonny. A successful synthetic run obtained word timestamps from
OpenRouter and used the native Editonny cut and render gates. It depended on
disposable adapters and a checkout-local key. The shared bootstrap policy calls
for independent secret copies between same-repository worktrees. It has no
executable copy step for this key.

## Decision

Speech-to-Text owns the optional hosted request and the source-linked transcript.
Explicit authorization covers one bounded audio-only request tied to the source
SHA-256 recorded before approval. The client checks a private snapshot against
that hash, sends only audio extracted from it, and keeps the request and response
artifacts private. OpenRouter can route within its service. The client sends one
request without resubmission. After a successful response, the saved receipt
binds its raw SHA-256 to the approved source and uploaded audio. Offline recovery
uses that receipt and publishes a normalized transcript exclusively. Video
Editing owns the local workflow and its native Editonny transcript bridge.
Editonny owns the confirmed project, cut timing, review, caption layout, and
final export checks.

Read the raw key only from the selected checkout's private, Git-ignored
`.cli/openrouter/api-key`. The copy command uses the shared protected-file
controls and verifies that both roots belong to the same Git repository. It
creates an independent destination without replacement and preserves conflicting
keys. Credential use stays explicit per checkout. Other providers retain their
existing bootstrap and rotating-session rules.

## Alternatives

A provider switch inside Editonny would couple upstream project and runtime
state to this suite. Installing a local speech model would conflict with the
requested hosted route. Shared links or a global key search would hide which
account the destination uses and could expose unrelated credentials. Explicit
copying keeps the existing checkout boundary and works with ordinary Git
worktrees.

## Consequences

The existing catalog distributes the portable client, copy command and bridge
under ADR-0011. The OpenRouter route requires a configured key, bounded supported
audio and actual word timestamps. The native bridge is constrained to the
verified upstream contract. Hosted processing is separately authorized from
ordinary editing, and local editing and export checks still apply. Reverting
this integration removes the route without deleting local keys or media.

## Revisit

Reassess when Editonny exposes a supported external transcript import interface,
longer clips establish a tested chunking requirement, or the worktree copy
contract needs a portable owner-only ACL implementation.

On 2026-11-11, [ADR-0017](0017-use-codex-connected-apps-and-retire-project-cli-credentials.md)
replaced this policy under the maintainer's global connected-app and no-project-token-store request.
The rationale above records the earlier choice; current operation and runtime
authentication follow ADR-0017.
