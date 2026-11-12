# DigitalOcean managed services runbook

Use the [Infisical-backed CLI channel](../../agentic-workflows/references/service-browser-operations.md).
Obtain the required token from Infisical and verify provider identity and exact
target through read-only CLI commands. Missing tokens, commands or permissions
block dependent work; do not switch to connectors or cached login.

Use for Kubernetes, managed databases, container registries, and Spaces-related requests.

## Kubernetes

Discover cluster CLI commands and inspect the exact action schema. Capture cluster ID, region,
version, node pools, autoscaling, maintenance window, VPC, and status. Treat cluster deletion,
upgrades, node-pool removal, credential retrieval, and registry integration as high impact. Never
expose kubeconfig credentials.

## Databases

Discover database CLI commands and inspect the exact action schema. Capture engine, version, region,
size, nodes, maintenance, users, databases, pools, firewalls, replicas, and status as applicable.
Never print connection credentials or reset a password merely to test access. Treat deletion,
resize, migration, failover, user deletion, firewall changes, and credential resets as high impact.

## Container registry

Discover registry CLI commands and inspect the exact action schema. Capture registry name, region, repositories, tags,
garbage-collection state, and subscriptions. Treat manifest deletion, garbage collection, registry
deletion, and Kubernetes integration changes as high impact. Never expose generated Docker
credentials.

## Spaces

Do not infer Spaces/S3 support from doctl authentication. Check actual CLI
coverage and required bucket/object permissions. Report missing support without
automatically adding an S3 client, another credential or dashboard fallback.

For every mutation, follow `change-management.md` and verify the service reaches a healthy terminal
state.
