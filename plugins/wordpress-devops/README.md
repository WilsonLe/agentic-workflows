# WordPress DevOps

AMSoft's infrastructure-only WordPress operations plugin.

## Boundary

This plugin resolves authorized Railway or DigitalOcean hosting targets and
operates their WordPress runtime over an existing SSH access path. It covers
WP-CLI discovery, plugin and theme lifecycle, filesystem ownership and update
diagnostics, PHP/runtime configuration, databases, caches, cron, deployment,
health, recovery, and rollback.

It does not author or mutate pages, posts, blocks, images, media, videos, or
user-facing design content. Route those requests to **WordPress Content**. A
task that changes runtime code and then needs a content review uses both
plugins: DevOps owns source, release, and commit; Content owns the user-facing
content and rendered verification.

## Authentication contract

Require one resolved provider target—Railway or DigitalOcean—and an existing
authorized SSH agent, host alias, or equivalent secret-manager-backed access
path. Railway and DigitalOcean account credentials are used only to resolve or
operate the provider target through their dedicated account workflows; they
are not WordPress REST credentials. Never paste provider tokens, private keys,
or SSH passwords into chat.

Every mutating DevOps operation must be represented in the versioned
infrastructure/deployment source of truth and committed. A remote diagnostic
is not a release, and a direct emergency repair leaves drift that must be
reconciled before the task can be called complete.

## First prompt

```text
Use WordPress DevOps to onboard my Railway or DigitalOcean WordPress target and existing SSH access read-only, identify the runtime and source of truth, and do not change the server.
```

Production changes retain separate approval, backup, deployment, readback,
and rollback gates.
