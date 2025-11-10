#!/usr/bin/env bash
set -euo pipefail

# Build a new lab repository using the labtools package and templates.
#
# Usage:
#   ./scripts/build_lab.sh --name my-lab --template default --destination ../my-lab
#   ./scripts/build_lab.sh --config configs/custom.yml --destination ../client-lab
#
# Assumes:
#   - labtools is installed in the current Python environment (pip install -e .)
#   - Destination directory does not yet exist (will be created).

NAME=""
TEMPLATE="default"
DESTINATION=""
CONFIG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)
      NAME="$2"
      shift 2
      ;;
    --template)
      TEMPLATE="$2"
      shift 2
      ;;
    --destination)
      DESTINATION="$2"
      shift 2
      ;;
    --config)
      CONFIG="$2"
      shift 2
      ;;
    --help|-h)
      cat <<EOF
Usage: $0 [--name NAME] [--template TEMPLATE] --destination PATH [--config CONFIG]

Builds a new lab repository from the packaged templates.
EOF
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$DESTINATION" ]]; then
  echo "--destination is required." >&2
  exit 1
fi

LABTOOLS_CLI="labtools"

if ! command -v "$LABTOOLS_CLI" >/dev/null 2>&1; then
  echo "labtools CLI not found on PATH. Activate your virtualenv and run 'pip install -e .' first." >&2
  exit 1
fi

ARGS=(init "$DESTINATION" --template "$TEMPLATE")

if [[ -n "$CONFIG" ]]; then
  ARGS+=(--config "$CONFIG")
fi

if [[ -n "$NAME" ]]; then
  TMP_CONFIG=$(mktemp)
  cat >"$TMP_CONFIG" <<EOF
name: "$NAME"
EOF
  ARGS+=(--config "$TMP_CONFIG")
fi

echo "=> Generating lab at $DESTINATION using template '$TEMPLATE'"
"$LABTOOLS_CLI" "${ARGS[@]}"

if [[ -n "${TMP_CONFIG:-}" ]]; then
  rm -f "$TMP_CONFIG"
fi

echo "=> Lab created successfully."
echo "Next steps:"
echo " 1. cd $DESTINATION"
echo " 2. ./scripts/bootstrap.sh"
echo " 3. Fill out project-specific documentation."


