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

1. Resolve the source checkout in the same repository: use the canonical checkout by default,
   or the originating worktree when branching from its local setup. Record the selected source;
   do not merge credentials from unrelated checkouts or silently fall back to a different account.
2. Inventory local environment files and `.cli/` credential files from that source, repository
   docs, Compose configuration, package scripts, and ignore rules. Include nested application
   env files. Tracked examples and templates arrive through Git; copy the local ignored files
   needed to preserve the project's setup to matching relative paths in every new worktree.
3. Before copying, apply [project-local CLI credential controls](../../agentic-workflows/references/task-authority-and-secrets.md#project-local-cli-credentials).
   Verify source and destination paths are inside their resolved roots, untracked, ignored,
   owner-controlled, and free of symlinks in every path component. Ensure `/.cli/` and each local
   env path are ignored in the destination before writing. A tracked, unignored, or unsafe
   secret path blocks the copy; resolve it first without exposing or staging contents.
4. Create independent copies with owner-only secret permissions and missing parent directories
   only inside the destination. Never overwrite an existing destination: reuse it only after
   a concealed comparison confirms it is identical; otherwise preserve it and resolve the
   conflict. Do not copy global credential stores, broad home-directory state, shared hardlinks,
   or symlinks. Same-project `.cli/` credentials are explicitly part of bootstrap.
5. Verify the copied-file inventory, permissions, `git check-ignore`, and absence from
   `git ls-files` without displaying values. Report missing required files as setup blockers;
   use provider onboarding for missing credentials. Never treat a partial copy as ready.
6. If the new worktree needs distinct non-secret overrides such as ports, hostnames, Compose
   project name, or database name, write them to the repository's documented local override file.
   Do not modify shared secret source files.
7. Apply provider-specific handling for copied rotating refresh tokens before any CLI auth
   check; Vercel onboarding requires an independent destination login for copied OAuth sessions.
   Rebind CLI commands to the new worktree's `.cli/` paths and verify authentication and exact
   account/project/environment read-only before dependent remote work. Copied credentials
   retain their remote access; they do not authorize production use or provide runtime isolation.

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
