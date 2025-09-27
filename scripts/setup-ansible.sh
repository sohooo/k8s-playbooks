#!/usr/bin/env bash
set -euo pipefail

# Determine repo root relative to this script
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
VENV_DIR="${VENV_DIR:-${REPO_ROOT}/.venv}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but was not found in PATH." >&2
  exit 1
fi

python3 -m venv "${VENV_DIR}"
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

pip install --upgrade pip
pip install --upgrade ansible ansible-lint

echo "Virtual environment created at ${VENV_DIR}" >&2
echo "Activate it with: source ${VENV_DIR}/bin/activate" >&2
echo "Ansible tooling installation complete." >&2
