# External Datasets

This directory is reserved for datasets that cannot be committed directly to the repository (for example, Kaggle downloads or other sources that require credentials or have redistribution restrictions).

## Usage

1. Download the dataset manually (e.g., via the Kaggle CLI or a web download).
2. Place the original archive in this directory.
3. Optionally extract contents into a subdirectory to keep raw files organised.
4. Record source URL, license, and download instructions in this README or a dataset-specific note.

## Notes

- Do **not** commit proprietary or credential-restricted data.
- For Kaggle, you can run:

  ```bash
  kaggle datasets download <dataset-id> -p data/external/
  ```

  Make sure you have configured your Kaggle API token locally; do not commit the token.

- When redistributing labtools as open source, point users here and describe any optional datasets they may add on their own.


