# ERPNext Operations

An Agentic Workflows Codex plugin for authenticated, permission-aware ERPNext operations.

The plugin:

- onboards from a user-selected JSON key file or standard Frappe CSV export without asking for secrets in chat;
- stores a normalized copy at `~/.config/agentic-workflows/erpnext/credentials.json`;
- protects the directory with mode `0700` and the credential file with mode `0400`;
- authenticates with Frappe's `Authorization: token api_key:api_secret` header;
- routes work to focused skills covering ERPNext desk roles and business domains;
- requires previews, explicit confirmation, and readback for consequential writes.

Start with: `Onboard my ERPNext API user from a key file.`

The source key file should contain:

```json
{
  "site_url": "https://erp.example.com",
  "api_key": "YOUR_API_KEY",
  "api_secret": "YOUR_API_SECRET"
}
```

`api_key_id` is accepted as an alias for `api_key`, and `api_key_secret` as an
alias for `api_secret`.

A standard one-row `frappe_api_keys.csv` containing `api_key,api_secret` is accepted with
`--site-url https://your-erpnext-origin`.
