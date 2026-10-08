# Official API and permission baseline

Apply [authenticated CLI and browser assistance](browser-selection.md). Default to
the protected authenticated command-line client; acquire missing API credentials
through the built-in browser with concealed transfer and verify the client. Browser
operations require a proven authenticated-client capability gap, never a permission
denial or unverified identity. Preserve the same site/user/company/record scope.


Use current official documentation before relying on endpoint shapes or ERPNext behavior:

- Frappe REST API: <https://docs.frappe.io/framework/user/en/api/rest>
- ERPNext role-based permissions: <https://docs.frappe.io/erpnext/role-based-permissions>
- ERPNext user permissions: <https://docs.frappe.io/erpnext/user-permissions>
- ERPNext roles and role profiles: <https://docs.frappe.io/erpnext/role-and-role-profile>
- ERPNext users: <https://docs.frappe.io/erpnext/adding-users>

Frappe authenticates API key access with:

`Authorization: token api_key:api_secret`

Frappe applies the authenticated user's roles and permissions to API requests. REST resources are
available under `/api/resource/:doctype` and whitelisted methods under `/api/method/:method`.
Never assume a method is whitelisted, a DocType exists, or fields match another ERPNext version.

Before a mutation, discover:

- exact DocType and document name;
- current record and `docstatus`;
- required fields and link targets;
- company, currency, fiscal year, warehouse, cost center, project and accounting dimensions;
- applicable workflow state and assigned approver;
- naming series and duplicate detection;
- downstream ledger, stock, manufacturing, payroll, email, or portal effects;
- supported reversal, return, cancellation, or amendment path.

Role assignment is only one layer. Role permissions govern actions on DocTypes, permission levels
can restrict fields, user permissions can restrict records such as a Company or Territory, and
workflows can further constrain transitions. Workspace visibility is not an authorization check.
