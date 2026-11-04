# ADR-0011: Publish portable packages from one maintained suite

- Status: accepted
- Date: 2026-11-04
- Owner: Project maintainer and implementing agent within task authority
- Evidence: Maintainer approval of plan v2 for [issue 93](https://github.com/WilsonLe/agentic-workflows/issues/93)
- Supersedes: none
- Superseded by: none

## Context

Codex installs the suite directly from the source marketplace. Claude Code and
OpenCode use harness-specific packages with transformed instructions, filtered
capabilities, and shared assets. Their generated trees add duplicate diffs to
source PRs. Component packages also own files mirrored into the Codex suite,
although both marketplaces list only the suite.

## Decision

The catalog and the existing materializer build the two portable bundles into a
separate directory. A read-only Actions job validates the build from current
`main`. A separate job publishes the validated tree to `dist` with its source
commit in the commit message. Publication uses regular fast-forward pushes,
skips stale and byte-identical builds, and keeps the last validated tree if a
check or push fails. A revert on `main` republishes the restored package.

After hosted consumer verification, Claude Code will fetch the consolidated
bundle from `dist` under the same marketplace and plugin IDs. OpenCode users
will use a persistent `dist` checkout with the existing native skills config.
Codex continues to install the suite from `main`, where the suite becomes the
only maintained package. The catalog declares each skill's harnesses and the
portable filter excludes shared Codex-only assets explicitly. The
`legacy-components-v1` tag preserves the last pre-cutover standalone paths.
Roll out the publisher, portable consumer cutover, and Codex consolidation in
that order.

## Alternatives

Committing generated trees alongside source keeps install paths simple and
requires source PRs to carry the duplicate trees. Release archives preserve
packages but require a separate OpenCode update procedure. Continuing to build
legacy components would keep a second supported package shape with little
benefit for marketplace users. Consolidation preserves the suite's existing
paths and native Codex update channel.

## Consequences

Claude and OpenCode updates follow the last verified distribution commit. A
failed publish is visible in Actions and can be retried from `main`. OpenCode
users change their configured path once. Standalone consumers can pin the
legacy tag or migrate to the maintained suite. Contributors keep running
source and package checks before PRs. Full local CI remains a merge-time gate.

The [first hosted release](https://github.com/WilsonLe/agentic-workflows/actions/runs/41753486712)
was verified from fresh Claude Code and OpenCode installs before the portable
cutover. The [legacy tag](https://github.com/WilsonLe/agentic-workflows/tree/legacy-components-v1)
pins the verified pre-cutover source and its standalone package paths.

## Revisit

Reassess if a host drops the supported Git or local skills install path, if
automatic builds regularly lag behind source changes, or if a demonstrated
standalone consumer needs maintained releases.
