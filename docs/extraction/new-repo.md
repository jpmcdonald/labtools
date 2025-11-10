<!-- Instructions for setting up the standalone labtools repository -->

# New Repository Setup

Follow these steps after filtering the legacy tooling history to integrate the assets into the `labtools` repository.

## 1. Import Filtered Assets

```bash
cd /Users/jpmcdonald/Code/labtools
tar xzf /Users/jpmcdonald/Code/tmp-wair-tools/wair-tooling-export.tgz -C .
```

Alternatively, copy the filtered repository contents directly into the relevant directories (`scripts/`, `src/labtools/`, `templates/`).

## 2. Normalize Structure

- Move reusable scripts into `scripts/` and name them descriptively (`sparse_checkout.sh`, `filter_history.sh`, etc.).
- Place shared configuration under `templates/`.
- Co-locate Python modules under `src/labtools/`.

## 3. Add Packaging Metadata

Ensure `pyproject.toml` defines the `labtools` package and includes required dependencies. Update version numbers, authors, and URLs as needed.

## 4. Document Everything

- Update `README.md` with project overview and usage instructions.
- Create or refresh `CONTRIBUTING.md`, `LICENSE`, and any usage guides.
- Capture extraction workflows under `docs/extraction/`.

## 5. Validate the Result

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
labtools --help
```

Run through a dry-run project scaffold (`labtools init ../sandbox`) to ensure the CLI and templates function correctly.

## 6. Initialize Git Remotes

If this repository is new:

```bash
git init
git add .
git commit -m "chore: initialise labtools repository"
git remote add origin git@github.com:your-org/labtools.git
git push -u origin main
```

## 7. Clean Up

Delete any temporary extraction directories or archives once the content is safely committed.


