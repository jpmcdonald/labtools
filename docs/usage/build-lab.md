<!-- Usage guide for the build_lab script and CLI -->

# Building a New Lab

Two entry points exist for generating a new lab repository:

1. The `labtools` CLI (`labtools init`)
2. The wrapper script `scripts/build_lab.sh`
3. Optional sync commands (`labtools infra|shell|docs sync`) to pull shared assets into the repo.

## Prerequisites

- Python 3.11+
- `pip install -e .` from the repository root
- Optional: custom configuration YAML defining lab metadata

## Using the CLI Directly

```bash
labtools init ../sandbox-lab --template default --config configs/sandbox.yml
```

## Using the Wrapper Script

```bash
./scripts/build_lab.sh --name sandbox-lab --template default --destination ../sandbox-lab
```

Supported flags:

- `--name` – overrides the lab name in the template context.
- `--template` – selects the template directory under `src/labtools/templates/`.
- `--destination` – target directory for the generated project (required).
- `--config` – path to a YAML file with additional template variables.

## Custom Configuration

Example `configs/sandbox.yml`:

```yaml
description: "Sandbox lab for verifying tooling."
owner: "Discovery Team"
runtime: "python"
```

## Post-Generation Checklist

1. Move into the new project: `cd ../sandbox-lab`.
2. Run bootstrap: `./scripts/bootstrap.sh`.
3. Sync reusable assets as needed:

   - `labtools infra sync ...` for Terraform modules.
   - `labtools shell sync ...` for shared Bash helpers.
   - `labtools docs sync ...` for documentation templates.
   - `labtools core sync ...` for Python helper modules.
   - `labtools data sync ...` for data loaders/cleaners and dictionaries.
   - `labtools reports sync ...` for report generators and templates.
   - `labtools mcp sync ...` for MCP orchestration tools.
   - `labtools runtime sync ...` for signal-driven job orchestration primitives.
   - `labtools requirements sync ...` for dependency manifests.

4. Update the generated `README.md` with project specifics.
5. Populate `docs/` with lab procedures (see `docs/usage/environment.md` for env management).
6. Commit the scaffold to version control.


