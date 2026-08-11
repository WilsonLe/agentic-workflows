---
name: excalidraw-api-operations
description: Safely inspect and operate an authorized Excalidraw Plus account through the public REST API using a protected personal MCP/API key. Use for onboarding, collections, scenes, users, invites, logs, workspace inventory, API errors, request-authorized changes, and destructive-operation approval. Never use MCP for this skill.
---

# Excalidraw API Operations

Use the bundled REST helper at `<plugin-root>/scripts/excalidraw_api.py`. Do not configure or
call Excalidraw MCP. The Excalidraw Plus API is a public-beta surface; verify
current official documentation when a response or route differs from the
documented contract.

For setup or first use, read
[onboarding.md](references/onboarding.md) and
[credential-contract.md](references/credential-contract.md). Accept only a
user-confirmed personal MCP/API key supplied through a local file path. Never
ask for key text in chat.

## Core workflow

1. Verify protected credentials read-only with `GET /collections?limit=1`.
2. Resolve the workspace, collection, and scene from structured reads.
3. Keep collection, scene metadata, and scene content distinct.
4. Before a write, read
   [change-management.md](references/change-management.md), identify the exact
   method/path/ID, capture pre-state, summarize the payload without dumping it,
   and describe verification and recovery. The user's explicit request to make
   the non-destructive change is authorization; do not ask for a typed token or
   a second confirmation. DELETE retains its destructive confirmation gate.
5. Execute the smallest sufficient operation.
6. Read back the affected resource and compare the intended fields.
7. If a write response is lost, do not retry. Perform safe readback and report
   the outcome as confirmed, not observed, or unknown.

Inspect, diagnose, inventory, explain, and plan requests authorize reads only.
They do not authorize collection or scene writes.

## Resource routing

Read [api-resource-map.md](references/api-resource-map.md) for the complete
documented surface. The typed client covers every documented route, including
workspace, user, and invite mutations, but broad key access does not create
broad change authority.

Use `excalidraw-scene-operations` whenever the task creates, edits, replaces,
backs up, verifies, or deletes one scene.

## Failure handling

Read [errors-and-rate-limits.md](references/errors-and-rate-limits.md).
Safe reads may retry bounded `429` or transport failures. Writes are never
automatically retried because Excalidraw documents no idempotency contract.

## Verification

Report the personal key declaration, resolved IDs, method/path without headers,
authorization basis, sanitized response status, rate-limit metadata, protected
backup path where applicable, readback result, and recovery state. Never report
the key, authorization header, credential record, or unreviewed scene content.
