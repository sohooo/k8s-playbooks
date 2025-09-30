# Inventory Conventions

The repository ships with a static inventory located at [`inventories/hosts.yml`](../inventories/hosts.yml). It is organised to
make individual clusters easy to target while keeping per-host metadata minimal.

## Group layout

- Each `kube_<name>` group represents a single RKE2 cluster.
- Cluster groups expose helper variables such as `kube_server_group` so that agent nodes can discover their control-plane
  delegate.
- Inside each cluster the `server` and `agent` child groups keep control-plane and worker nodes separate without introducing
  extra per-cluster helper groups.

Example excerpt:

```yaml
all:
  children:
    kube_alpha:
      vars:
        kube_cluster: kube_alpha
        kube_server_group: server
      children:
        server:
          hosts:
            kube01:
            kube02:
            kube03:
        agent:
          hosts:
            kube04:
            kube05:
```

## Targeting hosts

- **Cluster:** `ansible-playbook -i inventories/hosts.yml playbooks/maintenance.yml --limit kube_alpha`
- **Single host:** `ansible-playbook -i inventories/hosts.yml playbooks/maintenance.yml --limit kube02`
- **Server or agent subset:** Use `--limit server` or `--limit agent` alongside the cluster limit to run only part of the fleet.

When creating new clusters, copy an existing section and adjust the hostnames. Keep the naming consistent to simplify filtering
and monitoring.
