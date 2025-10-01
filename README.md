# RKE2 Cluster Playbooks

This repository provides Ansible resources for operating Rancher Kubernetes Engine 2 (RKE2) clusters. It currently includes:

- A readable YAML inventory that organises hosts per cluster and exposes dedicated `server` and `agent` groups.
- A rolling maintenance playbook that drains, updates, reboots, and uncordons each host one at a time, ensuring control-plane
  nodes are serviced before workers.

## Repository layout

```
.
├── docs/                     # Extended documentation and onboarding material
├── inventories/
│   └── hosts.yml             # Static inventory for the managed clusters
├── playbooks/
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

## Usage

Preview the inventory graph:

```bash
ansible-inventory -i inventories/hosts.yml --graph
```

Run the maintenance workflow against a single cluster:

```bash
ansible-playbook -i inventories/hosts.yml playbooks/maintenance.yml --limit kube_alpha
```

You can also target an individual host or a subset of node types:

```bash
ansible-playbook -i inventories/hosts.yml playbooks/maintenance.yml --limit kube02
ansible-playbook -i inventories/hosts.yml playbooks/maintenance.yml --limit "kube_alpha:&server"
ansible-playbook -i inventories/hosts.yml playbooks/maintenance.yml --limit "kube_alpha:&agent"
```

> **Note:** Each play runs with `serial: 1`, ensuring maintenance actions complete on one node before moving on to the next.

### Running ad-hoc commands

Use Ansible ad-hoc commands for quick spot checks or remediation steps without running the full maintenance playbook. The
examples below assume the provided inventory (`inventories/hosts.yml`) and demonstrate common tasks for an RKE2 cluster.

Check the Kubernetes control-plane versions by running `kubectl` on every server node:

```bash
ansible -i inventories/hosts.yml 'kube_alpha:&server' \
  -m ansible.builtin.command \
  -a 'kubectl version --short'
```

Confirm that the RKE2 services are healthy on both control-plane and worker nodes:

```bash
ansible -i inventories/hosts.yml 'kube_alpha:&server' \
  -m ansible.builtin.command \
  -a 'systemctl is-active rke2-server'

ansible -i inventories/hosts.yml 'kube_alpha:&agent' \
  -m ansible.builtin.command \
  -a 'systemctl is-active rke2-agent'
```

Inspect Kubernetes node conditions from a single control-plane host and filter by the `Ready` status:

```bash
ansible -i inventories/hosts.yml kube01 \
  -m ansible.builtin.shell \
  -a "kubectl get nodes --no-headers | awk '{print \$1, \$2}'"
```

Collect the current pod scheduling pressure across namespaces to identify hotspots:

```bash
ansible -i inventories/hosts.yml 'kube_alpha:&server' \
  -m ansible.builtin.shell \
  -a "kubectl get pods -A --field-selector=status.phase!=Running"
```

> **Tip:** Add `-b` when commands require privilege escalation and append `--limit <subset>` to further constrain the target
> hosts.

## Verification

After making changes to the playbooks or inventory, run the following commands from an activated virtual environment to ensure
the content remains valid. When modifying `inventories/hosts.yml`, validate the rendered inventory against the schema before
committing so structural regressions are caught early:

```bash
# Verify inventory structure matches the required schema
python scripts/validate_inventory.py

# Validate the inventory loads correctly
ansible-inventory -i inventories/hosts.yml --graph

# Lint the playbook content
ansible-lint playbooks/maintenance.yml

# Perform a syntax check without connecting to any hosts
ansible-playbook -i inventories/hosts.yml playbooks/maintenance.yml --syntax-check
```
