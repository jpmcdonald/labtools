"""Enhanced Parquet manifest utilities with business context integration.

Compute comprehensive metadata for Parquet files including:
- Schema drift detection
- Business context integration
- Data quality indicators
- Performance benchmarking
- Business rules validation

Supports retail analytics workloads with location-specific validation rules.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import psutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import logging

import pandas as pd
import pyarrow.parquet as pq
from datetime import datetime, timezone

# Set up logging
logger = logging.getLogger(__name__)


# Business context defaults (can be overridden via environment variables)
DEFAULT_BUSINESS_COLUMNS = [
    'LocationId', 'VariantId', 'DocumentDateTime', 'Quantity',
    'DocumentType', 'LocationTypeName', 'MerchL1Name', 'UnitPrice',
    'IsDeleted', 'SaleDate', 'TotalAmount'
]

BUSINESS_COLUMNS = [
    col.strip() for col in os.getenv(
        'LABTOOLS_BUSINESS_COLUMNS',
        ','.join(DEFAULT_BUSINESS_COLUMNS)
    ).split(',') if col.strip()
]

LOCATION_TYPE_COLUMN = os.getenv('LABTOOLS_LOCATION_TYPE_COLUMN', 'LocationTypeName')
CATEGORY_COLUMN = os.getenv('LABTOOLS_CATEGORY_COLUMN', 'MerchL1Name')
PRIMARY_CATEGORY_VALUE = os.getenv('LABTOOLS_PRIMARY_CATEGORY_VALUE', 'Dames Fashion')
PRIMARY_LOCATION_VALUE = os.getenv('LABTOOLS_PRIMARY_LOCATION_VALUE', 'Regular Store')

KEY_COLUMNS = [
    col.strip() for col in os.getenv(
        'LABTOOLS_KEY_COLUMNS',
        'LocationId,VariantId,DocumentDateTime'
    ).split(',') if col.strip()
]

BUSINESS_RULES = {
    'category_focus_ratio': float(os.getenv('LABTOOLS_CATEGORY_RATIO_THRESHOLD', '0.95')),
    'primary_location_ratio': float(os.getenv('LABTOOLS_PRIMARY_LOCATION_RATIO', '0.5')),
    'key_column_null_threshold': float(os.getenv('LABTOOLS_KEY_COLUMN_NULL_THRESHOLD', '0.05')),
    'stock_range': {
        'min': float(os.getenv('LABTOOLS_STOCK_MIN', '0')),
        'max': float(os.getenv('LABTOOLS_STOCK_MAX', '10000')),
    },
}

LOCATION_ID_COLUMN = os.getenv('LABTOOLS_LOCATION_ID_COLUMN', 'LocationId')
VARIANT_ID_COLUMN = os.getenv('LABTOOLS_VARIANT_ID_COLUMN', 'VariantId')
DATETIME_COLUMN = os.getenv('LABTOOLS_DATETIME_COLUMN', 'DocumentDateTime')
QUANTITY_COLUMN = os.getenv('LABTOOLS_QUANTITY_COLUMN', 'Quantity')
DOCUMENT_TYPE_COLUMN = os.getenv('LABTOOLS_DOCUMENT_TYPE_COLUMN', 'DocumentType')
UNIT_PRICE_COLUMN = os.getenv('LABTOOLS_UNIT_PRICE_COLUMN', 'UnitPrice')
IS_DELETED_COLUMN = os.getenv('LABTOOLS_IS_DELETED_COLUMN', 'IsDeleted')
TOTAL_AMOUNT_COLUMN = os.getenv('LABTOOLS_TOTAL_AMOUNT_COLUMN', 'TotalAmount')


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    """Compute SHA256 hash of a file in chunks."""
    h = hashlib.sha256()
    with path.open('rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def get_memory_usage() -> float:
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


def detect_schema_drift(current_manifest: Dict[str, Any],
                       historical_manifests: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Detect schema drift between current and historical manifests.

    Args:
        current_manifest: Current manifest data
        historical_manifests: List of historical manifests to compare against

    Returns:
        Dictionary containing drift analysis results
    """
    if not historical_manifests:
        return {'drift_detected': False, 'message': 'No historical data for comparison'}

    current_columns = set(current_manifest['columns'])
    drift_results = {
        'drift_detected': False,
        'added_columns': [],
        'removed_columns': [],
        'schema_changes': [],
        'comparisons': []
    }

    for historical_manifest in historical_manifests:
        hist_columns = set(historical_manifest['columns'])

        # Find added and removed columns
        added = current_columns - hist_columns
        removed = hist_columns - current_columns

        if added or removed:
            drift_results['drift_detected'] = True

        if added:
            drift_results['added_columns'].extend(list(added))

        if removed:
            drift_results['removed_columns'].extend(list(removed))

        # Compare schema details
        comparison = {
            'historical_file': historical_manifest['file'],
            'historical_timestamp': historical_manifest.get('manifest_created_at'),
            'added_columns': list(added),
            'removed_columns': list(removed),
            'row_count_change': current_manifest['rows'] - historical_manifest.get('rows', 0),
            'size_change_bytes': current_manifest['size_bytes'] - historical_manifest.get('size_bytes', 0)
        }
        drift_results['comparisons'].append(comparison)

    # Remove duplicates
    drift_results['added_columns'] = list(set(drift_results['added_columns']))
    drift_results['removed_columns'] = list(set(drift_results['removed_columns']))

    return drift_results


def validate_business_rules(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate business rules against dataframe.

    Args:
        df: DataFrame to validate

    Returns:
        Dictionary containing validation results
    """
    validation_results = {
        'passed': True,
        'violations': [],
        'warnings': []
    }

    # Check Dames Fashion ratio
    if CATEGORY_COLUMN in df.columns:
        focus_count = (df[CATEGORY_COLUMN] == PRIMARY_CATEGORY_VALUE).sum()
        total_records = len(df)
        focus_ratio = focus_count / total_records if total_records > 0 else 0

        if focus_ratio < BUSINESS_RULES['category_focus_ratio']:
            validation_results['violations'].append(
                f"{PRIMARY_CATEGORY_VALUE} ratio {focus_ratio:.2%} below threshold "
                f"{BUSINESS_RULES['category_focus_ratio']:.2%}"
            )
            validation_results['passed'] = False

    # Check primary location ratio
    if LOCATION_TYPE_COLUMN in df.columns:
        primary_location_count = (df[LOCATION_TYPE_COLUMN] == PRIMARY_LOCATION_VALUE).sum()
        total_records = len(df)
        primary_location_ratio = primary_location_count / total_records if total_records > 0 else 0

        if primary_location_ratio < BUSINESS_RULES['primary_location_ratio']:
            validation_results['warnings'].append(
                f"{PRIMARY_LOCATION_VALUE} ratio {primary_location_ratio:.2%} below expected "
                f"{BUSINESS_RULES['primary_location_ratio']:.2%}"
            )

    # Check key column null thresholds
    for col in KEY_COLUMNS:
        if col in df.columns:
            null_count = df[col].isnull().sum()
            total_records = len(df)
            null_rate = null_count / total_records if total_records > 0 else 0

            if null_rate > BUSINESS_RULES['key_column_null_threshold']:
                validation_results['violations'].append(
                    f"Column {col} null rate {null_rate:.2%} exceeds threshold "
                    f"{BUSINESS_RULES['key_column_null_threshold']:.2%}"
                )
                validation_results['passed'] = False

    # Check stock level ranges for Regular Stores
    if LOCATION_TYPE_COLUMN in df.columns and QUANTITY_COLUMN in df.columns:
        primary_mask = df[LOCATION_TYPE_COLUMN] == PRIMARY_LOCATION_VALUE
        if primary_mask.any():
            primary_quantities = df.loc[primary_mask, QUANTITY_COLUMN]
            extreme_negative = (primary_quantities < BUSINESS_RULES['stock_range']['min']).sum()
            extreme_positive = (primary_quantities > BUSINESS_RULES['stock_range']['max']).sum()

            if extreme_negative > 0:
                validation_results['warnings'].append(
                    f"Found {extreme_negative:,} stock values below {BUSINESS_RULES['stock_range']['min']} "
                    f"in {PRIMARY_LOCATION_VALUE}"
                )

            if extreme_positive > 0:
                validation_results['warnings'].append(
                    f"Found {extreme_positive:,} stock values above {BUSINESS_RULES['stock_range']['max']:,} "
                    f"in {PRIMARY_LOCATION_VALUE}"
                )

    return validation_results


def calculate_business_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate business KPIs for the dataset.

    Args:
        df: DataFrame to analyze

    Returns:
        Dictionary containing KPI calculations
    """
    kpis = {
        'total_records': len(df),
        'unique_locations': 0,
        'unique_variants': 0,
        'location_type_distribution': {},
        'data_quality_metrics': {},
        'business_metrics': {}
    }

    if df.empty:
        return kpis

    # Basic counts
    kpis['unique_locations'] = df[LOCATION_ID_COLUMN].nunique() if LOCATION_ID_COLUMN in df.columns else 0
    kpis['unique_variants'] = df[VARIANT_ID_COLUMN].nunique() if VARIANT_ID_COLUMN in df.columns else 0

    # Location type distribution
    if LOCATION_TYPE_COLUMN in df.columns:
        location_dist = df[LOCATION_TYPE_COLUMN].value_counts().to_dict()
        kpis['location_type_distribution'] = location_dist

    # Data quality metrics
    if IS_DELETED_COLUMN in df.columns:
        deleted_count = df[IS_DELETED_COLUMN].sum()
        active_count = len(df) - deleted_count
        kpis['data_quality_metrics'] = {
            'deleted_records': int(deleted_count),
            'active_records': int(active_count),
            'deletion_rate': float(deleted_count / len(df)) if len(df) > 0 else 0
        }

    # Business metrics
    if QUANTITY_COLUMN in df.columns:
        total_quantity = df[QUANTITY_COLUMN].sum()
        avg_quantity = df[QUANTITY_COLUMN].mean()
        kpis['business_metrics'] = {
            'total_quantity': float(total_quantity),
            'avg_quantity_per_record': float(avg_quantity)
        }

        # Stock level analysis by location type
        if LOCATION_TYPE_COLUMN in df.columns:
            stock_by_location = df.groupby(LOCATION_TYPE_COLUMN)[QUANTITY_COLUMN].agg(['sum', 'mean', 'count'])
            kpis['business_metrics']['stock_by_location_type'] = stock_by_location.to_dict()

    return kpis


def parquet_manifest(path: str | Path, include_business_analysis: bool = True) -> Dict[str, Any]:
    """Create comprehensive manifest for Parquet file with business context integration.

    Args:
        path: Path to Parquet file
        include_business_analysis: Whether to include business rules validation and KPIs

    Returns:
        Enhanced manifest dictionary with business context and quality metrics
    """
    p = Path(path)

    # Performance benchmarking - start timing
    start_time = time.time()
    initial_memory = get_memory_usage()

    try:
        # Basic file operations
        pf = pq.ParquetFile(p)
        schema = pf.schema_arrow
        st = p.stat()

        # Basic metadata
        file_mtime = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat()
        file_ctime = datetime.fromtimestamp(st.st_ctime, tz=timezone.utc).isoformat()
        created_at = datetime.now(tz=timezone.utc).isoformat()

        # Core manifest data
        manifest = {
            'file': str(p),
            'size_bytes': p.stat().st_size,
            'rows': pf.metadata.num_rows,
            'row_groups': pf.metadata.num_row_groups,
            'columns': schema.names,
            'schema': [
                {
                    'name': f.name,
                    'type': str(f.type),
                    'nullable': f.nullable,
                }
                for f in schema
            ],
            'sha256': sha256_file(p),
            'file_mtime': file_mtime,
            'file_ctime': file_ctime,
            'manifest_created_at': created_at,
        }

        # Performance metrics
        end_time = time.time()
        final_memory = get_memory_usage()

        manifest['performance_metrics'] = {
            'creation_time_seconds': round(end_time - start_time, 3),
            'memory_increase_mb': round(final_memory - initial_memory, 2),
            'processing_rate_mb_per_sec': round(
                manifest['size_bytes'] / (1024 * 1024) / (end_time - start_time), 2
            ) if end_time > start_time else 0
        }

        # Business analysis (optional)
        if include_business_analysis:
            try:
                # Read sample of data for analysis (limit to avoid memory issues)
                sample_size = min(10000, manifest['rows'])  # Limit sample size
                df = pd.read_parquet(p).head(sample_size) if manifest['rows'] > 0 else pd.DataFrame()

                if not df.empty:
                    # Business rules validation
                    manifest['business_validation'] = validate_business_rules(df)

                    # Business KPIs
                    manifest['business_kpis'] = calculate_business_kpis(df)

                    # Data quality indicators
                    manifest['data_quality'] = {
                        'null_rates': {
                            col: round(df[col].isnull().sum() / len(df), 4)
                            for col in df.columns if df[col].isnull().sum() > 0
                        },
                        'unique_counts': {
                            col: df[col].nunique()
                            for col in BUSINESS_COLUMNS
                            if col in df.columns
                        }
                    }

                else:
                    manifest['business_validation'] = {
                        'passed': True,
                        'violations': [],
                        'warnings': ['Empty dataset - no validation performed']
                    }
                    manifest['business_kpis'] = {}
                    manifest['data_quality'] = {}

            except Exception as e:
                logger.warning(f"Business analysis failed for {p}: {str(e)}")
                manifest['business_analysis_error'] = str(e)

        return manifest

    except Exception as e:
        # Ensure we capture timing even on errors
        end_time = time.time()
        final_memory = get_memory_usage()

        # Return error manifest
        error_manifest = {
            'file': str(p),
            'error': str(e),
            'error_type': type(e).__name__,
            'manifest_created_at': datetime.now(tz=timezone.utc).isoformat(),
            'performance_metrics': {
                'creation_time_seconds': round(end_time - start_time, 3),
                'memory_increase_mb': round(final_memory - initial_memory, 2),
                'processing_rate_mb_per_sec': 0
            }
        }

        logger.error(f"Failed to create manifest for {p}: {str(e)}")
        return error_manifest


def write_manifest(manifest: Dict[str, Any], out_dir: str | Path) -> Path:
    """Write manifest to JSON file."""
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    file_name = Path(manifest['file']).name
    dest = out_path / f"{file_name}.manifest.json"
    dest.write_text(json.dumps(manifest, indent=2))
    return dest


def load_historical_manifests(manifest_dir: str | Path,
                            file_pattern: str = "*.manifest.json") -> List[Dict[str, Any]]:
    """Load historical manifests from directory for schema drift analysis.

    Args:
        manifest_dir: Directory containing historical manifests
        file_pattern: Pattern to match manifest files

    Returns:
        List of historical manifest dictionaries
    """
    manifest_path = Path(manifest_dir)
    if not manifest_path.exists():
        logger.warning(f"Manifest directory {manifest_path} does not exist")
        return []

    manifest_files = list(manifest_path.glob(file_pattern))
    historical_manifests = []

    for manifest_file in manifest_files:
        try:
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)

            # Skip the current file if it's in the same directory
            if manifest.get('file') != str(manifest_file):
                historical_manifests.append(manifest)

        except Exception as e:
            logger.warning(f"Failed to load manifest {manifest_file}: {str(e)}")

    # Sort by creation time, most recent first
    historical_manifests.sort(
        key=lambda x: x.get('manifest_created_at', ''),
        reverse=True
    )

    logger.info(f"Loaded {len(historical_manifests)} historical manifests")
    return historical_manifests


def create_manifest_report(manifest: Dict[str, Any],
                          historical_manifests: List[Dict[str, Any]] = None) -> str:
    """Create a human-readable report from manifest data.

    Args:
        manifest: Current manifest data
        historical_manifests: Optional list of historical manifests for comparison

    Returns:
        Markdown-formatted report string
    """
    report_lines = []

    # Header
    report_lines.append("# Parquet File Manifest Report")
    report_lines.append(f"Generated: {manifest['manifest_created_at']}")
    report_lines.append("")

    # Basic file information
    report_lines.append("## File Information")
    report_lines.append(f"- **File**: {manifest['file']}")
    report_lines.append(f"- **Size**: {manifest['size_bytes'] / (1024*1024):.2f} MB")
    report_lines.append(f"- **Rows**: {manifest['rows']:,}")
    report_lines.append(f"- **Row Groups**: {manifest['row_groups']:,}")
    report_lines.append(f"- **Columns**: {len(manifest['columns'])}")
    report_lines.append("")

    # Performance metrics
    if 'performance_metrics' in manifest:
        perf = manifest['performance_metrics']
        report_lines.append("## Performance Metrics")
        report_lines.append(f"- **Creation Time**: {perf['creation_time_seconds']:.3f}s")
        report_lines.append(f"- **Memory Increase**: {perf['memory_increase_mb']:.2f} MB")
        report_lines.append(f"- **Processing Rate**: {perf['processing_rate_mb_per_sec']:.2f} MB/s")
        report_lines.append("")

    # Schema information
    report_lines.append("## Schema")
    report_lines.append("| Column | Type | Nullable |")
    report_lines.append("|--------|------|----------|")

    for field in manifest['schema']:
        report_lines.append(f"| {field['name']} | {field['type']} | {field['nullable']} |")
    report_lines.append("")

    # Business validation
    if 'business_validation' in manifest:
        validation = manifest['business_validation']
        report_lines.append("## Business Validation")

        if validation['passed']:
            report_lines.append("✅ **All business rules passed**")
        else:
            report_lines.append("❌ **Business rule violations found:**")
            for violation in validation['violations']:
                report_lines.append(f"- {violation}")

        if validation['warnings']:
            report_lines.append("⚠️ **Warnings:**")
            for warning in validation['warnings']:
                report_lines.append(f"- {warning}")
        report_lines.append("")

    # Business KPIs
    if 'business_kpis' in manifest and manifest['business_kpis']:
        kpis = manifest['business_kpis']
        report_lines.append("## Business KPIs")
        report_lines.append(f"- **Total Records**: {kpis['total_records']:,}")
        report_lines.append(f"- **Unique Locations**: {kpis['unique_locations']:,}")
        report_lines.append(f"- **Unique Variants**: {kpis['unique_variants']:,}")

        if 'location_type_distribution' in kpis and kpis['location_type_distribution']:
            report_lines.append("- **Location Type Distribution:**")
            for loc_type, count in kpis['location_type_distribution'].items():
                report_lines.append(f"  - {loc_type}: {count:,}")

        if 'data_quality_metrics' in kpis and kpis['data_quality_metrics']:
            dq = kpis['data_quality_metrics']
            report_lines.append("- **Data Quality:**")
            report_lines.append(f"  - Active Records: {dq['active_records']:,}")
            report_lines.append(f"  - Deletion Rate: {dq['deletion_rate']:.2%}")
        report_lines.append("")

    # Schema drift analysis
    if historical_manifests:
        drift_analysis = detect_schema_drift(manifest, historical_manifests[:5])  # Compare with 5 most recent

        if drift_analysis['drift_detected']:
            report_lines.append("## Schema Drift Analysis")
            report_lines.append("⚠️ **Schema drift detected!**")
            report_lines.append("")

            if drift_analysis['added_columns']:
                report_lines.append("**Added Columns:**")
                for col in drift_analysis['added_columns']:
                    report_lines.append(f"- {col}")
                report_lines.append("")

            if drift_analysis['removed_columns']:
                report_lines.append("**Removed Columns:**")
                for col in drift_analysis['removed_columns']:
                    report_lines.append(f"- {col}")
                report_lines.append("")

            if drift_analysis['comparisons']:
                report_lines.append("**Recent Comparisons:**")
                for comp in drift_analysis['comparisons'][:3]:  # Show 3 most recent
                    report_lines.append(f"- **{Path(comp['historical_file']).name}**:")
                    report_lines.append(f"  - Row count change: {comp['row_count_change']:+,}")
                    report_lines.append(f"  - Size change: {comp['size_change_bytes'] / (1024*1024):+.2f} MB")
        else:
            report_lines.append("## Schema Drift Analysis")
            report_lines.append("✅ **No schema drift detected**")

    return "\n".join(report_lines)


def compare_manifests(manifest1: Dict[str, Any], manifest2: Dict[str, Any]) -> Dict[str, Any]:
    """Compare two manifests and return detailed comparison.

    Args:
        manifest1: First manifest to compare
        manifest2: Second manifest to compare

    Returns:
        Dictionary containing comparison results
    """
    comparison = {
        'files_compared': [manifest1['file'], manifest2['file']],
        'comparison_timestamp': datetime.now(tz=timezone.utc).isoformat(),
        'differences': {},
        'similarities': {}
    }

    # Compare basic metrics
    basic_metrics = ['rows', 'size_bytes', 'row_groups']

    for metric in basic_metrics:
        if metric in manifest1 and metric in manifest2:
            val1 = manifest1[metric]
            val2 = manifest2[metric]

            if val1 != val2:
                comparison['differences'][metric] = {
                    'file1': val1,
                    'file2': val2,
                    'change': val2 - val1,
                    'percent_change': ((val2 - val1) / val1 * 100) if val1 != 0 else float('inf')
                }
            else:
                comparison['similarities'][metric] = val1

    # Compare columns
    if 'columns' in manifest1 and 'columns' in manifest2:
        cols1 = set(manifest1['columns'])
        cols2 = set(manifest2['columns'])

        added = cols2 - cols1
        removed = cols1 - cols2

        if added or removed:
            comparison['differences']['schema'] = {
                'added_columns': list(added),
                'removed_columns': list(removed)
            }

    # Compare SHA256 (data integrity)
    if 'sha256' in manifest1 and 'sha256' in manifest2:
        if manifest1['sha256'] == manifest2['sha256']:
            comparison['similarities']['data_integrity'] = 'Identical'
        else:
            comparison['differences']['data_integrity'] = {
                'file1_hash': manifest1['sha256'],
                'file2_hash': manifest2['sha256']
            }

    return comparison


__all__ = [
    'parquet_manifest',
    'write_manifest',
    'detect_schema_drift',
    'validate_business_rules',
    'calculate_business_kpis',
    'load_historical_manifests',
    'create_manifest_report',
    'compare_manifests',
    'get_memory_usage'
]


