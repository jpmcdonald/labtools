<!-- Usage guide for importing Terraform/IaC utilities -->

# Infrastructure Utilities

After generating a filtered source-project tooling archive, use the infra utilities to stage Terraform modules into `labtools`.

## Directory Layout

- `templates/infra/modules/` — Target location for shared Terraform modules.
- `templates/infra/core/` — Root modules or environment-level stacks (optional).

## Syncing Modules

```bash
labtools infra sync \
  /Users/jpmcdonald/Code/tmp-wair-tools/wair-sparse/tools/infra \
  /Users/jpmcdonald/Code/labtools/templates/infra \
  --module modules/networking \
  --module modules/iam \
  --module modules/lab-observability
```

- The command overwrites existing module directories.
- Source directory must point to the sanitized sparse checkout produced earlier.
- Destination defaults to any path; recommend `templates/infra` within this repo.

## Sanitisation Checklist

- Replace account IDs, ARNs, and IP ranges with Jinja variables or Terraform input variables.
- Remove backend configuration blocks, leaving them to be defined per-project.
- Delete `.terraform` directories, state files, and lock files prior to sync.
- Update module `README.md` files to remove client references.

## Documenting Usage

After syncing, update:

- `docs/usage/build-lab.md` — Mention availability of Terraform modules.
- `docs/validation/checklist.md` — Add validation steps for applying `terraform init -backend=false`.

## Next Steps

- Compose configuration templates (`templates/infra/config/`) that reference the synced modules.
- Consider adding automated tests (e.g., `terraform validate`) in CI once modules are in place.


