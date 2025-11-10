<!-- Usage guide for syncing data utilities -->

# Data Utilities

Use `labtools data sync` to import reusable loaders, cleaners, quality checks, hash utilities, and data dictionaries from the sanitized source export.

## Directory Layout

- `src/data/` (legacy project) — Source tree for shared data tooling.
- `src/labtools/data_modules/` (labtools) — Destination package for staged utilities.

## Syncing Modules

```bash
labtools data sync \
  /Users/jpmcdonald/Code/tmp-wair-tools/wair-sparse/src/data \
  /Users/jpmcdonald/Code/labtools/src/labtools/data_modules \
  --module loaders \
  --module cleaners \
  --module quality \
  --module hashing.py \
  --module dictionaries \
  --module environment_manager.py \
  --module duckdb_config.py
```

- Mix directories and individual files as needed.
- Existing modules with the same name are overwritten.

## Sanitisation Checklist

- Parameterise storage locations, schema names, and client-specific IDs.
- Externalise thresholds for quality checks into configuration files.
- Ensure hash utilities do not embed secret salts; use environment variables if required.
- Replace data dictionary content with template placeholders.
- Confirm environment configs (memory limits, thread counts) align with reusable defaults.

## Integration Tips

- Expose staged utilities via `labtools.data_modules` or wrap them in higher-level classes.
- Add automated tests to assert loaders/cleaners operate with sample datasets.
- Consider shipping example configuration under `templates/` to guide downstream users.
- Coordinate with runtime modules so parallel workers reuse the environment manager’s connection factory.


