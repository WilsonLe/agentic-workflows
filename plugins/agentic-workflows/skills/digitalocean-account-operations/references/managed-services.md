# DigitalOcean browser managed services

Verify the control-panel team/account/project/resource/region before any operation.
Apply [change management](change-management.md) and use supported UI controls.

- Kubernetes: inspect cluster version, node pools, autoscaling, maintenance, VPC,
  and status. Upgrades, removal, access, and registry integrations need impact scope.
- Databases: inspect engine/version, size, nodes, maintenance, users, pools,
  firewall, replicas, and status without revealing connection credentials.
  Do not reset passwords or broaden access to test a diagnostic.
- Registry: inspect repositories/tags, subscriptions, cleanup, and integration
  status without exposing generated Docker credentials.
- Spaces: inspect bucket/region/access and relevant metadata through UI. Do not
  assume doctl has full storage coverage or substitute another credential class.

Reopen saved settings and verify healthy terminal state and relevant workload
behavior. Optional read-only CLI diagnostics must independently match browser
identity and target. Missing management UI support needs disclosure and explicit
user direction before any alternative mutation.
