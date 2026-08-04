# WordPress integrations and data flows

Use one lifecycle for optional plugins and external providers:

`available -> installed -> activated -> configured -> connected -> consent-enabled ->
collecting/recording -> verified -> rolled-back`

Do not collapse these states into “working”. Record the plugin/provider, version/source freshness,
dependency order, owner, mutable external state, data captured or forwarded, consent/privacy/
retention, duplicate event risk, backup/rollback, and verification surface.

## Integration boundaries

- **Forms/email:** identify form IDs, recipients, sender/reply-to behavior, anti-spam, SMTP/provider
  route, consent text, logs, and a safe non-sensitive test. Never expose submitted values.
- **Analytics/consent:** distinguish tag presence, consent mode, logged-in exclusion, connection,
  collection, retention, and delayed provider readback. Source markup is not collection proof.
- **SEO:** preserve approved facts, canonical/indexing/robots/sitemap/meta/schema state, and the
  content owner. Recommendations, implemented metadata, recrawl, and ranking are separate states.
- **Stream/audit:** preserve policy, retention, access, privacy, supported fixtures, cleanup, and
  administrator UI/data evidence. Configuration is not proof that the desired event was recorded.
- **Privacy/legal:** use approved source text and owner/jurisdiction review. Do not invent legal
  copy, consent claims, retention claims, or provider compliance.
- **Theme/starter/plugin import:** inspect current architecture and dependencies first. Do not use
  destructive clean imports, broad option resets, or automatic activation as a generic solution.

For every integration, state whether the requested work is read-only inspection, package/source
change, local configuration, staging apply, production apply, connection, publication, or data
collection. Each later state requires its own approval and evidence.
