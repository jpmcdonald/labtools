# Contributing to Labtools

Thank you for investing in reusable lab tooling. Follow these guidelines to keep the project healthy and client-safe.

## Workflow

1. Fork or create a feature branch.
2. Run `pip install -e .[dev]` to install development dependencies.
3. Add or update tests alongside code changes (mark them with `@pytest.mark.unit`, `@pytest.mark.integration`, or `@pytest.mark.governance` as appropriate).
4. Run formatters/linters (`ruff check`, `black`, `pytest`) before opening a PR. For faster feedback, run `tox -e py311-unit`; use `tox -e py311-all` before requesting review.

## Commit Hygiene

- Use descriptive commit messages referencing the workflow step (e.g., `extraction: add sparse checkout helper`).
- Avoid committing proprietary client data. Validate with `rg '(client|secret|confidential)'`.

## Sensitive Data Policy

- Only operate on sanitized repositories produced by the extraction workflow.
- Never add credentials, secrets, or client-specific identifiers to this repo.

## Pull Requests

- Describe the motivation, approach, and validation steps.
- Include any follow-up actions required after merging (e.g., re-running build scripts).
- Request review from at least one maintainer.

## Release Process

1. Update `CHANGELOG.md` (to be added).
2. Bump the version in `pyproject.toml` and `src/labtools/__init__.py`.
3. Tag the release: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`.
4. Publish to PyPI or internal package index as required.

## Contact

For questions or security concerns, reach out to `labtools-maintainers@example.com`.


