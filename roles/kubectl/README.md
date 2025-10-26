# kubectl role

Encapsulates common `kubectl` operations that the playbooks execute against an
RKE2 cluster. Instead of sprinkling ad-hoc command tasks throughout playbooks,
include this role and choose an action with `kubectl_action`.

## Supported actions

| Action              | Description |
| ------------------- | ----------- |
| `get_cordon_status` | Query whether the target node is marked unschedulable. |
| `cordon`            | Mark the node unschedulable. |
| `drain`             | Drain pods from the node with configurable handling for DaemonSets and emptyDir data. |
| `uncordon`          | Mark the node schedulable again. |

## Usage

```yaml
- name: Ensure the node is cordoned before maintenance
  ansible.builtin.include_role:
    name: kubectl
  vars:
    kubectl_action: cordon
    kubectl_node: "{{ inventory_hostname }}"
```

All actions default to operating on the current inventory host, delegating
`kubectl` through `kube_kubectl_delegate`, and updating the
`kube_node_is_cordoned` fact so existing logic can continue to reference it.
Fine-grained behaviour (timeouts, drain flags, etc.) is configurable via role
variables documented in `defaults/main.yml`. By default the drain action keeps
DaemonSet pods running by passing `--ignore-daemonsets=false`.
