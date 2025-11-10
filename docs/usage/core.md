<!-- Usage guide for importing core Python utilities -->

# Core Utilities

Some reusable Python helpers live under `src/core` in the legacy project repository. Use the core sync commands to import them into labtools or into a generated lab project.

## Directory Layout

- `src/core/` (legacy project) — Source tree containing shared Python modules.
- `src/labtools/core_modules/` (recommended destination) — Location inside labtools for synced modules.

## Syncing Core Modules

```bash
labtools core sync \
  /Users/jpmcdonald/Code/tmp-wair-tools/wair-sparse/src/core \
  /Users/jpmcdonald/Code/labtools/src/labtools/core_modules \
  --module utils \
  --module config \
  --module logging \
  --module run_context.py
```

- Destination may be any package path; create `src/labtools/core_modules` (tracked via placeholder) to host the modules.
- Command overwrites existing files with the same names.

## Sanitisation Checklist

- Remove client-specific configuration defaults, API endpoints, or identifiers.
- Ensure logging and telemetry targets point to generic destinations.
- Replace hard-coded secrets with environment variables or configuration entries.
- Run `pytest` / `mypy` to validate compatibility after syncing.

## Integration Tips

- Expose imported modules via `labtools.core_modules` or wrap them in higher-level APIs.
- Update `pyproject.toml` if additional dependencies are required.
- Consider adding smoke tests covering critical utilities once synced.
- Share run tokens and environment metadata with runtime workers by reading `labtools.core_modules.run_context`.
- Combine `DiagnosticsEngine`, `ValidationRunner`, and `ExecutionEnforcer` to enforce diagnostics levels, test coverage, and human review gates before promoting code.


