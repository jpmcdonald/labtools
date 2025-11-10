<!-- Validation checklist for labtools workflows -->

# Validation Checklist

Use this checklist after each extraction and before releasing new tooling versions.

## 1. Environment Setup

- [ ] Create/activate a fresh virtual environment.
- [ ] Install package in editable mode with dev extras:

  ```bash
  pip install -e .[dev]
  ```

## 2. Automated Tests

- [ ] Run unit tests:

  ```bash
  pytest
  ```

- [ ] Run static checks (optional for now):

  ```bash
  ruff check src/ tests/
  mypy src/
  ```

## 3. CLI Dry Run

- [ ] Generate a sandbox project:

  ```bash
  ./scripts/build_lab.sh --name validation-lab --destination ../validation-lab
  ```

- [ ] Inspect generated files for placeholders and ensure no client references exist.
- [ ] Execute the generated `scripts/bootstrap.sh` (optionally with `--dry-run` modifications).

- [ ] Exercise sync commands against fixture directories (use temp dirs):

  ```bash
  labtools infra sync <fixtures>/tools/infra templates/infra --module modules/networking
  labtools shell sync <fixtures>/scripts scripts/lib --helper lib/logging.sh
  labtools docs sync <fixtures> src/labtools/templates/docs --document doc/templates/status-report.md
  labtools core sync <fixtures>/src/core src/labtools/core_modules --module utils
  labtools data sync <fixtures>/src/data src/labtools/data_modules --module loaders
  labtools reports sync <fixtures>/src/reports src/labtools/reporting --module generator
  labtools mcp sync <fixtures>/src/mcp src/labtools/mcp_tools --module orchestrator
  labtools runtime sync <fixtures>/src/runtime src/labtools/runtime_modules --module jobs.py
  labtools requirements sync <fixtures>/requirements requirements --file requirements.txt
  ```

- [ ] Remove synced assets after verification if they were test fixtures.

## 4. Clean Up

- [ ] Remove the sandbox project and temporary sparse clones:

  ```bash
  rm -rf ../validation-lab /Users/jpmcdonald/Code/tmp-wair-tools
  ```

- [ ] Confirm no proprietary data is present (`rg '(client|secret|confidential)'`).
- [ ] Deactivate virtual environment when done: `./deactivate.sh`.

## 5. Release Readiness

- [ ] Update version numbers and changelog (if releasing).
- [ ] Tag and push the release commit.


