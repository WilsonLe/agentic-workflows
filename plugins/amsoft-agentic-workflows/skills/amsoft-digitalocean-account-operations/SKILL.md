---
name: amsoft-digitalocean-account-operations
description: Safely inspect and operate a DigitalOcean account through the doctl CLI using a user-provided API access token. Use for DigitalOcean onboarding, authentication checks, account and resource inventory, Droplets, VPCs, firewalls, domains and DNS, load balancers, Kubernetes, databases, container registries, Spaces metadata, projects, monitoring, snapshots, images, SSH keys, invoices, incidents, approval-gated changes, and debugging failed or unfamiliar doctl requests with help, verbose, or trace output.
---

# DigitalOcean Account Operations

Use `doctl` as the execution layer. Do not add or call an MCP server and do not replace `doctl`
with ad hoc API requests when the CLI supports the operation.

For setup or first use, read [references/onboarding.md](references/onboarding.md). Use the bundled
protected installer and `digitalocean_cli.py` launcher. Never ask the user to paste a token into
chat or put a literal token in a command, log, or tool argument.

## Core workflow

1. Confirm `doctl` is installed with `doctl version`.
2. Confirm the protected credential record is present with the required owner-only modes.
3. Verify read access with `doctl --context default account get --output json` so the
   environment-provided token takes precedence over stored non-default contexts.
4. Discover resource identifiers with read-only `doctl` commands; never guess IDs, names, regions,
   VPCs, clusters, databases, domains, records, or project assignments.
5. For a change, read the current state and retain the fields required for rollback.
6. Resolve the exact command and flags with `doctl help`, `doctl <resource> --help`, and
   `doctl <resource> <action> --help`.
7. Present the target, exact command with secret-free placeholders, impact, validation, and
   rollback.
8. Obtain explicit approval before running a create, update, delete, action, deployment, resize,
   migration, failover, rebuild, reboot, power, or project-assignment command.
9. Execute the smallest sufficient command.
10. Read the resource again and report before/after evidence.

Never interpret inspect, diagnose, review, explain, inventory, or plan as authorization to change
DigitalOcean.

## Authentication and secrets

- Load the normalized credential from
  `~/.config/amsoft/digitalocean/credentials.json` through the bundled launcher.
- Run token-backed commands with the `default` context. DigitalOcean documents that the
  environment token is ignored when a non-default authentication context is selected.
- Prefer the environment variable over `doctl auth init`, because `auth init` persists a token in a
  local authentication context.
- If the user explicitly requests a persistent context, explain that storage behavior and obtain
  approval before running `doctl auth init`.
- Never use `--access-token` with a literal token. If a command must use the global flag, reference
  the environment variable without printing it.
- Prefer a least-privilege, expiring token appropriate to the requested resources.
- Never print shell environments, configuration files, trace headers, or debug output that could
  expose a token. Redact credentials before reporting diagnostics.

## Command discipline

- Prefer `--output json` for inspection and verification.
- Use `--format` only after checking the command help for supported fields.
- Do not select a non-default context for token-backed work. Use one only when the user explicitly
  asks to operate a stored context instead of the supplied environment token.
- Narrow list requests with supported filters and pagination flags.
- Do not assume flags are uniform across resource groups; inspect the specific action help.
- Do not install or upgrade `doctl` without user approval.

## Help and debugging

When syntax, flags, capabilities, or errors are unclear, read
[references/troubleshooting.md](references/troubleshooting.md). Start with command help, then retry
only a read-only request with `--verbose` or `--trace`. Treat trace output as potentially sensitive
and sanitize it before showing or saving it.

## Runbooks

Read the relevant reference before acting:

- [General change runbook](references/change-management.md) for every mutation.
- [Compute and networking](references/compute-networking.md) for Droplets, VPCs, firewalls, load
  balancers, reserved IPs, images, snapshots, SSH keys, and actions.
- [Domains and DNS](references/dns.md) for domains and records.
- [Managed services](references/managed-services.md) for Kubernetes, databases, registries, and
  Spaces-related work.
- [Troubleshooting](references/troubleshooting.md) for help discovery, verbose output, trace
  collection, authentication failures, rate limits, and unknown commands.

DigitalOcean CLI behavior changes. Use the installed `doctl` help as the command-specific source of
truth, and consult current official DigitalOcean documentation when behavior, limits, or risk is
uncertain.
