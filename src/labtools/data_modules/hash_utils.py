"""Deterministic hashing utilities for parquet files.

This module provides utilities for computing stable, deterministic hashes
of parquet files to enable hash-gated data loading and validation.

Hashing Rules:
1. Drop volatile columns (timestamps, load metadata)
2. Normalize column order (alphabetical)
3. Stabilize row order (via primary key sorting)
4. Use deterministic serialization (Arrow IPC format)
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


def compute_parquet_hash(
    path: str,
    *,
    drop_columns: list[str] | None = None,
    row_key: list[str] | None = None,
) -> dict[str, Any]:
    """Compute deterministic SHA256 hash of a parquet file.
    
    Args:
        path: Path to parquet file
        drop_columns: Optional list of column names to exclude before hashing
        row_key: Optional list of column names to use for deterministic row sorting
        
    Returns:
        Dictionary containing:
        - algorithm: Hash algorithm used ('sha256')
        - hash: Hex digest of the hash
        - row_count: Number of rows in the file
        - schema: Sorted list of column names (after dropping columns)
        
    Raises:
        FileNotFoundError: If the parquet file does not exist
        
    Examples:
        >>> result = compute_parquet_hash('data.parquet')
        >>> result['hash']
        'a3f5...'
        
        >>> result = compute_parquet_hash(
        ...     'data.parquet',
        ...     drop_columns=['load_timestamp'],
        ...     row_key=['id']
        ... )
    """
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Parquet file not found: {path}")
    
    # Read parquet file
    df = pd.read_parquet(path)
    
    # Drop volatile columns if specified
    if drop_columns:
        existing_drops = [col for col in drop_columns if col in df.columns]
        if existing_drops:
            df = df.drop(columns=existing_drops)
    
    # Normalize column order (alphabetical)
    df = df[sorted(df.columns)]
    
    # Stabilize row order if row_key provided
    if row_key:
        # Verify row_key columns exist
        missing_keys = [key for key in row_key if key not in df.columns]
        if missing_keys:
            raise ValueError(f"Row key columns not found in data: {missing_keys}")
        df = df.sort_values(by=row_key).reset_index(drop=True)
    
    # Convert to Arrow table for deterministic serialization
    table = pa.Table.from_pandas(df, preserve_index=False)
    
    # Serialize using Arrow IPC format (deterministic)
    sink = pa.BufferOutputStream()
    with pa.ipc.new_stream(sink, table.schema) as writer:
        writer.write_table(table)
    
    # Get the buffer and compute hash
    buf = sink.getvalue()
    hash_digest = hashlib.sha256(buf.to_pybytes()).hexdigest()
    
    return {
        'algorithm': 'sha256',
        'hash': hash_digest,
        'row_count': len(df),
        'schema': list(df.columns),
    }


def write_hash_metadata(
    hash_result: dict[str, Any],
    metadata_path: str,
) -> None:
    """Write hash metadata to a sidecar JSON file.
    
    Args:
        hash_result: Result dict from compute_parquet_hash
        metadata_path: Path where to write the metadata JSON
        
    Examples:
        >>> result = compute_parquet_hash('data.parquet')
        >>> write_hash_metadata(result, 'data.parquet.meta.json')
    """
    import json
    from datetime import datetime, timezone
    
    metadata = {
        **hash_result,
        'created_at': datetime.now(timezone.utc).isoformat(),
    }
    
    Path(metadata_path).parent.mkdir(parents=True, exist_ok=True)
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)


def read_hash_metadata(metadata_path: str) -> dict[str, Any] | None:
    """Read hash metadata from a sidecar JSON file.
    
    Args:
        metadata_path: Path to the metadata JSON file
        
    Returns:
        Metadata dict if file exists and is valid, None otherwise
        
    Examples:
        >>> metadata = read_hash_metadata('data.parquet.meta.json')
        >>> if metadata and metadata['hash'] == expected_hash:
        ...     print("Hash matches")
    """
    import json
    
    path = Path(metadata_path)
    if not path.exists():
        return None
    
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


__all__ = [
    'compute_parquet_hash',
    'write_hash_metadata',
    'read_hash_metadata',
]