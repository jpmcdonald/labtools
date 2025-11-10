#!/usr/bin/env bash
set -euo pipefail

if [ -n "${BASH_SOURCE[0]+set}" ]; then
  SCRIPT_PATH="${BASH_SOURCE[0]}"
else
  SCRIPT_PATH="$0"
fi
PROJECT_ROOT="$(cd "$(dirname "${SCRIPT_PATH}")" && pwd)"

ENV_ARG="${LABTOOLS_ENV:-dev}"

if [ "${1:-}" = "--env" ]; then
  if [ -z "${2:-}" ]; then
    echo "Usage: $0 [--env ENV] [labtools args...]" >&2
    exit 1
  fi
  ENV_ARG="$2"
  shift 2
fi

# Activate requested environment
# shellcheck disable=SC1090
source "${PROJECT_ROOT}/activate.sh" "${ENV_ARG}"

python "${PROJECT_ROOT}/go.py" "$@"

