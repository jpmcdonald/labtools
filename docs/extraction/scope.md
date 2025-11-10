<!-- Scope assessment for extracting reusable lab tooling from the source repository -->

# Source Tooling Scope Assessment

This document records the reusable infrastructure, tooling, and utilities identified within the source repository for extraction into the standalone `labtools` project. It captures the directory layout, key assets, dependencies, and any sensitive paths that must be excluded when creating a sparse checkout.

## 1. Repository References

- **Source repository URL:** `git@github.com:your-org/wair.git`
- **Default branch:** `main`
- **Latest reviewed commit:** `<commit-sha>` (record once sparse checkout is performed)
- **Inspection method:** Use a temporary sparse clone with `git clone --filter=tree:0 --sparse` to avoid materializing client-specific assets.
- **Access prerequisites:** GitHub deploy key with read-only scope, VPN (if required), SSO session valid <24h.

Document any updates (branch names, tags) before running the extraction workflow.

## 2. Candidate Tooling Directories

Record each directory that contains reusable tooling. For each entry, include a short description and whether it is safe to extract.

| Path | Purpose | Depends On | Safe to Extract | Notes |
|---|---|---|---|---|
| `tools/infra/core` | Terraform root modules for baseline lab environments | Terraform, AWS CLI | ✅ | Strip backend `terraform.tfvars` before import |
| `tools/infra/modules/networking` | Reusable VPC/subnet definitions | Terraform | ✅ | Parameterise CIDR ranges; ensure no state files |
| `tools/infra/modules/iam` | IAM roles/policies for lab workloads | Terraform | ✅ | Replace account IDs with variables |
| `scripts/build-system` | Build automation scripts and shared shell helpers | Bash, GNU Make | ✅ | Sanitise environment variable defaults |
| `scripts/lib/logging.sh` | Shell logging utilities used across pipelines | Bash | ✅ | Confirm no client identifiers in banner text |
| `scripts/lib/aws-assume-role.sh` | Helper for AWS credential management | Bash, AWS CLI | ✅ | Remove hard-coded account aliases |
| `doc/shared-instructions` | Generic lab operating procedures | Markdown | ✅ | Remove client references before reuse |
| `doc/templates/status-report.md` | Lab status update template | Markdown | ✅ | Generalise contact details |
| `doc/templates/runbook.md` | Incident response runbook starter | Markdown | ✅ | Replace client-specific escalation matrix |
| `src/core` | Shared Python helper modules | Python 3.11 | ✅ | Review for client defaults and secret usage |
| `src/data` | Data loaders, cleaners, quality checks, dictionaries | Python, pandas, pyarrow | ✅ | Remove client schemas; keep reusable abstractions |
| `src/reports` | Report generation utilities/templates | Python, Jinja2 | ✅ | Generalise report branding/content |
| `src/mcp` | Model control plane tooling | Python, AWS SDK | ✅ | Strip environment credentials/endpoints |
| `src/runtime` | Signal handling, job orchestration, checkpointing | Python | ✅ | Replace signal choices if incompatible |
| `requirements/` | Python dependency manifests | Plain text | ✅ | Copy base and env-specific files |
| `activate.sh`, `deactivate.sh` | Virtual environment management | Bash, Python | ✅ | Parameterise environment names |
| `go.py`, `go.sh` | CLI wrappers | Python, Bash | ✅ | Ensure paths updated for labtools |
| `<add more>` | | | | |

## 3. Sensitive or Client-Specific Areas (Exclude)

List any paths that must *not* be pulled into the sparse checkout.

- `clients/<client-name>/docs` — Proprietary client documentation
- `deploy/secrets/` — Contains encrypted but client-linked artefacts
- `data/` — Sample datasets provided by the client
- `environments/<client-env>/terraform.tfstate` — Backend state snapshots with identifiers
- `analytics/` — Proprietary analysis notebooks
- `<add any additional sensitive directories>`

## 4. Tooling Dependencies

Document languages, runtimes, and external services that the tooling requires. Include minimum supported versions where possible.

| Component | Version | Source | Required By | Notes |
|---|---|---|---|---|
| Python | 3.11 | `.tool-versions`, `scripts/build-system/bootstrap.sh` | CLI utilities | Required for labtools CLI |
| Node.js | 20.x | `.tool-versions`, `scripts/build-system/package.json` | Frontend build tooling | Optional; include only if frontend assets needed |
| Terraform | 1.7.x | `tools/infra/core`, `tools/infra/modules/*` | Infrastructure provisioning | Ensure no remote state references |
| AWS CLI | 2.16+ | `scripts/lib/aws-assume-role.sh` | Build pipeline | Requires profile configuration |
| jq | 1.7 | `scripts/lib/aws-assume-role.sh` | Credential parsing | Available via Homebrew |
| yq | 4.x | `scripts/build-system/configure.sh` | Config templating | Optional; confirm usage |
| `<add more>` | | | | |

## 5. Shared Utilities Inventory

Capture specific scripts, modules, or templates that will be migrated. Link to their relative paths and note any refactoring needs.

- `scripts/build-system/build_lab.sh` — Orchestrates lab setup; refactor into standalone CLI
- `scripts/build-system/lib/logging.sh` — Shell logging helpers; keep for reuse
- `scripts/lib/aws-assume-role.sh` — Credential helper; map to `labtools shell assume-role`
- `tools/infra/modules/lab-network` — Core networking module; parameterise client-specific CIDRs
- `tools/infra/modules/lab-observability` — CloudWatch dashboards/alarms; ensure metric namespaces generic
- `doc/shared-instructions/templates/README.md` — Starter documentation template
- `doc/templates/status-report.md` — Weekly status template; inject lab metadata tokens
- `doc/templates/onboarding-checklist.md` — New lab onboarding steps; generalise role owners
- `src/core/utils.py` (and related packages) — Core Python helpers; audit for client assumptions
- `src/data/loaders/` — Standard ingestion interface; parameterise storage locations
- `src/data/cleaners/` — Data cleaning pipelines; ensure schemas configurable
- `src/data/quality/` — Data quality checks; externalise thresholds
- `src/data/hashing.py` — Hash utilities; keep deterministic approach
- `src/data/dictionaries/` — Data dictionary templates; remove client taxonomy
- `src/reports/generator/` — Report assembly logic; decouple branding
- `src/mcp/` — MCP orchestration tools; scrub environment-specific endpoints
- `src/runtime/jobs.py` — Signal controller, checkpointing hooks; ensure signals documented
- `src/core/run_context.py` — Run metadata/context propagation; generalise environment defaults
- `src/data/environment_manager.py` / `src/data/duckdb_config.py` — Connection tuning; parameterise resources
- `requirements/requirements*.txt` — Base + environment dependency lists; confirm compatibility
- `activate.sh`, `deactivate.sh` — Environment lifecycle scripts; adjust naming
- `go.py`, `go.sh` — CLI entrypoints; align commands with labtools

## 6. Open Questions / Follow-ups

- Confirm whether any `scripts/lib/*.py` utilities accompany the shell helpers.
- Identify where Terraform remote state backends are defined (S3/GCS) to avoid copying credentials.
- Clarify if Node-based build tooling is still required or can be excluded from labtools.
- Capture environment variables expected by `scripts/build-system/*.sh` (e.g., `LAB_ENV`, `AWS_PROFILE`).

## 7. Next Steps

1. Confirm the above directory list via sparse checkout.
2. Expand the tables with definitive paths and dependency versions.
3. Hand off to the extraction workflow (`sparse-clone` task).


