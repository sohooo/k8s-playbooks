# Maintenance Playbook Reference

The `playbooks/maintenance.yml` file is the primary entry point for scheduled upkeep of the RKE2 clusters. It contains two plays that share the same maintenance block while using the inventory `controlplane` host variable to steer execution.

## Execution order

1. **Server play** – Targets every host in the inventory but immediately skips nodes without `controlplane=true`. With `serial: 1` the play finishes maintenance on one server before moving on to the next.
2. **Agent play** – Runs the same sequence for worker nodes. Each host skips itself when `controlplane=true` and discovers the appropriate server delegate by intersecting its cluster membership with hosts that expose the `controlplane` flag.

The separation into two plays keeps the orchestration logic obvious while the shared host variable avoids maintaining parallel groups in the inventory.

## Task sequence

Both plays embed the same maintenance block directly in the playbook so that the workflow remains visible without chasing extra task files. The block executes the following steps:

1. **Check cordon status** – Captures whether the node is already cordoned to avoid double-draining.
2. **Drain if required** – Runs `kubectl drain` only when the node was schedulable.
3. **Puppet maintenance** – Imports [`common/puppet_agent.yml`](../playbooks/tasks/common/puppet_agent.yml) to run the Puppet agent in test mode and fail on unexpected issues.
4. **OS updates** – Imports [`common/dnf_update.yml`](../playbooks/tasks/common/dnf_update.yml) to upgrade packages when updates are available.
5. **Reboot** – Imports [`common/reboot.yml`](../playbooks/tasks/common/reboot.yml) to restart the host and wait for it to come back online.
6. **Post-maintenance cordon check** – Confirms whether the node is still cordoned.
7. **Uncordon if needed** – Runs `kubectl uncordon` when the previous check reports that the node remains unschedulable.

Each command task has explicit `failed_when` rules so that unexpected return codes surface immediately.

> **Delegation note:** RKE2 worker nodes do not ship with `kubectl` or a KUBECONFIG. The playbook therefore
> delegates every Kubernetes command to a control-plane host within the same cluster whenever the current
> target lacks the tooling. This keeps the maintenance workflow functional across all node types while
> preserving the node-specific scheduling logic.

## Extending the workflow

- Add new steps to the maintenance block in `playbooks/maintenance.yml` so the server and agent plays stay in sync.
- For optional steps, prefer wrapping the included tasks in `block` statements with clear conditionals so the behaviour remains discoverable.
- When a new maintenance action requires additional variables, document them in the task file and consider providing defaults in `group_vars`.

Keeping the main playbook compact and delegating the implementation to a shared task file preserves readability while making it straightforward to add new capabilities.
