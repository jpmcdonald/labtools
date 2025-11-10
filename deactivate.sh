#!/usr/bin/env bash
set -euo pipefail

if [ -n "${BASH_SOURCE[0]+set}" ]; then
  _SCRIPT_PATH="${BASH_SOURCE[0]}"
elif [ -n "${ZSH_VERSION+set}" ]; then
  _SCRIPT_PATH="${(%):-%N}"
else
  _SCRIPT_PATH="$0"
fi
PROJECT_ROOT="$(cd "$(dirname "${_SCRIPT_PATH}")" && pwd)"
TARGET_ENV="${1:-${LABTOOLS_ENV:-dev}}"
VENV_DIR="${PROJECT_ROOT}/virtualenv/venv-${TARGET_ENV}"

if [ -z "${VIRTUAL_ENV:-}" ]; then
  echo "No virtual environment is currently active."
  exit 0
fi

if [ "${VIRTUAL_ENV}" != "${VENV_DIR}" ]; then
  echo "Active virtual environment (${VIRTUAL_ENV}) does not match target (${VENV_DIR})."
  echo "Deactivating anyway."
fi

echo "Deactivating virtual environment: ${VIRTUAL_ENV}"
deactivate

if [ -z "${VIRTUAL_ENV:-}" ]; then
  echo "Virtual environment successfully deactivated."
  echo "Current python: $(command -v python 2>/dev/null || echo 'not found')"
else
  echo "Warning: virtual environment may still be active (${VIRTUAL_ENV})."
fi


