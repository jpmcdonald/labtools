<!-- History filtering instructions for reusable tooling extraction -->

# History Rewriting with `git filter-repo`

After validating the sparse checkout, rewrite the repository history so that only the reusable tooling remains.

## 1. Install `git-filter-repo`

```bash
pipx install git-filter-repo
# or
python3 -m pip install --user git-filter-repo
```

Ensure the `git-filter-repo` command is on your `PATH`.

## 2. Run the Filtering Script

```bash
/Users/jpmcdonald/Code/labtools/scripts/extraction/filter_history.sh \
  /Users/jpmcdonald/Code/tmp-source-tools/source-sparse \
  tools/infra \
  scripts/build-system \
  doc/shared-instructions \
  src/core \
  src/data \
  src/reports \
  src/mcp \
  src/runtime \
  requirements \
  activate.sh \
  deactivate.sh \
  go.py \
  go.sh
```

This rewrites the history so only the specified paths remain and removes the original remote reference.

## 3. Validate the Rewritten Repository

Within the filtered repo:

```bash
cd /Users/jpmcdonald/Code/tmp-wair-tools/wair-sparse
git log --oneline | head
git ls-tree --full-tree -r HEAD | cut -f2-
rg --stats '(client|secret|confidential)'
```

Confirm:

- Commit messages no longer reference client work.
- No sensitive file paths or contents remain.
- Only tooling-related files are present.

## 4. Prepare for Transfer

Once validation passes:

1. Archive the filtered repo (`tar czf wair-tooling-export.tgz .`).
2. Copy the archive (or the directory) into the `labtools` repository workspace.
3. Delete the temporary sparse clone directory when done.

## 5. Update Documentation

Record any adjustments needed in `docs/extraction/scope.md` (e.g., additional paths kept or removed, reference to filtered commit range).


