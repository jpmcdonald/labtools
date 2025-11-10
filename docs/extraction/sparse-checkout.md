<!-- Instructions for sparse checkout of reusable tooling from the source repository -->

# Sparse Checkout Workflow

Follow this procedure to extract only the reusable tooling components from the source repository without touching proprietary client deliverables.

## 1. Prepare a Clean Workspace

```bash
mkdir -p /Users/jpmcdonald/Code/tmp-source-tools
cd /Users/jpmcdonald/Code/tmp-source-tools
```

Keep this temporary directory isolated and delete it after the extraction process.

## 2. Run the Sparse Checkout Script

Use the provided helper to materialise just the tooling directories. Update the placeholder repository URL and adjust the path list as needed.

```bash
/Users/jpmcdonald/Code/labtools/scripts/extraction/sparse_checkout.sh \
  <source-repo-url> \
  source-sparse \
  tools/infra/core \
  tools/infra/modules/networking \
  tools/infra/modules/iam \
  tools/infra/modules/lab-observability \
  scripts/build-system \
  scripts/lib \
  doc/shared-instructions \
  doc/templates \
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

The script:

- Creates a sparse clone with tree filtering (`--filter=tree:0 --sparse`).
- Limits the materialised files to the specified directories.
- Performs a basic scan for sensitive artefacts (file extensions, keywords).

## 3. Verify the Checkout

Inside the sparse clone (`cd source-sparse`):

1. `git status` should show a clean working tree.
2. `ls` should list only the tooling directories and `.git`.
3. Review the script’s scan output. Investigate any warnings immediately.
4. Optionally run manual checks such as:

   ```bash
   rg --stats '(client|secret|confidential)' tools/ scripts/ doc/
   rg --stats '(account-id|arn:aws)' tools/infra/modules
   ```

If any proprietary files appear, stop and update the `git sparse-checkout set ...` list to exclude them, then reclone.

## 4. Capture Findings

Update `docs/extraction/scope.md` with any newly discovered safe/unsafe paths and note additional dependencies uncovered during inspection.

## 5. Proceed to History Filtering

Once the sparse checkout is validated, continue with the history rewriting process outlined in `docs/extraction/filtering.md`.

## Cleanup Reminder

After the extraction workflow is complete, remove the temporary sparse clone directory:

```bash
rm -rf /Users/jpmcdonald/Code/tmp-source-tools/source-sparse
```

Ensure no client artefacts remain on disk.


