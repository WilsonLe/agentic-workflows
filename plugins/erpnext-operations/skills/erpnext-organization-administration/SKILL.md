---
name: erpnext-organization-administration
description: Expertly inspect and safely administer ERPNext companies, departments, branches, users, roles, role profiles, role permissions, user permissions, global defaults, system settings, email, workspaces, translations, and access controls through an authorized API user. Use for System Manager, Workspace Manager, Report Manager, Translator, Inbox User, and organization-administration work.
---

# ERPNext Organization Administration

First apply `erpnext-operations` for authentication, API discipline, approvals, and verification.

## Scope and discovery

Map the live organization before changing it: Company, Department tree, Branch, Cost Center,
Warehouse, Employee/User links, Global Defaults, System Settings, Fiscal Year, Currency, Country,
Letter Head, Email Account, Domain Settings, Workspace, Role, Role Profile, Custom DocPerm, User
Permission, Workflow and Workflow State. Read the exact live schema and records that matter.

For access work, distinguish:

- desk users from website users;
- roles from role profiles;
- DocType action permissions from field permission levels;
- user permissions and defaults from role permissions;
- page/report access from document access;
- workspace visibility from authorization;
- inherited standard permissions from customized permissions.

Never assign every role as a generic solution. Build the minimum coherent role profile for the
person's job, preserve separation of duties, and test effective access using the intended user.

## High-impact controls

Always show and obtain explicit approval for changes to users, enabled state, roles, role profiles,
permissions, 2FA, API access, email accounts, workflows, global/system defaults, naming, fiscal
settings, company structure, translations affecting live labels, or workspace publication.

Before access changes, capture current assignments and effective restrictions. Afterward, read them
back and, where possible, verify a permitted and a forbidden operation as the affected user.
Never reveal password hashes, reset links, OAuth secrets, SMTP credentials, API secrets, or other
authentication fields.

Company deletion, transaction deletion tools, fiscal-year changes, immutable-ledger settings,
currency changes, and broad permission resets require a backup/rollback plan and separate,
unambiguous approval. Prefer a new corrective configuration over destructive history rewrites.
