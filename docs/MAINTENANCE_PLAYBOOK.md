# Maintenance Playbook Reference

The `playbooks/maintenance.yml` file is the primary entry point for scheduled upkeep of the RKE2 clusters. It is intentionally
simple: the file contains two plays that re-use the same task sequence so that control-plane nodes are completed before worker
nodes.

## Execution order

1. **Control-plane play** – Targets every host but immediately skips nodes without `controlplane=true`. With `serial: 1` the play
   finishes maintenance on one control-plane node before moving on to the next.
2. **Worker play** – Runs the exact same maintenance sequence for the remaining nodes, again processing them one at a time.

The separation into two plays keeps the orchestration logic obvious: control-plane availability is prioritised without having to
manage custom host groups or delegate logic to external tooling.

## Task sequence

The shared implementation lives in [`playbooks/tasks/maintenance_sequence.yml`](../playbooks/tasks/maintenance_sequence.yml). It
executes the following steps:

1. **Check cordon status** – Captures whether the node is already cordoned to avoid double-draining.
2. **Drain if required** – Runs `kubectl drain` only when the node was schedulable.
3. **Puppet maintenance** – Imports [`common/puppet_agent.yml`](../playbooks/tasks/common/puppet_agent.yml) to run the Puppet
   agent in test mode and fail on unexpected issues.
4. **OS updates** – Imports [`common/dnf_update.yml`](../playbooks/tasks/common/dnf_update.yml) to upgrade packages when updates
   are available.
5. **Reboot** – Imports [`common/reboot.yml`](../playbooks/tasks/common/reboot.yml) to restart the host and wait for it to come
   back online.
6. **Post-maintenance cordon check** – Confirms whether the node is still cordoned.
7. **Uncordon if needed** – Runs `kubectl uncordon` when the previous check reports that the node remains unschedulable.

Each command task has explicit `failed_when` rules so that unexpected return codes surface immediately.

## Extending the workflow

- Add new tasks to `maintenance_sequence.yml` to keep the control-plane/worker orchestration intact.
- For optional steps, prefer wrapping the included tasks in `block` statements with clear conditionals so the behaviour remains
  discoverable.
- When a new maintenance action requires additional variables, document them in the task file and consider providing defaults in
  `group_vars`.

Keeping the main playbook compact and delegating the implementation to a shared task file preserves readability while making it
straightforward to add new capabilities.
