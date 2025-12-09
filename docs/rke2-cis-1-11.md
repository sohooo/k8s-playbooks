# RKE2 CIS 1.11 Hardening Playbook

This playbook applies the controls from the [RKE2 CIS 1.11 Self-Assessment Guide](https://docs.rke2.io/security/cis_self_assessment111) and can also be run in check mode to audit an existing cluster. The role focuses on reproducible system configuration, idempotent file permissions, and lightweight reporting of deviations.

## Inventory targeting

The playbook assumes the static inventory found at `inventories/hosts.ini`. Target all nodes with `kube_nodes` or restrict to control-plane or worker nodes with `kube_control_plane` and `kube_workers`.

## Running in audit (noop) mode

Use Ansible check mode to view the current cluster state without changing it:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/rke2-cis-hardening.yml --check
```

The audit summary reports any sysctl or file permission mismatches against the CIS profile.

## Applying the CIS profile

Run the playbook normally to apply the hardening settings:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/rke2-cis-hardening.yml
```

Use `-e rke2_cis_1_11_apply=false` to skip remediation tasks while still generating the audit report.

## Customizing controls

All knobs live in `roles/rke2_cis_1_11/defaults/main.yml`:

- `rke2_cis_1_11_sysctl_overrides` manages kernel and networking tunables and writes them to `/etc/sysctl.d/60-rke2-cis.conf`.
- `rke2_cis_1_11_config` renders a drop-in at `/etc/rancher/rke2/config.yaml.d/90-cis-profile.yaml` with hardened API server, controller manager, scheduler, kubelet, and kube-proxy arguments.
- `rke2_cis_1_11_file_permissions` defines permission expectations for sensitive RKE2 assets.
- `rke2_cis_1_11_audit_policy_path` controls where the managed audit policy is written; update the template at `roles/rke2_cis_1_11/templates/audit-policy.yaml.j2` if you need finer-grained logging.

## Tags

- `cis` covers the full role
- `harden` limits execution to remediation tasks
- `audit` limits execution to the reporting steps
