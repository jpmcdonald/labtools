<!-- Usage guide for labtools virtual environment workflow -->

# Environment Management

Labtools ships portable activation scripts (`activate.sh`, `deactivate.sh`) that manage virtual environments per deployment environment (base, dev, lab, test, stage, client).

## Activation

```bash
./activate.sh            # defaults to LABTOOLS_ENV=dev
./activate.sh lab        # explicit environment
LABTOOLS_ENV=stage ./activate.sh
```

- Virtual environments live under `virtualenv/venv-<env>`.
- Dependencies install from `requirements/requirements-<env>.txt` if present, otherwise `requirements/requirements.txt`.

## Deactivation

```bash
./deactivate.sh          # uses current LABTOOLS_ENV (default dev)
./deactivate.sh stage    # explicitly target stage environment
```

## Go CLI Wrapper

`go.py` exposes the `labtools` CLI via Python, while `go.sh` wraps activation + invocation.

```bash
./go.sh --env lab infra sync ...      # Activate lab env then run command
./go.py core sync ...                 # Assume environment already activated
```

## Environment Variables

- `LABTOOLS_ENV` / `LABTOOLS_ENVIRONMENT` – active environment name.
- `LABTOOLS_PROJECT_ROOT` – absolute path to repository root.
- Thread defaults: `VECLIB_MAXIMUM_THREADS`, `OMP_NUM_THREADS`, `NUMEXPR_MAX_THREADS`, `PYTORCH_ENABLE_MPS_FALLBACK` (overridable before activation).

## Syncing Requirements

Use the CLI to copy sanitized requirements from the original project export:

```bash
labtools requirements sync \
  /Users/.../wair-sparse/requirements \
  /Users/.../labtools/requirements \
  --file requirements.txt \
  --file requirements-dev.txt \
  --file requirements-lab.txt
```

Add new files to the command as additional `--file` arguments.


