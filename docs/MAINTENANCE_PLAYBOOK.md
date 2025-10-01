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

## Troubleshooting stuck drains

`kubectl drain` can wait indefinitely when pods refuse eviction. The playbook now exposes several variables to tune that behaviour:

- `kube_drain_include_daemonsets` (default: `false`) – When set to `true` the command renders `--ignore-daemonsets=false`, which forces the drain to wait for daemonset-managed pods. Because daemonsets are typically recreated immediately, the drain will appear to hang unless the daemonset is scaled to zero first.
- `kube_drain_delete_emptydir_data` (default: `true`) – Enables `--delete-emptydir-data` so pods using `emptyDir` volumes are terminated instead of blocking the drain.
- `kube_drain_timeout` (default: `10m`) – Maps to the native `--timeout` flag on `kubectl drain` to abort the operation when the grace period expires. The timeout must include a unit (e.g. `5m`, `30s`).
- `kube_kubectl_command_timeout` (default: `900`) – Caps the runtime of every delegated `kubectl` invocation to prevent the Ansible task itself from running forever if the client hangs or loses connectivity.

When a drain times out or hangs, take the following recovery steps:

1. Inspect which pods are blocking the drain with `kubectl get pods -A --field-selector spec.nodeName=<node> -o wide`. Daemonset pods must be deleted by scaling the owning daemonset to zero or by temporarily disabling the drain option that includes them.
2. Check for pod disruption budgets (`kubectl get pdb -A`) that may prevent voluntary disruption. Temporarily raise their `maxUnavailable` or delete them while maintenance is in progress.
3. If the playbook aborted midway, run `kubectl uncordon <node>` to restore scheduling and return the cluster to a healthy state before retrying.
4. After resolving the blockers, rerun the maintenance play. The drain task will respect the configured timeouts and fail fast when pods are still preventing eviction, allowing manual intervention without leaving the node cordoned indefinitely.
