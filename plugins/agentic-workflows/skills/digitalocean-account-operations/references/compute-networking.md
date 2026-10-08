# DigitalOcean browser compute and networking

Use the control panel for Droplets, VPCs, firewalls, load balancers, reserved IPs,
images/snapshots, SSH-key management, and resource actions.

1. Verify the browser team/account/project, resource ID/name, and region.
2. Inspect size/image/VPC, tags, firewall rules, forwarding/health checks, IPs,
   project association, and pending actions as applicable.
3. Check downtime, replacement behavior, billing/capacity, dependencies, and recovery.
   For rebuilding/deletion, verify backups when recovery is expected.
4. Follow [change management](change-management.md) and use UI resource/settings
   controls. Firewall previews identify every protocol/port/address/target.
5. Wait for terminal operation status, reopen settings, and verify network/workload
   health separately. A completed provider action does not prove application health.

Optional doctl reads may supplement status after independent identity and target
matching. They do not authorize resize, reboot, rebuild, create, update, or delete.
