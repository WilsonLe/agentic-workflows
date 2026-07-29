# WordPress Stream audit-logging onboarding

Use read-only discovery first.

## Required context

Resolve:

- the authorized site, environment, canonical HTTPS URL, and whether production is in scope;
- SSH/hosting access and the supported bare-metal, managed-host, or Docker Compose WP-CLI adapter;
- WordPress, PHP, database, multisite, active theme, relevant plugin, and Stream versions;
- current Stream status, source, tables, options, scheduler, retention, access, exclusions, alerts,
  integrations, warnings, and approximate record volume;
- current backup and rollback mechanisms;
- the server/CDN/reverse-proxy boundary that establishes the trusted client IP;
- the privacy-notice surface and accountable policy owner;
- administrator browser access for real UI verification.

Never ask for passwords, private keys, database credentials, WordPress salts, cookies, tokens, or
audit exports in chat. Use an existing authorized session, SSH agent, or secret manager.

## Readiness

Return one status:

- `Ready`: the exact target, authorization, runtime adapter, current state, backup path, policy
  owner, and required verification channels are known.
- `Needs input`: a material target, policy, authorization, or owner decision is missing.
- `Needs configuration`: access or a required runtime/verification channel is not usable.
- `Not selected`: audit logging is not requested for this site.

A read-only review can proceed with partial context, but label every unknown. Installation or
configuration remains blocked until material policy and recovery choices are resolved.

## First prompts

- `Review whether Stream audit logging is working on this authorized WordPress site. Do not change anything.`
- `Add Stream audit logging to this repository-managed WordPress stack and stop at the required approval gates.`
- `Configure and prove Stream on this authorized staging site, including a reversible synthetic event.`
