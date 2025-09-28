# Inventory Conventions

The repository ships with a static inventory located at [`inventories/hosts.ini`](../inventories/hosts.ini). It is organised to
make clusters easy to target while keeping per-host metadata minimal.

## Group layout

- Each `[kube_<name>]` section represents a single RKE2 cluster.
- Within a cluster, hosts that run the control plane are annotated with the host variable `controlplane=true`.
- Worker nodes are listed without additional variables.

Example excerpt:

```ini
[kube_alpha]
kube01 controlplane=true
kube02 controlplane=true
kube03 controlplane=true
kube04
kube05
```

## Targeting hosts

- **Entire fleet:** `ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml`
- **Specific cluster:** `ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube_alpha`
- **Single host:** `ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube07`
- **All control-plane nodes:** `ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit 'all[?controlplane]'`

When creating new clusters, copy an existing section and adjust the hostnames. Keep the naming consistent to simplify filtering
and monitoring.
