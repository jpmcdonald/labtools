<!-- Access checklist for retrieving utilities from the source repository -->

# Source Repository Access Notes

Record the credentials, contacts, and prerequisites required before running the extraction workflow.

## Repository Metadata

- **URL:** `<source-repo-url>`
- **Default branch:** `main`
- **Alternate branches of interest:** `infra/main`, `tools/shared`
- **Latest confirmed commit for tooling extraction:** `<commit-sha>`

Update the commit reference once the sparse checkout is performed to keep a reproducible baseline.

## Authentication Requirements

- Git hosting account with read-only access to the source repository.
- SSH key registered with the hosting provider (or HTTPS credentials).
- VPN connection to corporate network (if applicable).
- Optional: GitHub personal access token (classic) with `repo:read` scope for HTTPS cloning.

## Local Environment Prerequisites

- Git 2.42+ with sparse checkout support.
- `git-filter-repo` installed via `pipx` or `pip`.
- `rg` (ripgrep) for content scanning.
- Terraform, AWS CLI, jq, yq (align versions with `docs/extraction/scope.md` dependency table).

## Points of Contact

- **Technical owner:** `<name> <email>`
- **Security contact:** `<name> <email>`
- **Change approval:** `<name/team>`

## Notes

- Ensure all work occurs within `/Users/jpmcdonald/Code/tmp-source-tools` (or equivalent) to keep client artefacts isolated.
- Log extraction date/time and commit hash in `docs/extraction/scope.md` once available.
- If access changes are required, submit a ticket referencing this document.


