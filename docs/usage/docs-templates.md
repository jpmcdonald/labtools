<!-- Usage guide for documentation templates -->

# Documentation Templates

Use `labtools docs sync` to import sanitized documentation templates into the repository (e.g., status reports, runbooks, onboarding checklists).

## Directory Layout

- `src/labtools/templates/docs/` — Jinja templates shipped with labtools.
- `docs/templates/` (target repo) — Destination for synced templates from the source export.

## Syncing Templates

```bash
labtools docs sync \
  /Users/jpmcdonald/Code/tmp-wair-tools/wair-sparse \
  /Users/jpmcdonald/Code/labtools/src/labtools/templates/docs \
  --document doc/templates/status-report.md \
  --document doc/templates/runbook.md \
  --document doc/templates/onboarding-checklist.md
```

- Destination can be `src/labtools/templates/docs` (to ship with the package) or a project’s `docs/` directory.
- Existing files with the same name will be overwritten.

## Template Tokens

Templates use the same context variables as other labtools scaffolds (`name`, `description`, `owner`, etc.). When copied into lab projects, they can be rendered via Jinja or manually edited.

## Sanitisation Checklist

- Remove client references, proprietary metrics, or contact details.
- Replace names/emails with placeholders or variables.
- Ensure any embedded links point to generic/internal resources.

## Integration Tips

- Reference available templates in `docs/usage/build-lab.md`.
- Encourage teams to version templates alongside lab code.
- Consider adding automation to render templates during `labtools init` (future enhancement).


