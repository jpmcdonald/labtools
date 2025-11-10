#!/usr/bin/env python3
"""
DuckDB Configuration Utilities

Reference configuration for Apple M2 Max-class hardware (64GB RAM, 12 cores).
Provides consistent settings across analytics pipelines and analysis scripts.
"""

import duckdb
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


# System-specific configuration
DEFAULT_MEMORY_LIMIT = '30GB'  # 30GB for DuckDB (out of 64GB total)
DEFAULT_THREADS = 12           # All 12 physical cores on M2 Max
DEFAULT_TEMP_DIR = 'data/scratch/tmp'


def get_optimized_connection(
    db_path: str = ':memory:',
    memory_limit: str = DEFAULT_MEMORY_LIMIT,
    threads: int = DEFAULT_THREADS,
    temp_directory: str = DEFAULT_TEMP_DIR,
    read_only: bool = False,
    **kwargs
) -> duckdb.DuckDBPyConnection:
    """
    Get DuckDB connection with standard performance settings used by the reference lab environment.
    
    Optimized for:
    - Apple M2 Max: 12 cores, 64GB RAM
    - Database size: ~8GB total
    - Workload: Analytics, ML training, reporting
    
    Args:
        db_path: Path to database file or ':memory:' for in-memory
        memory_limit: Memory limit for DuckDB (default: 30GB)
        threads: Number of threads to use (default: 12 for M2 Max)
        temp_directory: Directory for temporary files
        read_only: Open database in read-only mode
        **kwargs: Additional connection parameters
        
    Returns:
        Configured DuckDB connection
        
    Example:
        >>> conn = get_optimized_connection('data/database/datamart_lab.duckdb')
        >>> df = conn.execute("SELECT * FROM fact_sales_lines").fetchdf()
        >>> conn.close()
    """
    # Create connection
    conn = duckdb.connect(db_path, read_only=read_only, **kwargs)
    
    try:
        # Memory settings
        conn.execute(f"SET memory_limit='{memory_limit}'")
        conn.execute(f"SET max_memory='{memory_limit}'")
        
        # Ensure temp directory exists
        temp_path = Path(temp_directory)
        temp_path.mkdir(parents=True, exist_ok=True)
        conn.execute(f"SET temp_directory='{temp_directory}'")
        
        # Parallelism settings
        conn.execute(f"SET threads={threads}")
        conn.execute("SET enable_object_cache=true")
        
        # Query optimization
        conn.execute("SET preserve_insertion_order=false")  # Faster aggregations
        conn.execute("SET force_compression='auto'")        # Automatic compression
        
        logger.info(f"✅ DuckDB connection configured: {memory_limit} memory, {threads} threads")
        
    except Exception as e:
        logger.warning(f"⚠️  Could not set all DuckDB settings: {e}")
        # Don't fail - connection is still usable with default settings
    
    return conn


def get_lab_connection(read_only: bool = False) -> duckdb.DuckDBPyConnection:
    """
    Get connection to lab datamart with standard optimization.
    
    Args:
        read_only: Open in read-only mode
        
    Returns:
        Configured connection to datamart_lab.duckdb
    """
    db_path = 'data/database/datamart_lab.duckdb'
    return get_optimized_connection(db_path, read_only=read_only)


def get_production_connection(read_only: bool = True) -> duckdb.DuckDBPyConnection:
    """
    Get connection to production datamart (read-only by default).
    
    Args:
        read_only: Open in read-only mode (default: True for safety)
        
    Returns:
        Configured connection to datamart.duckdb
    """
    db_path = 'data/database/datamart.duckdb'
    return get_optimized_connection(db_path, read_only=read_only)


def get_dev_connection(read_only: bool = False) -> duckdb.DuckDBPyConnection:
    """
    Get connection to dev datamart with standard optimization.
    
    Args:
        read_only: Open in read-only mode
        
    Returns:
        Configured connection to datamart_dev.duckdb
    """
    db_path = 'data/database/datamart_dev.duckdb'
    return get_optimized_connection(db_path, read_only=read_only)


def get_in_memory_connection(
    memory_limit: str = '20GB'
) -> duckdb.DuckDBPyConnection:
    """
    Get pure in-memory connection (no persistence).
    
    Useful for temporary analysis where persistence is not needed.
    Uses less memory by default since no disk backing.
    
    Args:
        memory_limit: Memory limit (default: 20GB for in-memory)
        
    Returns:
        Configured in-memory connection
    """
    return get_optimized_connection(':memory:', memory_limit=memory_limit)


def configure_for_ml_pipeline(
    conn: duckdb.DuckDBPyConnection
) -> None:
    """
    Additional configuration for ML pipelines.
    
    Optimizes for:
    - Large result sets
    - Arrow zero-copy transfers
    - Parallel feature engineering
    
    Args:
        conn: Existing DuckDB connection to configure
    """
    # Additional ML-specific settings
    conn.execute("SET default_order='ASC'")  # Consistent ordering for reproducibility
    conn.execute("SET default_null_order='NULLS LAST'")
    
    logger.info("✅ Configured connection for ML pipeline")


def get_connection_info(conn: duckdb.DuckDBPyConnection) -> Dict[str, Any]:
    """
    Get information about current connection configuration.
    
    Args:
        conn: DuckDB connection to inspect
        
    Returns:
        Dictionary with configuration details
    """
    info = {}
    
    try:
        # Get key settings
        settings_query = """
            SELECT name, value 
            FROM duckdb_settings() 
            WHERE name IN ('max_memory', 'threads', 'temp_directory', 
                          'enable_object_cache', 'preserve_insertion_order')
        """
        settings = conn.execute(settings_query).fetchall()
        info['settings'] = {name: value for name, value in settings}
        
        # Get table count (if not in-memory with no tables)
        try:
            table_count = conn.execute("SELECT COUNT(*) FROM duckdb_tables()").fetchone()[0]
            info['table_count'] = table_count
        except:
            info['table_count'] = 0
        
        # Get database path
        try:
            db_path = conn.execute("SELECT database_name FROM duckdb_databases()").fetchone()[0]
            info['database'] = db_path
        except:
            info['database'] = ':memory:'
            
    except Exception as e:
        logger.warning(f"Could not get full connection info: {e}")
    
    return info


def benchmark_query(
    conn: duckdb.DuckDBPyConnection,
    query: str,
    label: str = "Query",
    warmup: bool = True
) -> float:
    """
    Benchmark a query and log results.
    
    Args:
        conn: DuckDB connection
        query: SQL query to benchmark
        label: Description for logging
        warmup: Run warmup query first (default: True)
        
    Returns:
        Elapsed time in seconds
        
    Example:
        >>> conn = get_lab_connection()
        >>> benchmark_query(conn, "SELECT COUNT(*) FROM fact_sales_lines", "Sales count")
        Sales count: 0.123 seconds (1282812 rows)
    """
    import time
    
    # Warm-up run (loads data into memory)
    if warmup:
        conn.execute(query).fetchall()
    
    # Timed run
    start = time.time()
    result = conn.execute(query).fetchall()
    elapsed = time.time() - start
    
    row_count = len(result) if result else 0
    logger.info(f"{label}: {elapsed:.3f} seconds ({row_count:,} rows)")
    
    return elapsed


# Context manager for automatic connection cleanup
class DuckDBConnection:
    """
    Context manager for DuckDB connections with automatic cleanup.
    
    Example:
        >>> with DuckDBConnection('data/database/datamart_lab.duckdb') as conn:
        ...     df = conn.execute("SELECT * FROM fact_sales_lines").fetchdf()
        # Connection automatically closed
    """
    
    def __init__(
        self,
        db_path: str = ':memory:',
        read_only: bool = False,
        **kwargs
    ):
        self.db_path = db_path
        self.read_only = read_only
        self.kwargs = kwargs
        self.conn = None
    
    def __enter__(self) -> duckdb.DuckDBPyConnection:
        self.conn = get_optimized_connection(
            self.db_path,
            read_only=self.read_only,
            **self.kwargs
        )
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
            logger.debug(f"Closed connection to {self.db_path}")


# Export key functions
__all__ = [
    'get_optimized_connection',
    'get_lab_connection',
    'get_production_connection',
    'get_dev_connection',
    'get_in_memory_connection',
    'configure_for_ml_pipeline',
    'get_connection_info',
    'benchmark_query',
    'DuckDBConnection',
    'DEFAULT_MEMORY_LIMIT',
    'DEFAULT_THREADS',
    'DEFAULT_TEMP_DIR',
]

