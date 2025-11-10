# Test Coverage Inventory

Date: 2025-11-09

## Existing Test Files

- `tests/test_cli.py` – CLI group help coverage.
- `tests/test_core_sync.py` – Core sync helper (happy path).
- `tests/test_data_sync.py` – Data sync helper (happy path).
- `tests/test_docs_sync.py` – Documentation sync helper (happy path).
- `tests/test_infra_sync.py` – Infra sync helper (happy path).
- `tests/test_mcp_sync.py` – MCP sync helper (happy path).
- `tests/test_reports_sync.py` – Reporting sync helper (happy path).
- `tests/test_requirements_sync.py` – Requirements sync helper (happy path).
- `tests/test_runtime_sync.py` – Runtime sync helper (happy path).
- `tests/test_shell_sync.py` – Shell sync helper (happy path).
- `tests/test_build_reporter.py` – Basic build reporter generation.
- `tests/test_diagnostics_engine.py` – Diagnostics engine placeholders.
- `tests/test_execution_enforcer.py` – Execution enforcer guard rails.
- `tests/test_hash_utils.py` – Parquet hashing utilities.
- `tests/test_manifest.py` – Manifest generation (success path).
- `tests/test_run_context.py` – Run context environment propagation.
- `tests/test_validation_runner.py` – Missing directory discovery guard.

## Modules Without Direct Coverage

- Environment bootstrap scripts (`activate.sh`, `deactivate.sh`, `go.sh`).
- Requirements CLI command (failure paths).
- Build reporter error handling and evidence bundle generation.
- Diagnostics engine level-specific checks (beyond placeholder).
- Validation runner execution paths with actual subprocess invocation.
- Execution enforcer audit hooks for subprocess/file access.
- Data manifest edge cases (empty datasets, business rule violations).
- DuckDB configuration bindings (parameter overrides).
- Runtime/infra/data sync failure scenarios (missing modules, permission errors).

## Identified Gaps

- No unit tests for human-in-loop enforcement workflow (RunContext + ExecutionEnforcer + DiagnosticsEngine integration).
- No CLI smoke tests invoking commands via `runner.invoke` with arguments.
- No coverage for governance docs or controls to ensure manual approval metadata is generated.
- No coverage of dataset scaffolding utilities (data dictionary generator, environment manager).
- No pytest markers/fixtures to distinguish unit vs integration tiers.

## Next Steps

1. Design fixtures to address the gaps (see plan step 2).
2. Implement targeted tests per gap, prioritising critical governance controls.
3. Automate tiers and document expectations for maintainers.


