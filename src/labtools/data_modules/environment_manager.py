#!/usr/bin/env python3
"""
Environment Manager for Multi-Environment Data Science Workflows

Manages connections and resources across test, dev, lab, audit, and client environments.
Ensures proper memory management when switching environments.

Environments:
- test: Mock data, unit testing, minimal datasets
- dev: Development with small characteristic datasets (10K-50K records)
- lab: Full analysis sandbox with production-scale data
- audit: End-of-project validation with synthetic/sanitized data
- client: Client delivery preparation (export to MS SQL Server format)
"""

import duckdb
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum
import logging
import gc
import psutil

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Supported environments."""
    TEST = "test"
    DEV = "dev"
    LAB = "lab"
    AUDIT = "audit"
    CLIENT = "client"


# Environment-specific configuration
ENVIRONMENT_CONFIG = {
    Environment.TEST: {
        'db_path': 'data/database/datamart_test.duckdb',
        'memory_limit': '5GB',      # Small for unit tests
        'threads': 4,                # Limited parallelism
        'description': 'Mock data and unit testing',
        'read_only': False,
    },
    Environment.DEV: {
        'db_path': 'data/database/datamart_dev.duckdb',
        'memory_limit': '10GB',     # Medium for development
        'threads': 8,                # Moderate parallelism
        'description': 'Development with small characteristic datasets',
        'read_only': False,
    },
    Environment.LAB: {
        'db_path': 'data/database/datamart_lab.duckdb',
        'memory_limit': '30GB',     # Large for full analysis
        'threads': 12,               # Full parallelism
        'description': 'Full analysis sandbox (production-scale data)',
        'read_only': False,
    },
    Environment.AUDIT: {
        'db_path': 'data/database/datamart_audit.duckdb',
        'memory_limit': '15GB',     # Medium for validation
        'threads': 8,                # Moderate parallelism
        'description': 'End-of-project validation with synthetic data',
        'read_only': True,           # Read-only for safety
    },
    Environment.CLIENT: {
        'db_path': 'data/database/datamart_client.duckdb',
        'memory_limit': '20GB',     # Large for export preparation
        'threads': 10,               # Good parallelism for transforms
        'description': 'Client delivery preparation (export to MS SQL Server)',
        'read_only': False,
    },
}


class EnvironmentManager:
    """
    Manages DuckDB connections across multiple environments.
    
    Ensures proper cleanup and memory management when switching environments.
    Only one environment connection is active at a time.
    
    Example:
        >>> env_mgr = EnvironmentManager()
        >>> 
        >>> # Work in lab environment
        >>> conn = env_mgr.connect(Environment.LAB)
        >>> df = conn.execute("SELECT ...").fetchdf()
        >>> 
        >>> # Switch to dev environment (auto-cleanup of lab)
        >>> conn = env_mgr.connect(Environment.DEV)
        >>> df = conn.execute("SELECT ...").fetchdf()
        >>> 
        >>> # Clean up when done
        >>> env_mgr.close()
    """
    
    def __init__(self):
        self.current_connection: Optional[duckdb.DuckDBPyConnection] = None
        self.current_environment: Optional[Environment] = None
        self._initial_memory = None
    
    def connect(
        self,
        environment: Environment,
        read_only: Optional[bool] = None,
        **kwargs
    ) -> duckdb.DuckDBPyConnection:
        """
        Connect to specified environment.
        
        Automatically closes previous connection if switching environments.
        
        Args:
            environment: Target environment
            read_only: Override default read-only setting
            **kwargs: Additional connection parameters
            
        Returns:
            Configured DuckDB connection
        """
        # Close existing connection if switching environments
        if self.current_connection and self.current_environment != environment:
            logger.info(f"Switching from {self.current_environment.value} to {environment.value}")
            self.close()
        
        # Get environment configuration
        config = ENVIRONMENT_CONFIG[environment]
        db_path = config['db_path']
        
        # Use environment default for read_only if not specified
        if read_only is None:
            read_only = config['read_only']
        
        # Check if database exists
        if not Path(db_path).exists() and environment != Environment.CLIENT:
            logger.warning(f"⚠️  Database not found: {db_path}")
            if environment == Environment.CLIENT:
                logger.info("Creating new client database for export preparation")
        
        # Create connection
        from src.data.duckdb_config import get_optimized_connection
        
        self.current_connection = get_optimized_connection(
            db_path=db_path,
            memory_limit=config['memory_limit'],
            threads=config['threads'],
            read_only=read_only,
            **kwargs
        )
        
        self.current_environment = environment
        self._initial_memory = self._get_memory_usage()
        
        logger.info(
            f"✅ Connected to {environment.value} environment\n"
            f"   Database: {db_path}\n"
            f"   Memory Limit: {config['memory_limit']}\n"
            f"   Threads: {config['threads']}\n"
            f"   Description: {config['description']}"
        )
        
        # Pre-warm buffer pool for lab environment
        if environment == Environment.LAB:
            self._prewarm_buffer_pool()
        
        return self.current_connection
    
    def close(self) -> None:
        """
        Close current connection and clean up resources.
        
        Ensures memory is released properly.
        """
        if self.current_connection:
            env_name = self.current_environment.value if self.current_environment else "unknown"
            
            self.current_connection.close()
            self.current_connection = None
            
            # Force garbage collection to release memory
            gc.collect()
            
            final_memory = self._get_memory_usage()
            memory_freed = self._initial_memory - final_memory if self._initial_memory else 0
            
            logger.info(
                f"🛑 Closed {env_name} environment\n"
                f"   Memory freed: {memory_freed:.1f} GB"
            )
            
            self.current_environment = None
            self._initial_memory = None
    
    def get_current_environment(self) -> Optional[Environment]:
        """Get currently active environment."""
        return self.current_environment
    
    def get_connection(self) -> Optional[duckdb.DuckDBPyConnection]:
        """Get current connection (if any)."""
        return self.current_connection
    
    def is_connected(self) -> bool:
        """Check if currently connected to an environment."""
        return self.current_connection is not None
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get information about current environment."""
        if not self.current_environment:
            return {'status': 'not_connected'}
        
        config = ENVIRONMENT_CONFIG[self.current_environment]
        
        info = {
            'environment': self.current_environment.value,
            'database': config['db_path'],
            'memory_limit': config['memory_limit'],
            'threads': config['threads'],
            'description': config['description'],
            'read_only': config['read_only'],
            'connected': self.is_connected(),
        }
        
        if self.current_connection:
            try:
                # Get table count
                table_count = self.current_connection.execute(
                    "SELECT COUNT(*) FROM duckdb_tables()"
                ).fetchone()[0]
                info['table_count'] = table_count
                
                # Get current memory usage
                info['memory_usage_gb'] = self._get_memory_usage()
            except:
                pass
        
        return info
    
    def _prewarm_buffer_pool(self) -> None:
        """Pre-warm buffer pool by loading key tables into memory."""
        if not self.current_connection:
            return
        
        try:
            logger.info("🔥 Pre-warming buffer pool...")
            
            # Load key tables into memory
            key_tables = [
                'fact_sales_lines',
                'fact_stock_mutations',
                'dim_products',
                'dim_locations',
            ]
            
            for table in key_tables:
                try:
                    count = self.current_connection.execute(
                        f"SELECT COUNT(*) FROM {table}"
                    ).fetchone()[0]
                    logger.debug(f"   Loaded {table}: {count:,} rows")
                except:
                    pass  # Table might not exist
            
            logger.info("✅ Buffer pool warmed - queries will run from RAM")
            
        except Exception as e:
            logger.warning(f"Could not pre-warm buffer pool: {e}")
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in GB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / (1024 ** 3)
        except:
            return 0.0
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class EnvironmentSession:
    """
    Context manager for single-environment sessions.
    
    Ensures connection is properly closed and resources released.
    
    Example:
        >>> with EnvironmentSession(Environment.LAB) as conn:
        ...     df = conn.execute("SELECT ...").fetchdf()
        # Connection automatically closed, memory released
    """
    
    def __init__(
        self,
        environment: Environment,
        read_only: Optional[bool] = None,
        **kwargs
    ):
        self.environment = environment
        self.read_only = read_only
        self.kwargs = kwargs
        self.manager = EnvironmentManager()
    
    def __enter__(self) -> duckdb.DuckDBPyConnection:
        return self.manager.connect(
            self.environment,
            read_only=self.read_only,
            **self.kwargs
        )
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.manager.close()


def get_environment_connection(
    environment: Environment,
    read_only: Optional[bool] = None
) -> duckdb.DuckDBPyConnection:
    """
    Get connection to specified environment.
    
    Note: Use EnvironmentManager for automatic cleanup when switching,
    or EnvironmentSession for context-managed connections.
    
    Args:
        environment: Target environment
        read_only: Override default read-only setting
        
    Returns:
        Configured DuckDB connection
    """
    config = ENVIRONMENT_CONFIG[environment]
    
    from src.data.duckdb_config import get_optimized_connection
    
    if read_only is None:
        read_only = config['read_only']
    
    return get_optimized_connection(
        db_path=config['db_path'],
        memory_limit=config['memory_limit'],
        threads=config['threads'],
        read_only=read_only,
    )


def list_environments() -> List[Dict[str, Any]]:
    """
    List all available environments and their configurations.
    
    Returns:
        List of environment information dictionaries
    """
    environments = []
    
    for env in Environment:
        config = ENVIRONMENT_CONFIG[env]
        
        info = {
            'environment': env.value,
            'database': config['db_path'],
            'exists': Path(config['db_path']).exists(),
            'size_mb': Path(config['db_path']).stat().st_size / (1024**2) 
                       if Path(config['db_path']).exists() else 0,
            'memory_limit': config['memory_limit'],
            'threads': config['threads'],
            'description': config['description'],
            'read_only_default': config['read_only'],
        }
        
        environments.append(info)
    
    return environments


def get_system_resources() -> Dict[str, Any]:
    """
    Get current system resource usage.
    
    Returns:
        Dictionary with CPU, memory, and disk information
    """
    mem = psutil.virtual_memory()
    
    return {
        'cpu_count': psutil.cpu_count(logical=False),
        'cpu_count_logical': psutil.cpu_count(),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_total_gb': mem.total / (1024 ** 3),
        'memory_available_gb': mem.available / (1024 ** 3),
        'memory_used_gb': mem.used / (1024 ** 3),
        'memory_percent': mem.percent,
    }


# Export key classes and functions
__all__ = [
    'Environment',
    'EnvironmentManager',
    'EnvironmentSession',
    'get_environment_connection',
    'list_environments',
    'get_system_resources',
    'ENVIRONMENT_CONFIG',
]

