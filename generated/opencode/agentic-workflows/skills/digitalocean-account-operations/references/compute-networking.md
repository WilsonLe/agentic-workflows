# Compute and networking runbook

Apply [authenticated CLI and browser assistance](browser-selection.md): verify
CLI identity and exact project target, authenticate via the built-in browser when
needed, and use browser operations only for an authenticated client capability gap.

Use for Droplets, VPCs, cloud firewalls, load balancers, reserved IPs, images, snapshots, SSH keys,
and resource actions.

## Inspect

1. Start with the relevant group help, such as `doctl compute --help` or
   `doctl compute droplet --help`.
2. List resources in JSON and resolve exact IDs.
3. Capture region, size, image, VPC, tags, firewall rules, load-balancer forwarding rules, health
   checks, IPs, and project association as applicable.
4. Inspect active actions before diagnosing an in-progress or failed operation.

## Plan, apply, and verify

1. Resolve the exact action help and supported flags.
2. Check dependencies, downtime, replacement behavior, billing changes, capacity, region
   availability, and rollback.
3. For firewall changes, state every inbound or outbound protocol, port, address, tag, or resource.
4. For load balancers, preserve forwarding rules, health checks, target Droplets, and traffic
   implications.
5. For destructive or rebuilding actions, verify backups or snapshots exist when the user expects
   recovery.
6. Follow `change-management.md`, wait for asynchronous actions to finish, then re-read the resource
   and verify networking and workload health separately.

Do not treat a successful API action as proof the workload or application is healthy.
