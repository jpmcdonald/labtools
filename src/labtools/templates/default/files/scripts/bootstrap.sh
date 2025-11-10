#!/usr/bin/env bash
set -euo pipefail

echo "Bootstrapping {{ name }} environment"

if command -v asdf >/dev/null 2>&1 && [[ -f ".tool-versions" ]]; then
  echo "Installing toolchain with asdf"
  asdf install
fi

python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel
pip install -r requirements.txt || true

echo "Bootstrap complete."

