# RKE2 Cluster Playbooks

This repository provides Ansible resources for operating Rancher Kubernetes Engine 2 (RKE2) clusters. It currently includes:

- A static INI inventory organised per cluster with control-plane nodes flagged via `controlplane=true`.
- A rolling maintenance playbook that drains, updates, reboots, and uncordons each host one at a time, ensuring control-plane
  nodes are serviced before workers.

## Repository layout

```
.
├── docs/                     # Extended documentation and onboarding material
├── inventories/
│   └── hosts.ini             # Static inventory for the managed clusters
├── playbooks/
│   ├── maintenance.yml       # Entry point for the maintenance workflow
│   └── tasks/
│       ├── common/           # Re-usable task snippets for maintenance actions
│       └── maintenance_sequence.yml
└── scripts/
    └── setup-ansible.sh      # Helper script to create the tooling virtual environment
```

See [`docs/README.md`](docs/README.md) for deep dives into the playbook internals, inventory conventions, and onboarding steps.

## Requirements

- Ansible 2.12+ (tested syntax)
- Access to the target nodes with privilege escalation (`become`)
- `kubectl` available on the nodes being maintained

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
ansible-inventory -i inventories/hosts.ini --graph
```

Run the maintenance workflow against both clusters:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml
```

Limit execution to a specific cluster:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube_alpha
```

You can also target a single host:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube07
```

To work only on control-plane hosts across clusters, limit the run by their host variable:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit 'all[?controlplane]'
```

> **Note:** Each play runs with `serial: 1`, ensuring maintenance actions complete on one node before moving on to the next.

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
