# RKE2 Cluster Playbooks

This repository provides Ansible resources for operating Rancher Kubernetes Engine 2 (RKE2) clusters. It currently includes:

- An INI inventory that defines a section per cluster and flags control-plane nodes with `controlplane=true`.
- A maintenance playbook that drains, updates, reboots, and uncordons each host one at a time, ensuring control-plane nodes are serviced before workers.

## Repository layout

```
.
├── inventories/
│   └── hosts.ini          # Static inventory for kube-alpha and kube-bravo
└── playbooks/
    └── maintenance.yml    # Rolling maintenance workflow
```

## Requirements

- Ansible 2.12+ (tested syntax)
- Access to the target nodes with privilege escalation (`become`)
- `kubectl` available on the nodes being maintained

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
