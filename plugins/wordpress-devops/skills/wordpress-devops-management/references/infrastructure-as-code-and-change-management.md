# WordPress infrastructure-as-code and change management

Use versioned infrastructure/deployment source for durable DevOps changes.

## Source-of-truth checklist

Identify the repository and exact path that controls the target's Dockerfile,
Compose/entrypoint, Terraform/provider settings, environment declarations,
plugin/theme package, deployment manifest, or release script. Before editing,
record the current commit, branch, dirty state, generated-file rules, and
checks. Preserve unrelated work.

## Change sequence

1. Write a narrow diff for the exact runtime/provider/plugin/filesystem issue.
2. Add or update tests, probes, manifests, and rollback documentation needed
   by the source change.
3. Validate syntax, generated artifacts, plugin/package compatibility, and
   targeted runtime behavior in an isolated environment where available.
4. Obtain review and environment-specific approval.
5. Deploy from the reviewed commit or run the exact approved release adapter.
6. Verify provider identity, deployed revision, SSH/runtime, WordPress/PHP,
   plugin/theme, filesystem, health, and affected public behavior.
7. Commit the final source change and retain the exact commit/deployment
   identity in the handoff.

Merge or commit is not deployment proof. Deployment or provider health is not
source or rollback proof.

## Prohibited shortcut

Do not complete a task by manually editing a remote PHP/CSS/JS/config file,
running an untracked plugin update, changing a provider variable without
source reconciliation, or hiding a filesystem repair in a content operation.
If the target cannot currently be changed through its source/deployment path,
report the DevOps task as blocked or as explicitly recorded emergency drift;
do not claim infrastructure-as-code completion.

## Rollback

Define the exact prior source revision, deployment artifact, provider revision,
plugin/theme version, volume/file ownership state, and database backup needed
for recovery. Keep rollback separate from content rollback. Never restore a
whole WordPress volume or run a broad database replacement as a diagnostic.
