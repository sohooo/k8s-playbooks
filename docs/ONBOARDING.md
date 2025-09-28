# Onboarding Guide

Follow this checklist to become productive quickly when working with the playbooks.

## 1. Clone the repository

```bash
git clone git@github.com:your-org/k8s-playbooks.git
cd k8s-playbooks
```

> Replace the remote URL with the location of your fork if you are contributing changes.

## 2. Create and activate the tooling virtual environment

Run the helper script and activate the environment in the same shell:

```bash
./scripts/setup-ansible.sh
source .venv/bin/activate
```

If you want to keep the virtual environment outside of the repository, set the `VENV_DIR` variable before invoking the script:

```bash
VENV_DIR=$HOME/.virtualenvs/k8s-playbooks ./scripts/setup-ansible.sh
source $HOME/.virtualenvs/k8s-playbooks/bin/activate
```

## 3. Validate the installation

After activation, confirm that both Ansible and the linter are available:

```bash
ansible --version
ansible-lint --version
```

## 4. Explore the inventory

Visualise the cluster layout to confirm your access to managed nodes:

```bash
ansible-inventory -i inventories/hosts.ini --graph
```

If you cannot reach the nodes yet, contact an administrator to obtain SSH access or to have the inventory updated with the
appropriate hostnames.

## 5. Dry-run the maintenance playbook

Before making changes, perform a syntax check. This verifies that the playbook parses correctly without touching any hosts:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --syntax-check
```

## 6. Apply changes responsibly

When you are ready to run the maintenance workflow against a test environment, limit execution to the relevant cluster or host:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube_alpha
```

Use the `--check` flag for a safe preview where possible, and always monitor the output for failed tasks. Reach out to the
platform engineering team if you encounter unexpected behaviour.
