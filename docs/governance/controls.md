# Governance Controls

Labtools includes a governance stack that combines diagnostics, layered testing, and human-in-the-loop approvals to ensure new code and datasets meet quality bars before promotion.

## Diagnostics Levels

`src/labtools/core_modules/diagnostics.py` defines ten diagnostics levels. Each level adds additional guarantees:

- **0** – Off (basic logging only)
- **1** – Structural checks (table/column presence, non-empty tables)
- **2** – Scope echo (min/max dates, coverage summaries, fingerprints)
- **3** – Math integrity (canonical rounding, checksums)
- **4** – Localization (partition deltas, distribution analysis)
- **5** – Governance snapshot (rule matrices, gate readiness)
- **6** – Decision readout (dual interpretation, reconciliation ledger)
- **7** – Reproducibility (frozen inputs, provenance manifest)
- **8** – Safety (data quality plus PII/drift scans)
- **9** – Audit-ready (performance profiling, replay evidence bundle)

Use the `DiagnosticsEngine` to execute targeted diagnostics and produce evidence bundles tied to a `RunContext`.

## Testing Levels

The `ValidationRunner` class orchestrates validation suites and aggregates results across:

- **Unit tests** (`pytest.mark.unit`) – fast checks for individual transformations and adapters.
- **Integration tests** (`pytest.mark.integration`) – multi-step pipeline validation and subprocess execution.
- **Governance tests** (`pytest.mark.governance`) – diagnostics bundles, approval evidence, and human-in-loop enforcement.

See `docs/testing/matrix.md` for the detailed fixture matrix, environment combinations, and sample datasets used in each tier. Hook automation into CI/CD by calling `ValidationRunner.discover_validation_scripts()` and running scripts before merge approvals.

## Human-in-the-loop Enforcement

`ExecutionEnforcer` and `RunContext` implement runtime controls:

- `RunContext` sets mandatory environment variables (`LAB_RUN_ID`, `LAB_RUN_TOKEN`, `LAB_DIAG`, `LAB_RULESET`) and tracks artifacts/audit logs.
- `ExecutionEnforcer` installs PEP 578 audit hooks, blocks unmanaged subprocesses, and checks for “throwaway” patterns (e.g., `print`, `exec`) to enforce coding standards.
- Configure allowed paths and license checks to ensure manual reviews occur before promotion.

## Approval Workflow

1. **Run Context** – Ensure every job runs inside a `RunContext` and records outputs via manifests/hashes.
2. **Diagnostics & Testing** – Execute the diagnostics level appropriate for the release plus the validation suite.
3. **Evidence Review** – Produce build reports (`BuildReporter`) and manifest comparisons for reviewer sign-off.
4. **Human Approval** – Require reviewers to sign off on the generated reports and audit logs before merging or deploying.

## Customisation

- Override diagnostics/test thresholds with environment variables (see `manifest.py` for configurable columns/rules).
- Extend the validation directory with project-specific tests; rerun via `labtools validation` workflows.
- Integrate with CI (GitHub Actions, GitLab CI) to enforce that no merge occurs without passing diagnostics/tests and manual review.


