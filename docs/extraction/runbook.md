<!-- End-to-end extraction runbook for legacy tooling -->

# Extraction Runbook

Use this checklist to create a sanitized bundle of legacy tooling (infrastructure, shell helpers, documentation) ready for import into `labtools`.

## 1. Environment Prep

- Ensure `docs/extraction/scope.md` and `docs/extraction/access.md` are up to date.
- Create/confirm the temp workspace: `/Users/jpmcdonald/Code/tmp-source-tools`.
- Verify required tools: `git`, `git-filter-repo`, `rg`, `jq`, `yq`.

## 2. Sparse Checkout

```bash
/Users/jpmcdonald/Code/labtools/scripts/extraction/sparse_checkout.sh \
  <source-repo-url> \
  /Users/jpmcdonald/Code/tmp-source-tools/source-sparse \
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

- Record the commit hash returned by `git rev-parse HEAD` in `docs/extraction/scope.md`.
- Investigate any warnings emitted by the script (files matching secret/client patterns).

## 3. Manual Verification

Inside `source-sparse`:

```bash
git status
ls
rg --stats '(client|secret|confidential)' .
rg --stats 'arn:aws' tools/infra
```

If results include client identifiers, adjust the sparse path list and repeat.

## 4. History Filtering

```bash
/Users/jpmcdonald/Code/labtools/scripts/extraction/filter_history.sh \
  /Users/jpmcdonald/Code/tmp-source-tools/source-sparse \
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

- Confirm `git remote -v` shows no `origin`.
- Inspect commits: `git log --oneline | head`.

## 5. Package Artifacts

From `/Users/jpmcdonald/Code/tmp-source-tools`:

```bash
tar czf source-tooling-export.tgz -C source-sparse .
shasum -a 256 source-tooling-export.tgz > source-tooling-export.tgz.sha256
```

- Move or copy the archive into the `labtools` workspace when ready.

## 6. Handover

- Update `docs/extraction/scope.md` with any new paths discovered.
- Log completion date and operator in this runbook (section below).
- Proceed to the integration tasks (`templates/`, `src/`, docs) using the archive contents.

## 7. Runbook Log

| Date | Operator | Commit Hash | Notes |
|---|---|---|---|
| | | | |

## 8. Cleanup Reminder

- After integration is complete, delete `/Users/jpmcdonald/Code/tmp-source-tools/source-sparse` and archives containing client-derived data.
- Follow the detailed checklist in `docs/extraction/cleanup.md` and log any follow-ups.


