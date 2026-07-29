# ERPNext API onboarding

## Credential contract

The source can be a JSON file containing:

```json
{
  "site_url": "https://erp.example.com",
  "api_key": "YOUR_API_KEY",
  "api_secret": "YOUR_API_SECRET"
}
```

Accepted aliases are `url`, `api_key_id`, and `api_key_secret`. Do not ask the user to paste any
value. A standard Frappe CSV export with exactly one row and headers `api_key,api_secret` is also
accepted. Because that CSV does not contain the ERPNext origin, pass `--site-url` separately.

Ask only: “Where is the ERPNext API key JSON or CSV file on this computer?” If a two-column CSV is
selected, also ask for the ERPNext site origin. On macOS, download metadata may identify the source
origin; present that origin for confirmation unless the user's request already authorizes verifying
the credential export against its own download origin.

The installer normalizes and copies the values to:

`~/.config/amsoft/erpnext/credentials.json`

It sets the parent directory to `0700`, atomically writes the file, then sets it to owner-read-only
mode `0400`. The API client refuses a credential file owned by another user or with any other mode.
The original remains the user's responsibility by default; if it is broadly readable, the installer
warns without exposing its contents. If the user explicitly authorizes relocation, wait until
read-only authentication succeeds, then move the original into
`~/.config/amsoft/erpnext/imported-sources/`, set that directory to `0700`, set the archived source
to `0400`, and report both paths. Never overwrite an existing archived source.

## First-use sequence

1. Ask for the source file path.
2. Confirm the path exists and is a regular file without displaying the file.
3. For JSON with a site URL, run
   `python3 <plugin-root>/scripts/erpnext_configure_credentials.py <source-path>`. For a two-column Frappe
   CSV, run
   `python3 <plugin-root>/scripts/erpnext_configure_credentials.py <source-path> --site-url <confirmed-origin>`.
4. If protected credentials already exist, do not replace them silently. Explain that replacement
   is credential rotation, obtain explicit confirmation, and rerun with `--replace`.
5. Run `python3 <plugin-root>/scripts/erpnext_api.py whoami`.
6. If authentication succeeds, run
   `python3 <plugin-root>/scripts/erpnext_api.py user-summary` to return only
   non-secret user metadata and role names. Do not print the full `User` document.
7. Read only enough Company, Global Defaults, System Settings, and installed-domain context to
   identify the site. Some records may be forbidden; a permission denial is evidence, not a reason
   to escalate or bypass access.
8. Report readiness: protected path, verified identity, reachable site origin, observed roles,
   company/default context, unavailable checks, and zero writes performed.
9. If source relocation was explicitly authorized, move it into the protected imported-sources
   directory only now, after successful authentication.

## Key creation guidance

If the user has no key yet, direct an authorized System Manager to open the ERPNext User record,
find API Access, and generate keys. The API secret is shown at generation time and should be put
directly into a protected local JSON file or password-manager export, not sent through chat.

## Failure handling

- `401` or `403`: report the sanitized response and ask the user to verify the selected ERPNext
  user, API key/secret pair, and role/permission assignments.
- TLS or hostname error: stop. Do not disable certificate verification.
- On macOS, if Python's bundled OpenSSL cannot find a valid issuer but system `curl` verifies the
  same origin with result `0`, use the system CA bundle at `/etc/ssl/cert.pem`; never use an
  unverified SSL context or `curl -k`.
- HTTP is allowed only for a loopback development origin.
- Missing DocType permission: do not switch to Administrator credentials or browser automation.
- Rotation: create a new key, install it with approved `--replace`, verify `whoami`, then revoke the
  old key through the authorized ERPNext workflow.
