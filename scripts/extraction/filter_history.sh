#!/usr/bin/env bash
set -euo pipefail

# History filtering helper for extracting reusable tooling from the source repository
#
# Usage:
#   ./scripts/extraction/filter_history.sh /path/to/wair-sparse tools/infra scripts/build-system doc/shared-instructions
#
# The script:
#   1. Runs git filter-repo to keep only the specified paths.
#   2. Removes references to the original remote.
#   3. Prints guidance for validating the rewritten history.

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <sparse-checkout-dir> <path> [<path> ...]" >&2
  exit 1
fi

CHECKOUT_DIR="$1"
shift
PATHS=("$@")

if [[ ! -d "$CHECKOUT_DIR/.git" ]]; then
  echo "Directory '$CHECKOUT_DIR' does not appear to be a git repository." >&2
  exit 1
fi

cd "$CHECKOUT_DIR"

if ! command -v git-filter-repo >/dev/null 2>&1; then
  echo "git-filter-repo is required. Install via 'pip install git-filter-repo'." >&2
  exit 1
fi

echo "=> Running git filter-repo to retain selected paths"
FILTER_ARGS=()
for path in "${PATHS[@]}"; do
  FILTER_ARGS+=("--path" "$path")
done
git filter-repo --force "${FILTER_ARGS[@]}"

echo "=> Removing original 'origin' remote reference"
if git remote | grep -q "^origin$"; then
  git remote remove origin
fi

echo "=> History filtered. Suggested validation:"
echo " 1. git log --stat --oneline | head"
echo " 2. git ls-tree --full-tree -r HEAD | cut -f2-"
echo " 3. Ensure no client-specific file paths remain."

echo
echo "Next steps:"
echo " 1. Copy the filtered repository into the labtools project."
echo " 2. Continue with repository setup as described in docs/extraction/new-repo.md."


