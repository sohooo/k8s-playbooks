# Inventory Conventions

The repository ships with a static inventory located at [`inventories/hosts.ini`](../inventories/hosts.ini). It is organised to make individual clusters easy to target while keeping per-host metadata minimal. Companion defaults live in [`inventories/group_vars/all.yml`](../inventories/group_vars/all.yml).

## Group layout

- Each `kube_<name>` group represents a single RKE2 cluster and sets `kube_cluster`.
- Control-plane nodes live in a dedicated `<cluster>_control_plane` child group. `group_vars/all.yml` derives the `kube_control_plane_group` variable from the cluster name so helper tasks can discover the correct hosts.
- Worker nodes live in a matching `<cluster>_workers` child group. The companion `kube_worker_group` variable is derived in the same way.
- Global `kube_control_plane` and `kube_workers` aggregate groups collect the cluster-specific children, expose role facts (such as `kube_node_is_control_plane`), and feed into a combined `kube_nodes` group used by the maintenance play.

Example excerpt:

```ini
[all:children]
kube_clusters

[kube_clusters:children]
kube_alpha

[kube_alpha:vars]
kube_cluster=kube_alpha

[kube_alpha:children]
kube_alpha_control_plane
kube_alpha_workers

[kube_alpha_control_plane]
kube[01:03]

[kube_alpha_workers]
kube[04:05]

[kube_control_plane:children]
kube_alpha_control_plane

[kube_control_plane:vars]
kube_node_is_control_plane=true

[kube_workers:children]
kube_alpha_workers

[kube_workers:vars]
kube_node_is_control_plane=false

[kube_nodes:children]
kube_control_plane
kube_workers
```

## Targeting hosts

- **Cluster:** `ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube_alpha`
- **Single host:** `ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube02`

The maintenance playbook automatically distinguishes between control-plane and worker roles by looking up the derived `kube_control_plane_group` and `kube_worker_group` variables while also consuming the `kube_node_is_control_plane` fact from the aggregate groups. When creating new clusters, copy an existing section, adjust the host ranges, and ensure the control-plane and worker children are declared so the helper tasks can locate a Kubernetes API delegate and the plays can target the correct hosts.
