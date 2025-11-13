<!-- Usage guide for the build_lab script and CLI -->

# Building a New Lab

Two entry points exist for generating a new lab repository:

1. The `labtools` CLI (`labtools init`)
2. The wrapper script `scripts/build_lab.sh`
3. Optional sync commands (`labtools infra|shell|docs sync`) to pull shared assets into the repo.

## Prerequisites

- Python 3.11+
- Virtual environment activated (see below)
- `pip install -e .` from the repository root
- Optional: custom configuration YAML defining lab metadata

### Activating the Environment

Before using `labtools`, activate your virtual environment:

```bash
# From the labtools repository root
source .venv/bin/activate
# OR use the provided activation script:
source activate.sh dev
```

Verify the installation:
```bash
labtools --help
```

## Using the CLI Directly

```bash
# Basic lab creation
labtools init ../sandbox-lab --template default --config configs/sandbox.yml

# Create lab with all tools automatically installed
labtools init ../sandbox-lab --template default --with-all-tools
```

## Using the Wrapper Script

```bash
# Basic lab creation
./scripts/build_lab.sh --name sandbox-lab --template default --destination ../sandbox-lab

# Create lab with all tools automatically installed
./scripts/build_lab.sh --name sandbox-lab --template default --destination ../sandbox-lab --with-all-tools
```

Supported flags:

- `--name` – overrides the lab name in the template context.
- `--template` – selects the template directory under `src/labtools/templates/`.
- `--destination` – target directory for the generated project (required).
- `--config` – path to a YAML file with additional template variables.
- `--with-all-tools` – automatically install all available tools (core, data, runtime, mcp, reports, requirements, scripts) into the new lab.

## Custom Configuration

Example `configs/sandbox.yml`:

```yaml
description: "Sandbox lab for verifying tooling."
owner: "Discovery Team"
runtime: "python"
```

## Post-Generation Checklist

### If you used `--with-all-tools`:

1. Move into the new project: `cd ../sandbox-lab`.
2. Activate the environment: `source activate.sh dev` (or `lab`, `test`, `stage`, `client`).
3. Install dependencies: `pip install -r requirements/requirements-dev.txt` (or appropriate environment).
4. Review and customize the installed tools as needed.
5. Update the generated `README.md` with project specifics.
6. Commit the scaffold to version control.

### If you did NOT use `--with-all-tools`:

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


