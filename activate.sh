#!/usr/bin/env bash
set -euo pipefail

# Determine project root (bash/zsh compatible)
if [ -n "${BASH_SOURCE[0]+set}" ]; then
  _SCRIPT_PATH="${BASH_SOURCE[0]}"
elif [ -n "${ZSH_VERSION+set}" ]; then
  _SCRIPT_PATH="${(%):-%N}"
else
  _SCRIPT_PATH="$0"
fi
PROJECT_ROOT="$(cd "$(dirname "${_SCRIPT_PATH}")" && pwd)"

# Environment selection: positional argument > LABTOOLS_ENV > default "dev"
REQUESTED_ENV="${1:-${LABTOOLS_ENV:-dev}}"
export LABTOOLS_ENV="${REQUESTED_ENV}"
SUPPORTED_ENVS=("base" "dev" "lab" "test" "stage" "client")
if ! printf '%s\0' "${SUPPORTED_ENVS[@]}" | grep -q -F -x "${LABTOOLS_ENV}"; then
  echo "Warning: LABTOOLS_ENV='${LABTOOLS_ENV}' is not in supported list (${SUPPORTED_ENVS[*]}). Proceeding anyway."
fi

# Virtual environment location
VENV_DIR="${PROJECT_ROOT}/virtualenv/venv-${LABTOOLS_ENV}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

# Create venv if missing
if [ ! -d "${VENV_DIR}" ]; then
  echo "Creating virtual environment for '${LABTOOLS_ENV}' at ${VENV_DIR}"
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

# Switch from other venvs if necessary
if [ -n "${VIRTUAL_ENV:-}" ] && [ "${VIRTUAL_ENV}" != "${VENV_DIR}" ]; then
  echo "Switching virtual environments: ${VIRTUAL_ENV} -> ${VENV_DIR}"
  deactivate 2>/dev/null || true
fi

# Activate
if [ "${VIRTUAL_ENV:-}" != "${VENV_DIR}" ]; then
  # shellcheck disable=SC1090
  source "${VENV_DIR}/bin/activate"
  echo "Activated virtual environment: ${VENV_DIR}"
fi

echo "Using Python from: $(command -v python)"
echo "Using pip from   : $(command -v pip)"

# Install requirements if not yet done
REQ_DIR="${PROJECT_ROOT}/requirements"
REQ_FILE="${REQ_DIR}/requirements-${LABTOOLS_ENV}.txt"
if [ ! -f "${REQ_FILE}" ]; then
  REQ_FILE="${REQ_DIR}/requirements.txt"
fi

if [ -f "${REQ_FILE}" ]; then
  MARKER="${VENV_DIR}/.requirements-$(basename "${REQ_FILE}")"
  if [ ! -f "${MARKER}" ]; then
    echo "Installing dependencies from ${REQ_FILE}"
    pip install -r "${REQ_FILE}"
    touch "${MARKER}"
  fi
else
  echo "No requirements file found for environment '${LABTOOLS_ENV}'. Skipping dependency install."
fi

# Threading defaults (safe values; adjust as needed)
export VECLIB_MAXIMUM_THREADS="${VECLIB_MAXIMUM_THREADS:-8}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-12}"
export NUMEXPR_MAX_THREADS="${NUMEXPR_MAX_THREADS:-12}"
export PYTORCH_ENABLE_MPS_FALLBACK="${PYTORCH_ENABLE_MPS_FALLBACK:-1}"

# Surface environment metadata
export LABTOOLS_ENVIRONMENT="${LABTOOLS_ENV}"
export LABTOOLS_PROJECT_ROOT="${PROJECT_ROOT}"

echo "LABTOOLS_ENVIRONMENT=${LABTOOLS_ENVIRONMENT}"
echo "Environment ready."


