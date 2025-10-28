# Trace Kit Guide

The trace kit playbook collects cluster diagnostics, node-level traces, and optional workload restarts to accelerate incident response and escalations.

## Run the playbook

Execute the playbook against the relevant cluster and provide customisation variables with an extra-vars file:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/trace-kit.yml \
  --limit kube_alpha \
  -e @vars/trace-kit.yaml
```

Define the targets and optional namespaces or restart lists in the variable file:

- `trace_kit_targets` – the hosts to probe.
- `trace_kit_flagged_namespaces` – namespaces that need deeper inspection.
- `trace_kit_restart_resources` – workloads that should be restarted during collection.

## What gets captured

Each run creates a timestamped archive under `artifacts/trace-kit/` containing per-node network tests, cluster-wide events, pod logs (including CNI, kube-proxy, and CoreDNS), optional workload restarts, and workload manifests for reproducing failures in a test environment.

When Longhorn is installed, trace kit gathers detailed diagnostics under `cluster/longhorn/`. It records high-level status tables for volumes, replicas, engines, nodes, share managers, and PersistentVolumes, captures the underlying custom resource manifests, and stores namespace events alongside `kubectl describe` output for every Longhorn pod. The role also tails pod logs grouped by component so you can quickly inspect manager, driver deployer, webhook, or instance manager activity. To help surface storage issues, the run highlights PersistentVolumes stuck in problematic phases (`Pending`, `Available`, `Released`, or `Failed`) or terminating and preserves both their manifests and `kubectl describe` output for root-cause analysis. Tune the behaviour with variables such as `trace_kit_capture_longhorn`, `trace_kit_longhorn_namespace`, `trace_kit_longhorn_status_commands`, `trace_kit_longhorn_resource_types`, `trace_kit_longhorn_trace_components`, and `trace_kit_longhorn_problematic_pv_phases`.

## Reproduce workloads in a test cluster

1. Extract the generated tarball on your workstation:
   ```bash
   tar -xzf artifacts/trace-kit/trace-kit-<run_id>.tar.gz \
     -C artifacts/trace-kit/
   ```
2. Review the extracted `cluster/reproduction/` directory. It contains:
   - `pods/`: pod manifests captured for every workload stuck outside the `Running` phase.
   - `owners/`: controller manifests (ReplicaSets, Deployments, StatefulSets, DaemonSets, Jobs, etc.) that manage the failed pods. ReplicaSet owners automatically include their parent Deployment manifests so application rollouts can be replayed.
3. Apply the manifests against a non-production cluster to recreate the workload state:
   ```bash
   kubectl apply -f cluster/reproduction/owners/
   kubectl apply -f cluster/reproduction/pods/
   ```
   > **Tip:** Apply the controller manifests first (`owners/`) so the controllers manage subsequent pod lifecycles. Use a purpose-built namespace or cluster to avoid impacting production workloads.
