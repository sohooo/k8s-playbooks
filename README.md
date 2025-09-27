# RKE2 Cluster Playbooks

This repository provides Ansible resources for operating Rancher Kubernetes Engine 2 (RKE2) clusters. It currently includes:

- An inventory describing the `kube-alpha` and `kube-bravo` clusters with simple host definitions and a `control_plane` tag applied to scheduler nodes.
- A maintenance playbook that drains, updates, reboots, and uncordons each host one at a time, ensuring control-plane nodes are serviced before workers.

## Repository layout

```
.
├── inventories/
│   └── hosts.yml          # Static inventory for kube-alpha and kube-bravo
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
ansible-inventory -i inventories/hosts.yml --graph
```

Run the maintenance workflow against both clusters:

```bash
ansible-playbook -i inventories/hosts.yml playbooks/maintenance.yml
```

Limit execution to a specific cluster:

```bash
ansible-playbook -i inventories/hosts.yml playbooks/maintenance.yml --limit kube_alpha
```

You can also target a single host:

```bash
ansible-playbook -i inventories/hosts.yml playbooks/maintenance.yml --limit kube07
```

> **Note:** Each play runs with `serial: 1`, ensuring maintenance actions complete on one node before moving on to the next.
