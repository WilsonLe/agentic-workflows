# ADR-0006: Use a portable skill for delegation

- Status: accepted
- Date: 2026-10-31
- Owner: Project maintainer and implementing agent within task authority
- Evidence: User explicitly requested skill-based, harness-agnostic delegation with configured defaults, explicit overrides and one integrated refactoring PR; [tracking issue](https://github.com/WilsonLe/agentic-workflows/issues/69)
- Supersedes: none
- Superseded by: none

## Context

A session was launched with a desktop tool's permissions instead of the saved
configuration. The existing launch contract lived in a Codex configuration-transfer
skill, which made a plain delegation request difficult to discover and mixed task
lifecycle with exporting credentials and activating settings. The user explicitly
requires a portable skill rather than a prompt-injection hook or a global rule.
The expanded request audits every installed feature, permits necessary task helpers,
and preserves automatic session titles as an explicit hook exception.

## Decision

One instruction-only Delegation skill owns ordinary agent/session creation,
configuration inheritance, explicit overrides, effective-setting verification and
handoff/management. The skill is included for Codex, Claude Code and OpenCode V2.
The chosen harness supplies native controls; Codex launch specifics live in one
conditional reference. Move the launch procedure from config transfer and keep a
compatibility link at the former location. The router and delivery/orchestration
workflows refer to the new owner without duplicating its procedure.

For new independent Git sessions, create an isolated worktree by default before
launch, including read-only audits. Explicit directory/lane choices and verified
resumes retain their intended location; native subagents are not silently substituted
for independent sessions. Verify the actual destination and preserve pending source
edits and required local setup.

Use existing generators and package checks. Remove the ordinary workflow-routing
hook and select that workflow through skill metadata. Retain the automatic-title
hook and its supporting code unchanged as the user's explicit exception. Account
for every packaged helper and its task-specific necessity in the audit. Add no
launcher, host adapter,
coordination schema, new prompt hook, global user instruction or automatic config
activation. Preserve specialized Goal-mode and review requirements. Remove the
duplicated orchestration readback paragraph while retaining its required gate.

## Alternatives

Hook-based routing would depend on a specific runtime and trust setup. A global
instruction would stay on one machine. Leaving launches in config transfer would
retain the discovery and responsibility mismatch. A cross-harness runtime would
add an abstraction without a demonstrated need beyond native controls and skills.

## Consequences

Ordinary delegation has one discoverable owner and configuration remains portable
without imposing one user's permission values. Explicit requests can override
defaults within managed policy. Skill/package checks prove distribution and links;
bounded fresh-agent trials provide behavioral observations, not universal adherence
or proof that every host exposes the required controls.

## Revisit

Revisit with evidence of repeated missed discovery or a native delegation operation
that cannot preserve required configuration. Prefer correcting the skill or using
supported host controls before adding executable machinery.
