# ERPNext browser permissions and optional diagnostic baseline

Browser forms, installed-site behavior, and actual permissions are authoritative.
Apply [service browser operations](browser-selection.md) and `erpnext-operations`.

Before a mutation inspect exact DocType/document, required fields/link targets,
company, currency, fiscal year, warehouse, cost center, project/dimensions,
workflow/docstatus, naming/duplicates, downstream effects, and reversal path.
Do not bypass role permissions, field permission levels, record-level restrictions,
workflows, fiscal locks, ledger rules, or separation of duties. Workspace visibility
alone is not authorization. Browser and API users can have different identities.

Optional protected API reads may supplement diagnosis only after matching the
helper's user/site/company scope independently to the browser. Use the bundled
`erpnext_api.py` read operations with bounded records/output. Do not print full User
records, key/secret values, authorization headers, or private business payloads.
Normal onboarding does not require a key file. If diagnostic credential setup is
explicitly within scope, the installer accepts a private JSON key file or one-row
Frappe CSV plus confirmed site origin; retain owner-only modes, protected storage,
read-only verification, and explicit replacement/archival controls. Do not generate
or rotate keys to test browser access or substitute an Administrator user.

Management, draft/transaction writes, submission/cancellation, and settings changes
use supported UI controls. A missing control requires a concrete limitation and
explicit channel direction before any API mutation; a client confirmation flag is
not authority. Preserve TLS checks and actual site permission failures.

Current official references:
- [Role permissions](https://docs.frappe.io/erpnext/role-based-permissions)
- [User permissions](https://docs.frappe.io/erpnext/user-permissions)
- [REST API](https://docs.frappe.io/framework/user/en/api/rest) for optional read-only diagnostics.
