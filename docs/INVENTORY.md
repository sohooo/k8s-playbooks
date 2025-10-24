# Inventory Conventions

The repository ships with a static inventory located at [`inventories/hosts.ini`](../inventories/hosts.ini). It is organised to make individual clusters easy to target while keeping per-host metadata minimal.

## Group layout

- Each `kube_<name>` group represents a single RKE2 cluster.
- Every cluster sets the `kube_cluster` variable so plays can enforce that maintenance only targets one cluster at a time.
- Each cluster lists every node directly under its group while setting `kube_cluster` so host variables inherit the cluster name.
- Control-plane nodes live in a dedicated `<cluster>_control_plane` child group referenced by the `kube_control_plane_group`
  variable. Worker nodes remain only in the parent cluster group.

Example excerpt:

```ini
[all:children]
kube_alpha

[kube_alpha:vars]
kube_cluster=kube_alpha

[kube_alpha]
kube01
kube02
kube03
kube04
kube05

[kube_alpha_control_plane]
kube01
kube02
kube03
```

## Targeting hosts

- **Cluster:** `ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube_alpha`
- **Single host:** `ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube02`

The maintenance playbook automatically distinguishes between control-plane and worker roles by looking up
the `kube_control_plane_group` variable defined for each cluster. When creating new clusters, copy an
existing section, adjust the hostnames, and create the companion control-plane group so the helper tasks
can locate a Kubernetes API delegate.
