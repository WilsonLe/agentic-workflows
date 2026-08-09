# Code, media, and extensions

## Git-owned code lane

Themes, `theme.json`, template/part files, registered PHP patterns, block
metadata, PHP/JS/CSS, and build artifacts flow from Git through build/package,
reviewed release, deployment identity, override detection, and rollback. A
content apply is not a code deployment.

Editor-originated code exports run in WordPress Playground or another
disposable environment. `code-export-plan` permits `theme.json` and bounded
HTML/JSON/CSS/static assets under allowlisted theme paths. It rejects PHP, JS,
hidden paths, dependencies, symlinks, and oversized files. The result is a
reviewed patch/bot branch, never a protected-branch write.

## Media lane

Git stores logical identity, source SHA-256, MIME/size/dimensions, alt/caption,
credit/license, provenance, and an approved object-store, release-artifact, or
declared Git LFS locator. It does not version the uploads tree or generated
derivatives. Hash, MIME, size, rights, duplication, private storage, and final
attachment mapping must pass before content references change.

## ACF and extensions

ACF Local JSON field-group definitions are Git-owned code/config and deploy
before dependent values. ACF values require explicit field-group and target
references. Raw PHP serialization and unknown field types/versions fail
closed. Other plugins implement the same adapter conformance contract; generic
`wp_options` or `postmeta` export is prohibited.
