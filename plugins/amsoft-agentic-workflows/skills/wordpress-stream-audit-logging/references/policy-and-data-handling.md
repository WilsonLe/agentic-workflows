# Stream policy and data handling

Record the site policy before mutation.

## Policy record

Include:

- selected Stream version/source and verification date;
- purpose and accountable owner;
- live-table retention and whether indefinite retention is allowed;
- viewer roles/capabilities and the settings capability;
- exclusions and comment-flood tracking choices;
- automatic-purge requirement and scheduler backend;
- email, webhook, Slack, IFTTT, export, external shipping, Abilities API, MCP Adapter, and AI access;
- WordPress database and backup data locations/retention;
- expected actor, role, action, object, timestamp, and verified request-IP fields;
- authoritative proxy/client-IP boundary;
- multisite/network behavior;
- privacy disclosure and release/rollback path.

Offer 90-day retention, administrator-only access, no exclusions, automatic purge, no outbound
integrations, and no AI/MCP access as a conservative reviewed proposal. Do not apply it without
explicit acceptance and do not present it as legal advice.

## Data boundaries

Treat Stream records as potentially sensitive. Keep real records, exports, IP addresses, emails,
user/customer information, sessions, and database content out of Git, issues, PRs, chat, terminal
transcripts, screenshots, and videos. Prefer synthetic local/staging fixtures and show only the
smallest filtered fields needed to prove the expected event.

Audit-log retention and backup retention are different. A 90-day live-table policy does not erase
older records already retained by backups. State both accurately in privacy and operational
documentation.

Do not enable alerts, external shipping, exports, Abilities API, MCP Adapter, or AI queries merely
because upstream supports them. Each adds a separate access or data-flow decision.

## Client IP

Require the web server or a validated trusted-proxy/CDN configuration to establish
`REMOTE_ADDR`. Refuse a workaround that trusts a raw `HTTP_X_FORWARDED_FOR`,
`HTTP_TRUE_CLIENT_IP`, or other client-supplied header without that boundary.

## Capability claims

Describe only connectors and actions verified in the selected upstream version and target
installation. Stream is an application activity log, not immutable off-host logging, a SIEM, a
backup, malware protection, a WAF, or proof that every third-party plugin action is captured.
