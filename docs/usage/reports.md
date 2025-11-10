<!-- Usage guide for syncing report generators -->

# Report Generator

The `labtools reports sync` command imports report assembly utilities from the legacy `src/reports` tree.

## Directory Layout

- `src/reports/` (legacy project) — Source for reporting utilities and templates.
- `src/labtools/reporting/` — Destination package in labtools.

## Syncing Components

```bash
labtools reports sync \
  /Users/jpmcdonald/Code/tmp-wair-tools/wair-sparse/src/reports \
  /Users/jpmcdonald/Code/labtools/src/labtools/reporting \
  --module generator \
  --module templates
```

- Include supporting assets (templates, schemas) referenced by the generator.
- Overwrites existing destinations.

## Sanitisation Checklist

- Replace client branding, colors, and copy with generic placeholders.
- Verify data sources referenced by the generator are parameterised.
- Remove credentials or API keys; expect them via configuration files.

## Integration Tips

- Provide example configuration for rendering reports in `templates/`.
- Add smoke tests that render sample reports using mock data.
- Document output formats and delivery mechanisms in README or usage docs.


