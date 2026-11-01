# ADR-0007: Provision native browser MCP from app-provided desktop context

- Status: accepted
- Date: 2026-11-01
- Owner: Project maintainer and implementing agent within task authority
- Evidence: User explicitly requests a current-build solution, repository implementation and local activation for iOS Remote tool/permission parity; [issue 71](https://github.com/WilsonLe/agentic-workflows/issues/71). Routine implementation/design authority is established by the Standard Development Workflow.
- Supersedes: none
- Superseded by: none

## Context

On the observed macOS desktop build, native CUA is excluded from Code Mode. A
complete explicit native MCP definition fixes discovery, but a real iOS voice
first turn still fails browser access: its inherited generic marker lacks the
desktop's per-chat account association. The host returns false before reading
Work settings, so the resulting Work-settings error is misleading. A native
desktop REPL already contains the app-provided account scope. A real iOS trial
using that same context opened/read/closed a browser tab before the first
automatic desktop resume. These observations motivate an explicit configuration
option; they do not justify relaxing browser policy or fabricating an identity.

## Decision

Extend the existing Codex configuration helper, following ADR-0004's opt-in local
activation and exact backup/restore contract. The new macOS browser option validates
the installed native manifest, OpenAI-signed executables and current-user process
ancestry. It copies one unique account scope verbatim from the selected native
desktop host's REPL context, checking app version, host pipes and Codex home. No
login store or token is read. Unsupported/ambiguous state fails before writes.

Provision only the native CUA connection, exposing it to Code Mode and requiring
startup. Preserve explicit tool/plugin policy and recognized native customizations;
reject conflicting policy layers, disabled tools and unrelated transports. Merge
disjoint per-tool rules without choosing between conflicting restrictions. Retain the original signed browser
runtime and its access preloader. Account matching, signed requests, nonce checks,
Work policy, OS consent and browser-route ownership remain native responsibilities.

Use an internal MCP launcher in the same helper to resolve current native runtime
paths and refresh only the host-instance prefix from the inherited native marker.
That prefix changes on app restart; storing it permanently would be incorrect.
The account/user components remain app-provided and are checked by the native host.
The launcher has no ordinary session-creation, hook or coordination responsibility.
ADR-0006's instruction-only ordinary delegation remains in force. Installation
does not activate the option, and encrypted transfer/schema ownership is unchanged.

## Alternatives

Exposure-only configuration was tested and failed the real browser outcome.
Desktop resume changes startup state and is unsuitable as an acceptance test or
required warm-up for every iOS chat. Navigation did not prove registration, and
an automatic hook would introduce UI effects without solving the demonstrated
contract. A static copied context goes stale after app restart. Login-store/token
decoding would introduce unnecessary sensitive-data access; invented identities,
modified native guards and proprietary binary patches are outside the design.
A separate setup skill would duplicate the existing configuration owner.

## Consequences

The reusable package contains generic code and synthetic tests; generated account
scope and machine paths remain in private local configuration/backups. Explicit
setup requires a normal desktop source context once, an installed native plugin
and cached pinned Python dependencies. Runtime startup does not discover a desktop
REPL or read login stores. A changed account or unsupported native layout fails
closed and requires reactivation. Moving/removing the skill's absolute launcher
path also requires reapplying from the new installed location.

This is a compatibility bridge for a verified current-build startup difference,
not a portable policy override. Actual fresh iOS text/voice browser outcomes and
effective permission readback remain acceptance checks; package parity, synthetic
probes and tool inventory alone cannot establish them. App restart behavior has
targeted lifecycle tests; live restart must respect unrelated active chats.

## Revisit

Remove this bridge when native iOS startup supplies the same browser registration
and tool exposure as desktop. Recheck after native transport/authentication changes,
app updates, plugin relocation or account/workspace changes. Keep exact rollback,
native access checks and opt-in activation through any replacement.
