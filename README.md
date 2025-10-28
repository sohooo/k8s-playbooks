# RKE2 Cluster Playbooks

This repository provides Ansible resources for operating Rancher Kubernetes Engine 2 (RKE2) clusters. It currently includes:

- A readable INI inventory that organises hosts per cluster with dedicated control-plane and worker groups for targeted plays.
- A rolling maintenance playbook that drains, updates, reboots, and uncordons each host one at a time, using inventory ordering to service control-plane nodes before workers.
- A GPU labelling playbook that detects NVIDIA hardware on each node and applies `gpu=on` or `gpu=off` Kubernetes labels so every node is consistently marked for GPU scheduling frameworks such as [HAMi](https://github.com/Project-HAMi/HAMi).
- A trace kit playbook that gathers multi-node network traces, cluster diagnostics, and packages the findings for SRE or vendor escalation.

See [`docs/README.md`](docs/README.md) for deep dives into playbook internals, inventory conventions, and onboarding material.

## Repository layout

```
.
├── docs/                     # Extended documentation and onboarding material
├── inventories/
│   └── hosts.ini             # Static inventory for the managed clusters
├── playbooks/
│   ├── label-gpu-nodes.yml   # Apply the gpu=on label to hosts with NVIDIA hardware
│   ├── maintenance.yml       # Entry point for the maintenance workflow
│   ├── trace-kit.yml         # Collect in-depth diagnostics for incident response
│   └── tasks/
│       └── common/           # Re-usable task snippets for maintenance actions
└── scripts/
    └── setup-ansible.sh      # Helper script to create the tooling virtual environment
```

## Requirements

- Ansible 2.12+ (tested syntax)
- Access to the target nodes with privilege escalation (`become`)
- `kubectl` available on control-plane nodes (worker nodes delegate Kubernetes operations to a control-plane host discovered during the kubectl role's setup helpers)

## Get Started

The checklist below summarises the onboarding workflow. Follow the [Day 1 setup guide](docs/ONBOARDING.md#day-1-setup) for the full commands and optional flags.

1. Clone this repository and switch into the project directory.
2. Run `./scripts/setup-ansible.sh` to provision the Python virtual environment and tooling.
3. Activate the environment and confirm Ansible, ansible-lint, and the inventory load correctly.

Keep the virtual environment activated (`source .venv/bin/activate`) in every new shell so the installed tooling remains available. The designated kubectl delegate (a control-plane host discovered during the kubectl helpers) must be able to reach the Kubernetes API and expose `kubectl` under `/var/lib/rancher/rke2/bin`.

## Usage

### Maintenance workflow

Run the maintenance workflow against a single cluster. The playbook targets the combined `kube_nodes` group and, thanks to the inventory ordering, finishes the control-plane hosts before moving on to workers:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube_alpha
```

> The play consumes the global `kube_nodes` aggregate (which includes `kube_control_plane` and `kube_workers`). Use `--limit <cluster>` to narrow execution to a single cluster so the helper tasks can derive the correct delegate facts.

You can also target an individual host or a subset of node types:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube02
```

> **Note:** Each play runs with `serial: 1`, ensuring maintenance actions complete on one node before moving on to the next.

### GPU labelling

Apply the GPU labels so that every node advertises whether a GPU is available. These labels are required when integrating with [HAMi](https://github.com/Project-HAMi/HAMi).

```bash
ansible-playbook -i inventories/hosts.ini playbooks/label-gpu-nodes.yml --limit kube_alpha
```

### Trace kit overview

Use the trace kit to capture network probes, Kubernetes object state, and component logs for escalations:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/trace-kit.yml \
  --limit kube_alpha \
  -e @vars/trace-kit.yaml
```

Start by copying [`vars/trace-kit.example.yml`](vars/trace-kit.example.yml) to `vars/trace-kit.yaml` and tailor the values for
your cluster. Read the [trace kit guide](docs/TRACE_KIT.md) for variable details, storage layout, and Longhorn-specific capture
behaviour.

### Running ad-hoc commands

Use Ansible ad-hoc commands for quick spot checks or remediation steps without running the full maintenance playbook. The examples below assume the provided inventory (`inventories/hosts.ini`) and demonstrate common tasks for an RKE2 cluster. Adjust the `--limit` values to match the hosts you want to target.

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

After making changes to the playbooks or inventory, run the following commands from an activated virtual environment to ensure the content remains valid:

```bash
# Validate the inventory loads correctly
ansible-inventory -i inventories/hosts.ini --graph

# Lint the playbook content
ansible-lint playbooks/maintenance.yml

# Perform a syntax check without connecting to any hosts
ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --syntax-check
```
