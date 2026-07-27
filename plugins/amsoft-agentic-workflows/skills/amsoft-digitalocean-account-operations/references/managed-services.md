# DigitalOcean managed services runbook

Use for Kubernetes, managed databases, container registries, and Spaces-related requests.

## Kubernetes

Inspect `doctl kubernetes --help` and the exact cluster action help. Capture cluster ID, region,
version, node pools, autoscaling, maintenance window, VPC, and status. Treat cluster deletion,
upgrades, node-pool removal, credential retrieval, and registry integration as high impact. Never
expose kubeconfig credentials.

## Databases

Inspect `doctl databases --help` and the exact subcommand help. Capture engine, version, region,
size, nodes, maintenance, users, databases, pools, firewalls, replicas, and status as applicable.
Never print connection credentials or reset a password merely to test access. Treat deletion,
resize, migration, failover, user deletion, firewall changes, and credential resets as high impact.

## Container registry

Inspect `doctl registry --help`. Capture registry name, region, repositories, tags,
garbage-collection state, and subscriptions. Treat manifest deletion, garbage collection, registry
deletion, and Kubernetes integration changes as high impact. Never expose generated Docker
credentials.

## Spaces

`doctl` support is not equivalent to the full S3-compatible Spaces API. Check `doctl help` and
current DigitalOcean documentation before claiming an operation is supported. Do not silently fall
back to another credential type or CLI. Explain the required tool and request direction if the task
is outside `doctl`.

For every mutation, follow `change-management.md` and verify the service reaches a healthy terminal
state.
