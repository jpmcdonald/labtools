from pathlib import Path

import pandas as pd
import pytest

from labtools.data_modules.manifest import parquet_manifest, write_manifest

pytestmark = pytest.mark.unit


def test_parquet_manifest(tmp_path: Path):
    df = pd.DataFrame(
        {
            "LocationId": [1, 1, 2],
            "VariantId": [100, 101, 102],
            "DocumentDateTime": pd.date_range("2025-01-01", periods=3, freq="D"),
            "Quantity": [5, 7, 9],
            "LocationTypeName": ["Regular Store", "Regular Store", "DC"],
            "MerchL1Name": ["Dames Fashion", "Dames Fashion", "Mens"],
            "IsDeleted": [0, 0, 0],
        }
    )

    parquet_path = tmp_path / "sample.parquet"
    df.to_parquet(parquet_path)

    manifest = parquet_manifest(parquet_path)
    assert manifest["file"] == str(parquet_path)
    assert manifest["rows"] == 3
    assert "business_validation" in manifest

    manifest_path = write_manifest(manifest, tmp_path / "manifests")
    assert manifest_path.exists()


def test_parquet_manifest_business_violation(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("LABTOOLS_CATEGORY_COLUMN", "MerchL1Name")
    monkeypatch.setenv("LABTOOLS_PRIMARY_CATEGORY_VALUE", "Primary")
    monkeypatch.setenv("LABTOOLS_CATEGORY_RATIO_THRESHOLD", "0.8")

    df = pd.DataFrame(
        {
            "LocationId": [1, 2, 3, 4],
            "VariantId": [10, 11, 12, 13],
            "DocumentDateTime": pd.date_range("2025-02-01", periods=4, freq="D"),
            "Quantity": [1, 2, 3, 4],
            "MerchL1Name": ["Primary", "Secondary", "Secondary", "Secondary"],
            "LocationTypeName": ["Regular Store"] * 4,
            "IsDeleted": [0, 0, 0, 0],
        }
    )

    parquet_path = tmp_path / "violations.parquet"
    df.to_parquet(parquet_path)

    manifest = parquet_manifest(parquet_path)
    validation = manifest["business_validation"]
    assert validation["passed"] is False
    assert any("threshold" in violation for violation in validation["violations"])
