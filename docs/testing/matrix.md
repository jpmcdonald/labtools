# Test Matrix & Fixture Plan

Date: 2025-11-09

## Test Tiers

| Tier | Description | Scope | Target Runtime | Trigger |
| --- | --- | --- | --- | --- |
| **unit** | Fast, deterministic tests for pure functions and adapters | Sync helpers, hashing, manifest core logic, CLI no-op invocations | < 1 min | Every push, PR |
| **integration** | Exercises interactions between modules and filesystem | RunContext + ExecutionEnforcer + DiagnosticsEngine, ValidationRunner subprocess, BuildReporter with temp DuckDB | 2-4 min | Nightly, pre-release |
| **governance** | High-diagnostic level checks aligned with human-in-loop gates | Evidence bundle generation, manifest drift detection, compliance scripts, environment activation | 5+ min | Release candidate, manual approval |

## Shared Fixtures

- **`pytest` fixtures** (to add):
  - `tmp_parquet`: produces small parquet datasets with configurable schema.
  - `run_context`: initializes `RunContext`, auto-finalizes on teardown.
  - `cli_runner`: wraps `click.testing.CliRunner` with environment activation.
  - `duckdb_conn`: yields temporary DuckDB database for integration tests.
  - `diagnostic_env`: sets diagnostics level, injects fake evidence directories.
  - `shell_scripts_dir`: copies shell helpers into isolated path for execution tests.

- **Dataset Samples**:
  - Already present UCI CSVs -> convert portions into parquet for hashing/manifest tests.
  - Add canned manifest JSON fixtures for regression comparisons.

- **Mock/Stub Utilities**:
  - Use `subprocess.run` monkeypatch for ValidationRunner to avoid executing real scripts.
  - Provide minimal validation script templates in `tests/fixtures/validation`.

## Environment Matrix

| Python | Platform | Notes |
| --- | --- | --- |
| 3.11 | macOS (Apple Silicon) | Primary development environment |
| 3.11 | Ubuntu (x86_64) | CI minimal test run |
| 3.12 (optional) | Ubuntu | Future-proof compatibility |

- Optional extras: `duckdb`, `pyarrow`, `pydantic` (if added) to be toggleable via extras.
- Use `tox` or `uv` to manage multi-environment execution; default to single env locally.

## Open Questions

- Do governance tests need real credentialed systems, or can they rely on fixtures?
- Should we snapshot BuildReporter outputs for regression using approval tests?
- Confirm acceptable runtime for release-gate suite.

## Next Steps

1. Implement fixtures under `tests/conftest.py` and supporting `tests/fixtures/`.
2. Label existing tests with `@pytest.mark.unit`.
3. Add integration/governance subsets as they are developed.


