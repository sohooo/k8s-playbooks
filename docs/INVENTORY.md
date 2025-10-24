# Inventory Conventions

The repository ships with a static inventory located at [`inventories/hosts.ini`](../inventories/hosts.ini). It is organised to make individual clusters easy to target while keeping per-host metadata minimal.

## Group layout

- Each `kube_<name>` group represents a single RKE2 cluster.
- Every cluster sets the `kube_cluster` variable so plays can enforce that maintenance only targets one cluster at a time.
- Control-plane nodes live in a dedicated `<cluster>_control_plane` child group referenced by the `kube_control_plane_group`
  variable.
- Worker nodes live in a matching `<cluster>_workers` child group referenced by the `kube_worker_group` variable.
- Global `kube_control_plane` and `kube_workers` aggregate groups collect the cluster-specific children so shared playbooks can
  target each role while `--limit` narrows execution to a single cluster.

Example excerpt:

```ini
[all:children]
kube_alpha

[kube_alpha:vars]
kube_cluster=kube_alpha
kube_control_plane_group=kube_alpha_control_plane
kube_worker_group=kube_alpha_workers

[kube_alpha:children]
kube_alpha_control_plane
kube_alpha_workers

[kube_alpha_control_plane]
kube01
kube02
kube03

[kube_alpha_workers]
kube04
kube05

[kube_control_plane:children]
kube_alpha_control_plane

[kube_workers:children]
kube_alpha_workers
```

## Targeting hosts

- **Cluster:** `ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube_alpha`
- **Single host:** `ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube02`

The maintenance playbook automatically distinguishes between control-plane and worker roles by looking up
the `kube_control_plane_group` and `kube_worker_group` variables defined for each cluster. When creating new
clusters, copy an existing section, adjust the hostnames, and create the companion control-plane and worker
groups so the helper tasks can locate a Kubernetes API delegate and the plays can target the correct hosts.
