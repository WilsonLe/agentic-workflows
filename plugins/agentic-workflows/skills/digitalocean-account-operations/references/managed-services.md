# DigitalOcean managed services runbook

Use the [Codex connected-app channel](../../agentic-workflows/references/service-browser-operations.md).
Verify connected identity and the exact target through read-only tools. Missing
connections, operations, or permissions remain blockers; recover through Codex
without local-token or dashboard fallback.

Use for Kubernetes, managed databases, container registries, and Spaces-related requests.

## Kubernetes

Discover connected cluster tools and inspect the exact action schema. Capture cluster ID, region,
version, node pools, autoscaling, maintenance window, VPC, and status. Treat cluster deletion,
upgrades, node-pool removal, credential retrieval, and registry integration as high impact. Never
expose kubeconfig credentials.

## Databases

Discover connected database tools and inspect the exact action schema. Capture engine, version, region,
size, nodes, maintenance, users, databases, pools, firewalls, replicas, and status as applicable.
Never print connection credentials or reset a password merely to test access. Treat deletion,
resize, migration, failover, user deletion, firewall changes, and credential resets as high impact.

## Container registry

Discover connected registry tools and inspect the exact action schema. Capture registry name, region, repositories, tags,
garbage-collection state, and subscriptions. Treat manifest deletion, garbage collection, registry
deletion, and Kubernetes integration changes as high impact. Never expose generated Docker
credentials.

## Spaces

Do not infer full Spaces/S3 support from the DigitalOcean connection. Check the
actual exposed tools and required bucket/object permissions. If the operation is
unavailable, report the exact capability gap without requesting another key,
constructing an API client, or falling back to dashboard management.

For every mutation, follow `change-management.md` and verify the service reaches a healthy terminal
state.
