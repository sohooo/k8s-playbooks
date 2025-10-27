# RKE2 Cluster Playbooks

This repository provides Ansible resources for operating Rancher Kubernetes Engine 2 (RKE2) clusters. It currently includes:

- A readable INI inventory that organises hosts per cluster with dedicated control-plane and worker groups for targeted plays.
- A rolling maintenance playbook that drains, updates, reboots, and uncordons each host one at a time, using inventory ordering
  to service control-plane nodes before workers.
- A GPU labelling playbook that detects NVIDIA hardware on each node and applies `gpu=on` or `gpu=off` Kubernetes labels so
  every node is consistently marked for GPU scheduling frameworks such as [HAMi](https://github.com/Project-HAMi/HAMi).
- A trace kit playbook that gathers multi-node network traces, cluster diagnostics, and packages the findings for
  SRE or vendor escalation.

## Repository layout

```
.
├── docs/                     # Extended documentation and onboarding material
├── inventories/
│   └── hosts.ini             # Static inventory for the managed clusters
├── playbooks/
│   ├── label-gpu-nodes.yml   # Apply the gpu=on label to hosts with NVIDIA hardware
│   ├── maintenance.yml       # Entry point for the maintenance workflow
│   ├── trace-kit.yml        # Collect in-depth diagnostics for incident response
│   └── tasks/
│       └── common/           # Re-usable task snippets for maintenance actions
└── scripts/
    └── setup-ansible.sh      # Helper script to create the tooling virtual environment
```

See [`docs/README.md`](docs/README.md) for deep dives into the playbook internals, inventory conventions, and onboarding steps.

## Requirements

- Ansible 2.12+ (tested syntax)
- Access to the target nodes with privilege escalation (`become`)
- `kubectl` available on control-plane nodes (worker nodes delegate Kubernetes operations to a
  control-plane host discovered during the kubectl role's setup helpers)

## Local development setup

Set up a local Python virtual environment and install Ansible along with the linting tools used by the repository by running the
helper script:

```bash
./scripts/setup-ansible.sh
source .venv/bin/activate
```

> The script creates a `.venv` directory in the repository by default. You can change the location by setting the `VENV_DIR`
> environment variable before running it.

Confirm the installation succeeded:

```bash
ansible --version
ansible-lint --version
```

> **Tip:** Activate the virtual environment (`source .venv/bin/activate`) in every new shell before running the commands below so
> that the installed tooling is available.

Ensure the selected kubectl delegate (a control-plane host discovered during the kubectl setup helpers) can reach the Kubernetes API and has `kubectl` available in `/var/lib/rancher/rke2/bin`.

## Usage

Preview the inventory graph:

```bash
ansible-inventory -i inventories/hosts.ini --graph
```

Run the maintenance workflow against a single cluster. The playbook targets the combined `kube_nodes` group and, thanks to the
inventory ordering, finishes the control-plane hosts before moving on to workers:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube_alpha
```

> The play consumes the global `kube_nodes` aggregate (which includes `kube_control_plane` and `kube_workers`). Use `--limit <cluster>` to
> narrow execution to a single cluster so the helper tasks can derive the correct delegate facts.

You can also target an individual host or a subset of node types:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube02
```

> **Note:** Each play runs with `serial: 1`, ensuring maintenance actions complete on one node before moving on to the next.

Apply the GPU labels so that every node advertises whether a GPU is available. These labels are required when integrating with
[HAMi](https://github.com/Project-HAMi/HAMi).

```bash
ansible-playbook -i inventories/hosts.ini playbooks/label-gpu-nodes.yml --limit kube_alpha
```

Run the trace kit to capture network probes, Kubernetes object state, and component logs. Provide
`trace_kit_targets` and optionally `trace_kit_flagged_namespaces` or restart lists (`trace_kit_restart_resources`) in an `extra-vars` file to customise the collection run:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/trace-kit.yml \
  --limit kube_alpha \
  -e @vars/trace-kit.yaml
```

The play creates a timestamped archive under `artifacts/trace-kit/` containing per-node tests, cluster-wide
events, pod logs (including CNI, kube-proxy, and CoreDNS), optional workload restarts, and workload manifests for reproducing
failures in a test environment.

When Longhorn is installed, trace kit gathers detailed diagnostics under `cluster/longhorn/`. It records high-level status
tables for volumes, replicas, engines, nodes, share managers, and PersistentVolumes, captures the underlying custom resource
manifests, and stores namespace events alongside `kubectl describe` output for every Longhorn pod. The role also tails pod
logs grouped by component so you can quickly inspect manager, driver deployer, webhook, or instance manager activity. To help
surface storage issues, the run highlights PersistentVolumes stuck in problematic phases (`Pending`, `Available`, `Released`,
or `Failed`) or terminating and preserves both their manifests and `kubectl describe` output for root-cause analysis. Tune
the behaviour with variables such as `trace_kit_capture_longhorn`, `trace_kit_longhorn_namespace`,
`trace_kit_longhorn_status_commands`, `trace_kit_longhorn_resource_types`, `trace_kit_longhorn_trace_components`, and
`trace_kit_longhorn_problematic_pv_phases`.

#### Reproducing failed workloads in a test cluster

1. Extract the generated tarball on your workstation:

   ```bash
   tar -xzf artifacts/trace-kit/trace-kit-<run_id>.tar.gz \
     -C artifacts/trace-kit/
   ```

2. Review the extracted `cluster/reproduction/` directory. It contains:

   - `pods/`: pod manifests captured for every workload stuck outside the `Running` phase.
   - `owners/`: controller manifests (ReplicaSets, Deployments, StatefulSets, DaemonSets, Jobs, etc.) that manage the failed
     pods. ReplicaSet owners automatically include their parent Deployment manifests so application rollouts can be replayed.

3. Apply the manifests against a non-production cluster to recreate the workload state:

   ```bash
   kubectl apply -f cluster/reproduction/owners/
   kubectl apply -f cluster/reproduction/pods/
   ```

   > **Tip:** Apply the controller manifests first (`owners/`) so the controllers manage subsequent pod lifecycles. Use a
   > purpose-built namespace or cluster to avoid impacting production workloads.

### Running ad-hoc commands

Use Ansible ad-hoc commands for quick spot checks or remediation steps without running the full maintenance playbook. The
examples below assume the provided inventory (`inventories/hosts.ini`) and demonstrate common tasks for an RKE2 cluster. Adjust
the `--limit` values to match the hosts you want to target.

Check the Kubernetes control-plane versions by running `kubectl` on every server node in the `kube_alpha` cluster:

```bash
ansible -i inventories/hosts.ini kube_alpha \
  --limit 'kube01,kube02,kube03' \
  -m ansible.builtin.command \
  -a 'kubectl version --short'
```

Confirm that the RKE2 services are healthy on control-plane and worker nodes:

```bash
ansible -i inventories/hosts.ini kube_alpha \
  --limit 'kube01,kube02,kube03' \
  -m ansible.builtin.command \
  -a 'systemctl is-active rke2-server'

ansible -i inventories/hosts.ini kube_alpha \
  --limit 'kube04,kube05' \
  -m ansible.builtin.command \
  -a 'systemctl is-active rke2-agent'
```

Inspect Kubernetes node conditions from a single control-plane host and filter by the `Ready` status:

```bash
ansible -i inventories/hosts.ini kube_alpha \
  --limit kube01 \
  -m ansible.builtin.shell \
  -a "kubectl get nodes --no-headers | awk '{print \$1, \$2}'"
```

Collect the current pod scheduling pressure across namespaces to identify hotspots:

```bash
ansible -i inventories/hosts.ini kube_alpha \
  --limit kube01 \
  -m ansible.builtin.shell \
  -a "kubectl get pods -A --field-selector=status.phase!=Running"
```

> **Tip:** Add `-b` when commands require privilege escalation and adjust `--limit` to narrow the target hosts.

## Verification

After making changes to the playbooks or inventory, run the following commands from an activated virtual environment to ensure
the content remains valid:

```bash
# Validate the inventory loads correctly
ansible-inventory -i inventories/hosts.ini --graph

# Lint the playbook content
ansible-lint playbooks/maintenance.yml

# Perform a syntax check without connecting to any hosts
ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --syntax-check
```
