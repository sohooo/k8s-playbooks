# Onboarding Playbook

Use this guide as a Day 1/Day 2 playbook. Day 1 gets your workstation ready to run the playbooks. Day 2 covers the routine actions you will perform while operating RKE2 clusters.

## Day 1 – Environment setup

### 1. Clone the repository

```bash
git clone git@github.com:your-org/k8s-playbooks.git
cd k8s-playbooks
```

> Replace the remote URL with the location of your fork if you are contributing changes.

### 2. Bootstrap the tooling virtual environment

Run the helper script and activate the environment in the same shell:

```bash
./scripts/setup-ansible.sh
source .venv/bin/activate
```

If you prefer to store the virtual environment elsewhere, set `VENV_DIR` before invoking the script:

```bash
VENV_DIR=$HOME/.virtualenvs/k8s-playbooks ./scripts/setup-ansible.sh
source $HOME/.virtualenvs/k8s-playbooks/bin/activate
```

Keep the environment active in every new shell so that the installed tooling remains available.

### 3. Validate the installation

After activation, confirm that both Ansible and the linter are available:

```bash
ansible --version
ansible-lint --version
```

### 4. Explore the inventory

Visualise the cluster layout to confirm your access to managed nodes:

```bash
ansible-inventory -i inventories/hosts.ini --graph
```

If you cannot reach the nodes yet, contact an administrator to obtain SSH access or to have the inventory updated with the appropriate hostnames.

## Day 2 – Routine operations

### 1. Dry-run the maintenance playbook

Run a syntax check to make sure the playbook parses correctly without touching any hosts:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --syntax-check
```

Use this command after any local changes to catch errors before they reach production.

### 2. Execute maintenance safely

Limit execution to the relevant cluster or host and consider `--check` for a preview when tasks support it:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube_alpha
```

Monitor the output for failed tasks and coordinate with the platform engineering team if you encounter unexpected behaviour.

### 3. Label GPU nodes when hardware changes

Run the GPU labelling playbook whenever GPU-capable hosts are added or removed so scheduling metadata stays accurate:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/label-gpu-nodes.yml --limit kube_alpha
```

### 4. Capture diagnostics with the trace kit

Gather cluster-wide diagnostics during incidents or vendor escalations:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/trace-kit.yml \
  --limit kube_alpha \
  -e @vars/trace-kit.yaml
```

Copy [`vars/trace-kit.example.yml`](../vars/trace-kit.example.yml) to `vars/trace-kit.yaml` as a starting point and then review
[TRACE_KIT.md](TRACE_KIT.md) for variable descriptions, captured artefacts, and Longhorn-specific behaviour before running the
play in production.

### 5. Keep validation commands handy

After any change to playbooks or inventory data, rerun the validation commands from Day 1 (ansible-inventory, ansible-lint, and syntax checks). They act as smoke tests that catch issues early.
