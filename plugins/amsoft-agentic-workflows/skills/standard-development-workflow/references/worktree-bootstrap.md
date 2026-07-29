# Worktree bootstrap and runtime isolation

Create the worktree before researching the issue or writing the implementation plan. Minimal
read-only discovery is allowed first because the exact repository, base, and safe target path must
be resolved before mutation.

## Create safely

1. Read repository and parent-directory instructions.
2. Identify the canonical checkout, remote, default/base branch, current branch, dirty state, and
   all existing worktrees. Preserve every unrelated modification.
3. Fetch the required remote state when network access is authorized. Create a clearly named
   feature branch from the intended current base revision, not from an arbitrary dirty checkout.
4. For each new worktree, use a sibling directory formed by appending `.worktrees` to the canonical
   repository directory name, then add a clearly named feature leaf:
   `<parent>/<repository>.worktrees/<feature-name>`. For example, a canonical checkout at
   `/workspace/example` uses `/workspace/example.worktrees/fix-login`. Confirm the path does not
   overlap an existing worktree. Record repository, base revision, branch, and path in progress
   updates.
5. Apply this convention prospectively. Never relocate, reset, clean, rename, or reuse an existing
   or unrelated worktree merely to make it conform or to make room.

## Carry over local configuration without leaking it

1. Inventory candidate environment files from repository docs, Compose configuration, package
   scripts, ignore rules, and the canonical checkout. Common names are evidence, not a blanket list.
2. Tracked examples and templates arrive through Git. Copy only required local, ignored
   environment files from the resolved canonical checkout to the matching relative paths.
3. Preserve file modes where practical. Create missing parent directories only inside the new
   worktree.
4. Never display file contents, copy credential stores or broad home-directory state, or stage
   copied secrets. Verify only path presence, ignore status, permissions, and required variable
   names without values.
5. If the new worktree needs distinct non-secret overrides such as ports, hostnames, Compose
   project name, or database name, write them to the repository's documented local override file.
   Do not modify shared secret source files.
6. Confirm copied local files remain ignored with Git's ignore diagnostics. Stop if a secret-bearing
   file would be tracked.

## Install and onboard

1. Re-read worktree-local instructions and lockfiles.
2. Verify exact runtime and package-manager versions from repository configuration.
3. Use the lockfile-preserving deterministic install command documented by the repository.
4. Run prerequisite generation, submodule, database, or asset steps only when repository evidence
   requires them.
5. Record commands and outcomes without recording credentials.

## Docker Compose isolation

1. Inspect all ports published by the canonical stack and other feature stacks, including inactive
   repository configurations and active host listeners.
2. Allocate one consecutive digit block large enough for every published worktree service. Keep the
   same last-digit service mapping when practical. Example: if the main stack uses `30289` through
   `30292`, choose a different free consecutive block rather than reusing any of those ports.
3. Assign a unique Compose project name derived from the repository and feature branch so
   containers, networks, and named volumes do not collide.
4. Keep container ports unchanged unless the application requires otherwise; isolate published host
   ports and worktree-facing URLs.
5. Isolate mutable databases, caches, uploads, queues, and volumes. Never point a feature stack at
   the canonical development database unless the repository explicitly defines that as safe.
6. Render and validate the effective Compose configuration before startup.
7. Start the full documented stack, wait for health, inspect logs, and verify the real local URL.
8. Record the port map and Compose project name in the implementation plan and draft PR evidence,
   excluding secrets.

## Capacity and suite isolation

Before startup or another expensive operation, apply the resource budget in
[discovery-contract-and-scope.md](discovery-contract-and-scope.md). Resolve task-owned,
repository-shared, host-shared, and external resources before any cleanup decision.

Worktree isolation does not automatically isolate validation suites. When integration, browser, or
other suites can mutate data observed by each other, give them separate databases, queues, object
stores, caches, filesystem roots, users, fixtures, or namespaces unless repository evidence proves
sharing safe. Record readiness and exact cleanup ownership before starting a suite.
