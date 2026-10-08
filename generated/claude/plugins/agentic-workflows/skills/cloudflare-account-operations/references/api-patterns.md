# Optional Cloudflare diagnostic patterns

[Service browser operations](browser-selection.md) is the base. This reference
covers optional read-only helper/CLI diagnostics only; browser management does
not require token installation or verification.

Use existing authorized protected credentials when a needed diagnostic is within
scope. The bundled `cloudflare_api.py` supports bounded read-only verification
and account/zone discovery. A token verification result alone does not identify
the dashboard account: independently resolve its identity/account and exact zone
or product scope, then compare to the visible browser target. If they cannot be
matched, skip the diagnostic. Do not extract credentials from the browser.

The protected installer `cloudflare_configure_credentials.py` is optional setup
only when credential setup for that diagnostic is authorized. Preserve its token
classification, private-file, ownership/mode, verification, and archival checks;
never request token values in chat or use Global API Keys. Do not replace an
existing credential silently or broaden scopes to bypass a denial.

For supplemental requests, inspect current official read-only documentation and
installed help. Bound pagination, item counts, timeouts, and logs; preserve useful
sanitized error codes. Do not dump headers, credentials, environments, or binding
values. No shell tracing or unsanitized verbose output.

Management writes use UI controls via [change management](change-management.md).
Do not construct curl write requests or deploy with Wrangler under diagnostic
permission. A non-browser mutation needs explicit channel direction after a UI gap
is explained. Do not extend a helper to add a write just to avoid the dashboard.
