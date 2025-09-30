# Ansible Development Tips

These techniques help you experiment safely, iterate quickly, and diagnose unexpected
behaviour when working on the playbooks in this repository.

## Safe preview runs

- **Syntax validation** – Always start with a parse check to catch indentation or YAML
  issues before connecting to hosts:
  ```bash
  ansible-playbook -i inventories/hosts.yml playbooks/maintenance.yml --syntax-check
  ```
- **No-op dry runs** – Use check mode to review the planned changes without executing
  them. Combine with a host limit to keep the output focused:
  ```bash
  ansible-playbook -i inventories/hosts.yml playbooks/maintenance.yml \
    --check --limit kube_alpha
  ```
- **Diff output** – Add `--diff` when you want to inspect the file or template
  differences that Ansible would apply during a real run.

## Targeting specific tasks

- **Run only tagged steps** – Tag long-running or optional tasks and then execute just
  those pieces with `--tags some_tag`. Exclude noisy sections with `--skip-tags`.
- **Resume from a task** – After a failed run, restart at the next relevant task without
  repeating earlier work using `--start-at-task "Task name"`.
- **List affected hosts and tasks** – Combine `--list-hosts`, `--list-tasks`, or
  `--list-tags` with other flags to confirm what would run before touching infrastructure.

## Debugging output

- **Increase verbosity** – Add `-v`, `-vv`, or `-vvv` to see module arguments,
  templated values, and SSH details. Reserve `-vvvv` for deep SSH debugging.
- **Prompt before each task** – Use `--step` to confirm execution one task at a time when
  investigating complex logic.
- **Capture task context** – Insert temporary `debug:` tasks to print variables. For
  large structures, set `var` so Ansible formats the output cleanly:
  ```yaml
  - name: Inspect host configuration
    ansible.builtin.debug:
      var: hostvars[inventory_hostname]
  ```

## Local iteration tips

- **Reuse the same Python virtualenv** – Activate the tooling environment (`source
  .venv/bin/activate`) to ensure the correct Ansible version and collections are loaded.
- **Cache facts during experiments** – Fact gathering can be slow on large inventories.
  Enable the JSON fact cache by exporting `ANSIBLE_FACT_PATH` to a writable directory and
  adding `fact_caching=jsonfile` in `ansible.cfg` while iterating.
- **Validate variable precedence** – When troubleshooting overrides, run
  `ansible-inventory ... --host <hostname>` to inspect the merged variables that a host
  receives.

## Post-run analysis

- **Review the recap** – Pay attention to the `changed` and `failed` counts per host. A
  host stuck in `changed=0` during check mode is a sign that nothing would happen in a
  real run.
- **Persist logs** – Pipe output to `tee` (`ansible-playbook ... | tee logs/maintenance.log`)
  so you can revisit the details or share them with the team.

Use these patterns together to de-risk changes, gather the information you need, and keep
runs predictable across environments.
