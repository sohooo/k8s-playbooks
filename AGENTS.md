# Contributor Guidelines for Ansible Projects

Welcome to the repository! This document sets expectations for contributors working anywhere in this project tree. Please read it before submitting changes.

## Testing
- Before running any linting or syntax-check commands, execute `./scripts/setup-ansible.sh` to install Ansible and the required tooling. Activate the virtual environment it creates so that the commands are available in your shell.
- Run `ansible-lint` against any roles, playbooks, or modules you modify. Address all reported issues before opening a pull request.
- Validate playbooks with `ansible-playbook --syntax-check` for each playbook touched in your change. Syntax checks must pass without warnings or errors.
- Include the commands you executed (and their results) in your pull request description so reviewers can verify the checks.

## Documentation
- Update relevant documentation, READMEs, or inline comments to reflect behavior or configuration changes introduced by your contribution.
- When adding new features, describe usage, prerequisites, and examples so users can quickly adopt them.
- Continuously improve onboarding materials (e.g., project overviews, setup instructions) whenever you notice gaps or outdated guidance while working on your change.
- Highlight any new dependencies or configuration steps prominently to reduce friction for new contributors.
