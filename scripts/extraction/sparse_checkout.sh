#!/usr/bin/env bash
set -euo pipefail

# Sparse checkout helper for extracting reusable tooling from a source repository
#
# Usage:
#   ./scripts/extraction/sparse_checkout.sh <wair-repo-url> <checkout-dir> \
#       tools/infra scripts/build-system doc/shared-instructions
#
# The script:
#   1. Creates a temporary sparse clone that materialises only the requested paths.
#   2. Runs a lightweight content scan for possible sensitive artefacts.
#   3. Prints next steps for history filtering.

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <wair-repo-url> <checkout-dir> <path> [<path> ...]" >&2
  exit 1
fi

REPO_URL="$1"
CHECKOUT_DIR="$2"
shift 2
PATHS=("$@")

if [[ -d "$CHECKOUT_DIR" ]]; then
  echo "Checkout directory '$CHECKOUT_DIR' already exists. Aborting to avoid overwriting." >&2
  exit 1
fi

echo "=> Creating sparse clone in $CHECKOUT_DIR"
git clone --filter=tree:0 --sparse "$REPO_URL" "$CHECKOUT_DIR"

cd "$CHECKOUT_DIR"

echo "=> Enabling sparse checkout"
git sparse-checkout init --cone
git sparse-checkout set "${PATHS[@]}"

echo "=> Fetching the requested paths"
git fetch origin
git checkout main

echo "=> Materialised directories:"
printf ' - %s\n' "${PATHS[@]}"

echo "=> Scanning for potentially sensitive files"
SENSITIVE_PATTERNS=(
  "\\.pem$"
  "\\.key$"
  "secret"
  "confidential"
  "client"
)

SCAN_HITS=0
for pattern in "${SENSITIVE_PATTERNS[@]}"; do
  if rg --files --iglob "$pattern" >/dev/null 2>&1; then
    ((SCAN_HITS++))
    echo "WARNING: Files matching '$pattern' found."
    rg --files --iglob "$pattern"
  fi
done

if [[ $SCAN_HITS -eq 0 ]]; then
  echo "=> No obvious sensitive artefacts detected in sparse checkout."
else
  echo "=> Review the above matches before proceeding."
fi

echo
echo "Next steps:"
echo " 1. Run 'git status' to confirm no unexpected files are present."
echo " 2. Continue with the history filtering step (see docs/extraction/filtering.md)."


