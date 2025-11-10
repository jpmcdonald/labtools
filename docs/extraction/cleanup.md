<!-- Cleanup guidance after extracting tooling -->

# Cleanup & Follow-up Tracking

Use this checklist once the sanitized tooling has been imported into `labtools`.

## 1. Remove Temporary Assets

- Delete sparse checkout directories:

  ```bash
  rm -rf /Users/jpmcdonald/Code/tmp-wair-tools/wair-sparse
  ```

- Delete export archives and checksum files:

  ```bash
  rm -f /Users/jpmcdonald/Code/tmp-wair-tools/wair-tooling-export.tgz*
  ```

- Clear shell history if sensitive commands were executed (`history -c` in dedicated shell).

## 2. Verify Workspace Hygiene

- Run `rg '(client|secret|confidential)'` at the repository root to confirm nothing leaked.
- Ensure `.gitignore` covers `tmp/`, archives, and other transient artefacts (update if needed).

## 3. Record Follow-ups

Document outstanding tasks, open questions, or issues discovered during extraction.

| Date | Item | Owner | Status |
|---|---|---|---|
| | | | |

- Transfer follow-up items to the issue tracker or project board as appropriate.

## 4. Notify Stakeholders

- Share a summary of imported assets (modules, scripts, docs) with the labtools maintainers.
- Provide the commit hash/tag used for extraction and any sanitisation notes.

## 5. Archive Evidence (Optional)

- Store validation logs or reports in a secure location if compliance requires proof of sanitisation.


