<!-- Usage guide for syncing MCP tools -->

# MCP Tools

Model Control Plane (MCP) utilities can be imported with `labtools mcp sync`.

## Directory Layout

- `src/mcp/` (legacy project) — Source for orchestration scripts, schedulers, and helpers.
- `src/labtools/mcp_tools/` — Destination package in labtools.

## Syncing Modules

```bash
labtools mcp sync \
  /Users/jpmcdonald/Code/tmp-wair-tools/wair-sparse/src/mcp \
  /Users/jpmcdonald/Code/labtools/src/labtools/mcp_tools \
  --module orchestrator \
  --module scheduler \
  --module adapters
```

- Include any shared libraries referenced by MCP components.
- Overwrites existing modules with the same names.

## Sanitisation Checklist

- Replace environment-specific endpoints (queues, topics, APIs) with configuration variables.
- Remove embedded credentials or tokens.
- Ensure logging and monitoring integrations target reusable channels.

## Integration Tips

- Provide example configuration (YAML/JSON) for MCP deployments.
- Add tests verifying critical workflows (e.g., job orchestration) using mocks.
- Coordinate with infra modules if MCP components expect specific infrastructure resources.


