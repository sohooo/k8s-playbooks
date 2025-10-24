# RKE2 Cluster Playbooks

This repository provides Ansible resources for operating Rancher Kubernetes Engine 2 (RKE2) clusters. It currently includes:

- A readable INI inventory that organises hosts per cluster while using host variables to distinguish control-plane nodes.
- A rolling maintenance playbook that drains, updates, reboots, and uncordons each host one at a time, ensuring control-plane
  nodes are serviced before workers.
- A GPU labelling playbook that detects NVIDIA hardware on each node and applies `gpu=on` or `gpu=off` Kubernetes labels so
  every node is consistently marked for GPU scheduling frameworks such as [HAMi](https://github.com/Project-HAMi/HAMi).

## Repository layout

```
.
├── docs/                     # Extended documentation and onboarding material
├── inventories/
│   └── hosts.ini             # Static inventory for the managed clusters
├── playbooks/
│   ├── label-gpu-nodes.yml   # Apply the gpu=on label to hosts with NVIDIA hardware
│   ├── maintenance.yml       # Entry point for the maintenance workflow
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
  control-plane host)
- The [`community.kubernetes`](https://galaxy.ansible.com/community/kubernetes) collection and its
  Python dependencies (`kubernetes`, `openshift`) installed in the execution environment

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

Install the required Ansible collections so the playbooks can use the Kubernetes modules without
shelling out to `kubectl` manually:

```bash
ansible-galaxy collection install -r collections/requirements.yml
```

> **Tip:** Activate the virtual environment (`source .venv/bin/activate`) in every new shell before running the commands below so
> that the installed tooling is available.

## Usage

Preview the inventory graph:

```bash
ansible-inventory -i inventories/hosts.ini --graph
```

Run the maintenance workflow against a single cluster:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube_alpha
```

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
