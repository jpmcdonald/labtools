# Labtools Sample Datasets

The `data/` tree includes openly available datasets for quick validation and demonstrations. These assets are sourced from the UCI Machine Learning Repository and other public archives cited below.

## Directory Structure

- `data/raw/` – Immutable input datasets downloaded from public sources.
- `data/processed/` – Placeholder for transformed datasets generated during exercises.
- `data/external/` – Space for third-party datasets (e.g., Kaggle exports) that require authentication.
- `data/metadata/` – Store data dictionaries or schema descriptors.
- `data/archive/` – Historical snapshots.
- `data/scratch/` – Scratch space for experiments.

## Bundled Raw Datasets

| Path | Description | Source |
| --- | --- | --- |
| `data/raw/iris.csv` | Classic Iris flower classification dataset (150 rows). | UCI Machine Learning Repository |
| `data/raw/winequality-red.csv` | Wine quality regression/classification dataset (red variants). | UCI Machine Learning Repository |
| `data/raw/winequality-white.csv` | Wine quality dataset (white variants). | UCI Machine Learning Repository |
| `data/raw/adult.csv` | Census income prediction dataset. | UCI Machine Learning Repository |
| `data/raw/Bike-Sharing-Dataset/day.csv` | Daily bike rental counts with weather context. | UCI Machine Learning Repository |
| `data/raw/Bike-Sharing-Dataset/hour.csv` | Hourly bike rental counts with weather context. | UCI Machine Learning Repository |

Each file retains the original licensing/usage terms of its source.

## Additional Recommendations

- **Kaggle Open Datasets** – Requires a Kaggle account; download into `data/external/` using the Kaggle CLI (`kaggle datasets download ...`).
- **Time Series Collections** – Open repositories such as `liaoyuhua/open-time-series-datasets` provide multi-variate benchmarks; store exports under `data/external/`.
- **Categorical Data Repositories** – GitHub collections (e.g., `alanagresti/categorical-data`) supply curated categorical datasets suitable for encoding tests.

## Updating Datasets

1. Ensure new datasets are covered by permissive licenses suitable for redistribution.
2. Place pristine copies in `data/raw/`. Derived artefacts belong in `data/processed/`.
3. Record metadata (schema, source URL, license) in `data/metadata/` or this README.
4. When adding large files, update `.gitattributes`/LFS strategy as needed.

For further curation ideas, see:

- UCI Machine Learning Repository – https://archive.ics.uci.edu/
- Kaggle Datasets – https://www.kaggle.com/datasets
- Open Time Series Datasets – https://github.com/liaoyuhua/open-time-series-datasets


