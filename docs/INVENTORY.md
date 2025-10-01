# Inventory Conventions

The repository ships with a static inventory located at [`inventories/hosts.yml`](../inventories/hosts.yml). It is organised to
make individual clusters easy to target while keeping per-host metadata minimal.

## Group layout

- Each `kube_<name>` group represents a single RKE2 cluster.
- Every cluster sets the `kube_cluster` variable so plays can enforce that maintenance only targets one cluster at a time.
- Each cluster lists every node directly under its `hosts` key while setting `kube_cluster` so host variables inherit the
  cluster name.
- Control-plane nodes inside a cluster set `kube_control_plane: true`. Worker nodes omit the flag.

Example excerpt:

```yaml
all:
  children:
    kube_alpha:
      vars:
        kube_cluster: kube_alpha
      hosts:
        kube01:
          kube_control_plane: true
        kube02:
          kube_control_plane: true
        kube03:
          kube_control_plane: true
        kube04:
        kube05:
```

## Targeting hosts

- **Cluster:** `ansible-playbook -i inventories/hosts.yml playbooks/maintenance.yml --limit kube_alpha`
- **Single host:** `ansible-playbook -i inventories/hosts.yml playbooks/maintenance.yml --limit kube02`

The maintenance playbook automatically distinguishes between control-plane and worker roles by checking the
`kube_control_plane` host variable, so no additional helper groups are required. When creating new clusters, copy an existing
section and adjust the hostnames. Keep the naming consistent to simplify filtering and monitoring.
