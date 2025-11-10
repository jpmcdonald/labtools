<!-- Usage guide for syncing shell helpers -->

# Shell Helper Utilities

Use the `labtools shell sync` command to import reusable Bash utilities from the sanitized source checkout.

## Directory Layout

- `scripts/lib/` — Destination for shared shell helpers (logging, AWS assume-role, etc.).
- `scripts/build-system/` — Higher-level orchestration scripts; may reference helpers.

## Syncing Helpers

```bash
labtools shell sync \
  /Users/jpmcdonald/Code/tmp-wair-tools/wair-sparse/scripts \
  /Users/jpmcdonald/Code/labtools/scripts/lib \
  --helper lib/logging.sh \
  --helper lib/aws-assume-role.sh
```

- Helpers are copied by filename into the destination directory.
- Existing helpers with the same name are overwritten.
- Preserve executable permissions (`chmod +x`) after syncing if required.

## Sanitisation Checklist

- Remove client-specific identifiers, email addresses, or banner text.
- Externalise environment-specific defaults (e.g., AWS account IDs) into configuration files.
- Validate shell scripts with `shellcheck` before committing.

## Testing

1. Run `shellcheck scripts/lib/*.sh`.
2. If helpers expose functions, consider adding smoke tests under `tests/shell/`.
3. Ensure CI runs relevant shell linters (future work).

## Integration Notes

- Update `labtools` CLI or bootstrap scripts to use the synced helpers where appropriate.
- Document helper usage in `docs/usage/build-lab.md` or script-specific README files.


