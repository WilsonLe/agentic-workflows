# Retired WordPress workflows

The WordPress packages and skills have been removed from this collection. New installations do not include them. This repository update does not modify any site, deployed runtime, content, credential, backup, or external repository.

For an existing installation:

1. Inventory the installed packages, scheduled jobs, connected repositories, and any deployed site runtime. Record the current operator and recovery path before changing local marketplace registrations.
2. Preserve the local configuration, site-specific runbooks, and backups you need under your own retention policy. Do not copy credentials into this repository.
3. Remove retired package installations from Codex or Claude Code when you are ready to stop invoking them. Update automation that calls retired skills. Install the surviving packages using the current marketplace names in the [README](../README.md).
4. Manage any deployed site runtime independently. The source cleanup does not disable it. If you choose to retire a runtime, use its site-specific maintenance process, take a backup, agree a rollback path, and verify the site afterward.
5. Keep existing site monitoring and backups until the replacement operating process is working.

Historical releases remain in Git history. They are outside the current marketplace and receive no new workflow updates here.
