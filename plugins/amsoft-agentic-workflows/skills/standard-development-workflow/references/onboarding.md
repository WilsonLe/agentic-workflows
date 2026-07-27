# Standard Development Workflow onboarding

Use this guide when the user asks to set up, onboard, or get started with the workflow.

## Prerequisites

- A Git repository with a resolvable canonical checkout and base branch.
- Git worktree support.
- Live GitHub CLI authentication with access to read the repository, create issues and branches,
  push changes, open pull requests, and merge when repository policy permits.
- The repository's documented language runtimes, package managers, test tools, and local stack.
- For containerized applications, Docker and Docker Compose plus an available isolated port block.
- For staging, an existing authorized deployment mechanism and non-production credentials supplied
  outside chat.

Never ask the user to paste secrets. Verify whether required variables or credentials exist without
printing their values.

## First-run readiness check

1. Locate the repository and read its local instructions.
2. Confirm Git and GitHub CLI availability and verify the live GitHub identity. The presence of
   `gh` alone is not proof of authentication.
3. Inspect configured worktrees, canonical checkout status, default branch, remotes, and repository
   protections without changing them.
4. Identify documented install, test, local-stack, and deployment commands.
5. For Docker Compose, inspect the canonical checkout's project name, published ports, networks,
   volumes, and active containers. Identify a consecutive, non-overlapping port block for the next
   worktree without starting it.
6. Report `Ready`, `Needs input`, `Needs configuration`, or `Blocked`, with the next safe action.
7. Do not create a worktree or GitHub issue merely to prove installation unless the user has also
   asked to begin a real change.

## Suggested first prompt

> Use Standard Development Workflow for this change. Create and onboard an isolated worktree,
> research and create a spec-ready GitHub issue, write the exhaustive implementation and test plan,
> then stop for my approval before coding.
