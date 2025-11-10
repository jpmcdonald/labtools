# Labtools Infrastructure Templates

This directory houses reusable Terraform modules and root stacks imported from prior projects. Use `labtools infra sync` to populate the contents from a sanitized sparse checkout.

## Structure

- `modules/` — Shared Terraform modules (networking, IAM, observability, etc.).
- `core/` — Optional root modules defining lab environments (create as needed).

## Guidelines

1. Ensure all client-specific identifiers are removed or parameterised.
2. Document module inputs/outputs in `README.md` files within each module.
3. Do not commit Terraform state, `.terraform/`, or generated files.
4. Keep module versions tracked via git tags or semantic version folders when appropriate.


