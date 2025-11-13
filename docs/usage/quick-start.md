# Quick Start: Setting Up a New Lab

The fastest way to create a new lab with all tools automatically included.

## Prerequisites

1. Install labtools in your Python environment:
   ```bash
   cd /path/to/labtools
   python -m venv .venv
   source .venv/bin/activate
   # OR use the provided activation script:
   # source activate.sh dev
   
   pip install --upgrade pip
   pip install -e .
   ```

2. **Activate the environment before using labtools:**
   ```bash
   # Make sure you're in the labtools directory
   source .venv/bin/activate
   # OR
   source activate.sh dev
   
   # Verify labtools is available
   labtools --help
   ```

## Create a New Lab with All Tools

**⚠️ Important:** Make sure your virtual environment is activated first!

```bash
# Activate the environment (if not already active)
source .venv/bin/activate
# OR
source activate.sh dev
```

### Option 1: Using the CLI

```bash
labtools init ../my-new-lab --with-all-tools
```

### Option 2: Using the Wrapper Script

```bash
./scripts/build_lab.sh --name my-new-lab --destination ../my-new-lab --with-all-tools
```

## What Gets Installed

When you use `--with-all-tools`, the following are automatically copied into your new lab:

- **Core Modules** (`src/core_modules/`):
  - `diagnostics.py` - Diagnostics engine with levels 0-9
  - `run_context.py` - Run ID, token, and artifact tracking
  - `execution_enforcer.py` - PEP 578 audit hooks and anti-bypass
  - `validation_runner.py` - Validation script discovery and execution
  - `build_reporter.py` - Comprehensive build reports

- **Data Modules** (`src/data_modules/`):
  - `hash_utils.py` - Deterministic parquet hashing
  - `manifest.py` - Metadata and schema drift detection
  - `duckdb_config.py` - Optimized DuckDB connection factory
  - `environment_manager.py` - Resource tuning and environment config

- **Runtime Modules** (`src/runtime_modules/`):
  - Job orchestration primitives for signal-driven checkpointing

- **MCP Tools** (`src/mcp_tools/`):
  - Model control plane utilities

- **Report Generators** (`src/reporting/`):
  - Report generation components

- **Requirements Files** (`requirements/`):
  - `requirements.txt`
  - `requirements-dev.txt`
  - `requirements-lab.txt`
  - `requirements-test.txt`

- **Environment Scripts** (root):
  - `activate.sh` - Multi-environment activation (base, dev, lab, test, stage, client)
  - `deactivate.sh` - Environment deactivation
  - `go.py` - Python CLI wrapper
  - `go.sh` - Shell wrapper for CLI

- **Documentation Templates** (`docs/templates/`):
  - Jinja2 templates for onboarding, runbooks, status reports

- **Data Directory Structure** (`data/`):
  - `archive/`, `external/`, `metadata/`, `processed/`, `raw/`, `scratch/`

## Next Steps

After creating your lab:

1. **Navigate to the new lab:**
   ```bash
   cd ../my-new-lab
   ```

2. **Activate the environment:**
   ```bash
   source activate.sh dev  # or: lab, test, stage, client
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements/requirements-dev.txt
   ```

4. **Review and customize:**
   - Review the installed tools in `src/`
   - Customize configuration files as needed
   - Update `README.md` with project specifics

5. **Initialize Git (optional):**
   ```bash
   git init
   git add .
   git commit -m "Initial lab setup with all tools"
   ```

## Customization

You can still customize the lab creation:

```bash
# Use a custom template
labtools init ../my-lab --template custom --with-all-tools

# Use a config file
labtools init ../my-lab --config configs/my-config.yml --with-all-tools
```

## Manual Tool Installation

If you prefer to install tools selectively instead of using `--with-all-tools`, see `docs/usage/build-lab.md` for instructions on using individual sync commands.

