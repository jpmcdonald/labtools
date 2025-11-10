from pathlib import Path

import pandas as pd
import pytest

from labtools.data_modules.hash_utils import compute_parquet_hash, write_hash_metadata, read_hash_metadata

pytestmark = pytest.mark.unit


def test_compute_parquet_hash(tmp_path: Path):
    df = pd.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
    parquet_path = tmp_path / "data.parquet"
    df.to_parquet(parquet_path)

    result = compute_parquet_hash(parquet_path)
    assert result["algorithm"] == "sha256"
    assert result["row_count"] == 3
    assert "hash" in result

    meta_path = tmp_path / "data.parquet.meta.json"
    write_hash_metadata(result, meta_path)
    metadata = read_hash_metadata(meta_path)
    assert metadata is not None
    assert metadata["hash"] == result["hash"]

