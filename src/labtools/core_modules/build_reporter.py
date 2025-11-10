"""Build Reporter - Comprehensive Build Report Generation

Generates detailed markdown and JSON reports for build runs including:
- Run metadata and configuration
- Table inventory with schemas and row counts
- Table hashes for reproducibility
- Validation results from all validation scripts
- Data quality metrics and statistical summaries
- Step execution logs and timing
- Warnings and errors summary

Author: Build Pipeline Enhancement
Date: 2025-10-29
"""

import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import duckdb
import pandas as pd


class BuildReporter:
    """Generates comprehensive build reports with all metadata and validation results."""
    
    def __init__(self, run_id: str, env: str, datamart_path: str, log_dir: Path):
        self.run_id = run_id
        self.env = env
        self.datamart_path = datamart_path
        self.log_dir = log_dir
        self.logger = logging.getLogger(f'build_reporter_{run_id}')
        
        # Report data storage
        self.report_data = {
            'run_metadata': {},
            'configuration': {},
            'table_inventory': {},
            'table_hashes': {},
            'validation_results': {},
            'voi_analysis_results': {},
            'data_quality_metrics': {},
            'statistical_summaries': {},
            'data_lineage': {},
            'step_execution_log': [],
            'warnings_errors': {
                'warnings': [],
                'errors': []
            }
        }
    
    def generate_comprehensive_report(self, 
                                    config: Dict[str, Any],
                                    step_results: List[Dict[str, Any]],
                                    validation_results: Dict[str, Any],
                                    start_time: datetime,
                                    end_time: datetime,
                                    voi_analysis_results: Dict[str, Any] = None) -> Tuple[Path, Path]:
        """Generate comprehensive markdown and JSON reports.
        
        Args:
            config: Build configuration
            step_results: Results from each build step
            validation_results: Results from validation scripts
            start_time: Build start time
            end_time: Build end time
            voi_analysis_results: Optional results from VOI analysis scripts
            
        Returns:
            Tuple of (markdown_report_path, json_report_path)
        """
        self.logger.info(f"Generating comprehensive report for run {self.run_id}")
        
        # Populate report data
        self._populate_run_metadata(config, start_time, end_time)
        self._populate_configuration(config)
        self._populate_table_inventory()
        self._populate_table_hashes()
        self._populate_validation_results(validation_results)
        if voi_analysis_results:
            self._populate_voi_analysis_results(voi_analysis_results)
        self._populate_data_quality_metrics()
        self._populate_statistical_summaries()
        self._populate_data_lineage(config)
        self._populate_step_execution_log(step_results)
        self._populate_warnings_errors(step_results, validation_results, voi_analysis_results)
        
        # Generate reports
        markdown_path = self._generate_markdown_report()
        json_path = self._generate_json_report()
        
        self.logger.info(f"Reports generated: {markdown_path}, {json_path}")
        return markdown_path, json_path
    
    def _populate_run_metadata(self, config: Dict[str, Any], start_time: datetime, end_time: datetime):
        """Populate run metadata section."""
        duration = end_time - start_time
        
        self.report_data['run_metadata'] = {
            'run_id': self.run_id,
            'environment': self.env,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'duration_human': str(duration),
            'datamart_path': self.datamart_path,
            'log_directory': str(self.log_dir),
            'build_status': 'SUCCESS' if not self._has_errors() else 'FAILED'
        }
    
    def _populate_configuration(self, config: Dict[str, Any]):
        """Populate configuration summary section."""
        env_config = config.get('environments', {}).get(self.env, {})
        steps_config = env_config.get('steps', {})
        
        self.report_data['configuration'] = {
            'environment': self.env,
            'input_root': env_config.get('input_root', 'N/A'),
            'output_root': env_config.get('output_root', 'N/A'),
            'enabled_steps': [step for step, enabled in steps_config.items() if enabled],
            'disabled_steps': [step for step, enabled in steps_config.items() if not enabled],
            'total_steps': len(steps_config),
            'enabled_count': sum(1 for enabled in steps_config.values() if enabled),
            'run_metadata': config.get('run_metadata', {})
        }
    
    def _populate_table_inventory(self):
        """Populate table inventory with schemas and row counts."""
        try:
            conn = duckdb.connect(self.datamart_path)
            
            # Get all tables
            tables_result = conn.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'main'
                ORDER BY table_name
            """).fetchall()
            
            for (table_name,) in tables_result:
                # Get row count
                count_result = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
                row_count = count_result[0] if count_result else 0
                
                # Get schema
                schema_result = conn.execute(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}' AND table_schema = 'main'
                    ORDER BY ordinal_position
                """).fetchall()
                
                schema = [
                    {
                        'column': col[0],
                        'type': col[1],
                        'nullable': col[2] == 'YES'
                    }
                    for col in schema_result
                ]
                
                self.report_data['table_inventory'][table_name] = {
                    'row_count': row_count,
                    'column_count': len(schema),
                    'schema': schema
                }
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error populating table inventory: {e}")
            self.report_data['warnings_errors']['errors'].append(f"Table inventory error: {e}")
    
    def _populate_table_hashes(self):
        """Calculate SHA256 hashes for all tables for reproducibility."""
        try:
            conn = duckdb.connect(self.datamart_path)
            
            for table_name in self.report_data['table_inventory'].keys():
                # Export table to parquet and calculate hash
                temp_parquet = self.log_dir / f"temp_{table_name}.parquet"
                
                conn.execute(f"""
                    COPY (SELECT * FROM {table_name} ORDER BY 1) 
                    TO '{temp_parquet}' (FORMAT PARQUET)
                """)
                
                # Calculate file hash
                with open(temp_parquet, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                
                self.report_data['table_hashes'][table_name] = {
                    'sha256': file_hash,
                    'file_size_bytes': temp_parquet.stat().st_size
                }
                
                # Clean up temp file
                temp_parquet.unlink()
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error calculating table hashes: {e}")
            self.report_data['warnings_errors']['errors'].append(f"Table hashes error: {e}")
    
    def _populate_validation_results(self, validation_results: Dict[str, Any]):
        """Populate validation results section."""
        self.report_data['validation_results'] = validation_results
    
    def _populate_voi_analysis_results(self, voi_analysis_results: Dict[str, Any]):
        """Populate VOI analysis results section."""
        self.report_data['voi_analysis_results'] = voi_analysis_results
    
    def _populate_data_quality_metrics(self):
        """Calculate data quality metrics for all tables."""
        try:
            conn = duckdb.connect(self.datamart_path)
            
            for table_name in self.report_data['table_inventory'].keys():
                metrics = {}
                
                # Get completeness metrics
                schema = self.report_data['table_inventory'][table_name]['schema']
                for col_info in schema:
                    col_name = col_info['column']
                    
                    # Count nulls
                    null_result = conn.execute(f"""
                        SELECT COUNT(*) 
                        FROM {table_name} 
                        WHERE {col_name} IS NULL
                    """).fetchone()
                    null_count = null_result[0] if null_result else 0
                    
                    total_rows = self.report_data['table_inventory'][table_name]['row_count']
                    completeness = (total_rows - null_count) / total_rows if total_rows > 0 else 0
                    
                    metrics[col_name] = {
                        'null_count': null_count,
                        'completeness': completeness,
                        'completeness_pct': round(completeness * 100, 2)
                    }
                
                # Get uniqueness metrics
                unique_result = conn.execute(f"SELECT COUNT(DISTINCT *) FROM {table_name}").fetchone()
                unique_count = unique_result[0] if unique_result else 0
                total_rows = self.report_data['table_inventory'][table_name]['row_count']
                uniqueness = unique_count / total_rows if total_rows > 0 else 0
                
                metrics['_table_uniqueness'] = {
                    'unique_rows': unique_count,
                    'total_rows': total_rows,
                    'uniqueness': uniqueness,
                    'uniqueness_pct': round(uniqueness * 100, 2)
                }
                
                self.report_data['data_quality_metrics'][table_name] = metrics
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error calculating data quality metrics: {e}")
            self.report_data['warnings_errors']['errors'].append(f"Data quality metrics error: {e}")
    
    def _populate_statistical_summaries(self):
        """Calculate statistical summaries for numeric columns."""
        try:
            conn = duckdb.connect(self.datamart_path)
            
            for table_name in self.report_data['table_inventory'].keys():
                schema = self.report_data['table_inventory'][table_name]['schema']
                numeric_cols = [col['column'] for col in schema if col['type'] in ['DOUBLE', 'INTEGER', 'BIGINT', 'DECIMAL']]
                
                if not numeric_cols:
                    continue
                
                summaries = {}
                for col in numeric_cols:
                    try:
                        stats_result = conn.execute(f"""
                            SELECT 
                                COUNT(*) as count,
                                MIN({col}) as min_val,
                                MAX({col}) as max_val,
                                AVG({col}) as mean_val,
                                STDDEV({col}) as stddev_val
                            FROM {table_name}
                            WHERE {col} IS NOT NULL
                        """).fetchone()
                        
                        if stats_result:
                            summaries[col] = {
                                'count': stats_result[0],
                                'min': stats_result[1],
                                'max': stats_result[2],
                                'mean': round(stats_result[3], 4) if stats_result[3] is not None else None,
                                'stddev': round(stats_result[4], 4) if stats_result[4] is not None else None
                            }
                    except Exception as e:
                        summaries[col] = {'error': str(e)}
                
                if summaries:
                    self.report_data['statistical_summaries'][table_name] = summaries
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error calculating statistical summaries: {e}")
            self.report_data['warnings_errors']['errors'].append(f"Statistical summaries error: {e}")
    
    def _populate_data_lineage(self, config: Dict[str, Any]):
        """Populate data lineage information."""
        # This would be enhanced to track actual data flow
        # For now, provide basic lineage based on configuration
        self.report_data['data_lineage'] = {
            'sources': {
                'mssql_tables': 'Archived parquet files from data/raw/archives/',
                'csv_files': 'External CSV files for seasonality, etc.',
                'model_outputs': 'ML model predictions and scores'
            },
            'processing_steps': config.get('environments', {}).get(self.env, {}).get('steps', {}),
            'outputs': {
                'datamart': self.datamart_path,
                'reports': str(self.log_dir),
                'logs': str(self.log_dir)
            }
        }
    
    def _populate_step_execution_log(self, step_results: List[Dict[str, Any]]):
        """Populate step execution log."""
        self.report_data['step_execution_log'] = step_results
    
    def _populate_warnings_errors(self, step_results: List[Dict[str, Any]], validation_results: Dict[str, Any], voi_analysis_results: Dict[str, Any] = None):
        """Populate warnings and errors summary."""
        # Collect from step results
        for step in step_results:
            if step.get('status') == 'error':
                self.report_data['warnings_errors']['errors'].append(f"Step {step['name']}: {step.get('error', 'Unknown error')}")
            elif step.get('status') == 'warning':
                self.report_data['warnings_errors']['warnings'].append(f"Step {step['name']}: {step.get('warning', 'Warning')}")
        
        # Collect from validation results
        for script_name, result in validation_results.items():
            if script_name == '_summary':  # Skip summary
                continue
            if isinstance(result, dict):
                if result.get('status') == 'error':
                    self.report_data['warnings_errors']['errors'].append(f"Validation {script_name}: {result.get('error', 'Unknown error')}")
                elif result.get('status') == 'warning':
                    self.report_data['warnings_errors']['warnings'].append(f"Validation {script_name}: {result.get('warning', 'Warning')}")
        
        # Collect from VOI analysis results
        if voi_analysis_results:
            for script_name, result in voi_analysis_results.items():
                if script_name == '_summary':  # Skip summary
                    continue
                if isinstance(result, dict):
                    if result.get('status') == 'error':
                        self.report_data['warnings_errors']['errors'].append(f"VOI Analysis {script_name}: {result.get('error', 'Unknown error')}")
                    elif result.get('status') == 'warning':
                        self.report_data['warnings_errors']['warnings'].append(f"VOI Analysis {script_name}: {result.get('warning', 'Warning')}")
    
    def _generate_markdown_report(self) -> Path:
        """Generate comprehensive markdown report."""
        report_path = self.log_dir / "build_report.md"
        
        with open(report_path, 'w') as f:
            f.write(f"# Build Report - {self.run_id}\n\n")
            f.write(f"**Environment**: {self.env}  \n")
            f.write(f"**Generated**: {datetime.now().isoformat()}  \n")
            f.write(f"**Status**: {self.report_data['run_metadata']['build_status']}  \n\n")
            
            # Run Metadata
            f.write("## Run Metadata\n\n")
            metadata = self.report_data['run_metadata']
            f.write(f"- **Run ID**: `{metadata['run_id']}`\n")
            f.write(f"- **Environment**: {metadata['environment']}\n")
            f.write(f"- **Start Time**: {metadata['start_time']}\n")
            f.write(f"- **End Time**: {metadata['end_time']}\n")
            f.write(f"- **Duration**: {metadata['duration_human']}\n")
            f.write(f"- **Datamart Path**: `{metadata['datamart_path']}`\n")
            f.write(f"- **Log Directory**: `{metadata['log_directory']}`\n\n")
            
            # Configuration Summary
            f.write("## Configuration Summary\n\n")
            config = self.report_data['configuration']
            f.write(f"- **Input Root**: `{config['input_root']}`\n")
            f.write(f"- **Output Root**: `{config['output_root']}`\n")
            f.write(f"- **Enabled Steps**: {config['enabled_count']}/{config['total_steps']}\n")
            f.write(f"- **Steps**: {', '.join(config['enabled_steps'])}\n\n")
            
            # Table Inventory
            f.write("## Table Inventory\n\n")
            f.write("| Table | Rows | Columns | Schema |\n")
            f.write("|-------|------|---------|--------|\n")
            for table_name, info in self.report_data['table_inventory'].items():
                schema_preview = ', '.join([f"{col['column']}:{col['type']}" for col in info['schema'][:3]])
                if len(info['schema']) > 3:
                    schema_preview += f" ... (+{len(info['schema'])-3} more)"
                f.write(f"| `{table_name}` | {info['row_count']:,} | {info['column_count']} | {schema_preview} |\n")
            f.write("\n")
            
            # Table Hashes
            f.write("## Table Hashes (for Reproducibility)\n\n")
            f.write("| Table | SHA256 Hash | File Size |\n")
            f.write("|-------|-------------|----------|\n")
            for table_name, hash_info in self.report_data['table_hashes'].items():
                f.write(f"| `{table_name}` | `{hash_info['sha256']}` | {hash_info['file_size_bytes']:,} bytes |\n")
            f.write("\n")
            
            # Validation Results
            f.write("## Validation Results\n\n")
            for script_name, result in self.report_data['validation_results'].items():
                if script_name == '_summary':  # Skip summary
                    continue
                if isinstance(result, dict):
                    status_icon = "✅" if result.get('status') == 'success' else "❌" if result.get('status') == 'error' else "⚠️"
                    f.write(f"### {script_name} {status_icon}\n")
                    f.write(f"- **Status**: {result.get('status', 'unknown')}\n")
                    f.write(f"- **Duration**: {result.get('duration', 'N/A')}s\n")
                    if result.get('output'):
                        f.write(f"- **Output**: {result['output'][:200]}{'...' if len(result['output']) > 200 else ''}\n")
                    f.write("\n")
            
            # VOI Analysis Results
            if 'voi_analysis_results' in self.report_data and self.report_data['voi_analysis_results']:
                f.write("## Value of Information (VOI) Analysis Results\n\n")
                voi_results = self.report_data['voi_analysis_results']
                if '_summary' in voi_results:
                    summary = voi_results['_summary']
                    f.write(f"### Summary\n\n")
                    f.write(f"- **Total Analyses**: {summary.get('total_count', 0)}\n")
                    f.write(f"- **Successful**: {summary.get('success_count', 0)}\n")
                    f.write(f"- **Warnings**: {summary.get('warning_count', 0)}\n")
                    f.write(f"- **Errors**: {summary.get('error_count', 0)}\n")
                    f.write(f"- **Success Rate**: {summary.get('success_rate', 0)}%\n")
                    f.write(f"- **Total Duration**: {summary.get('total_duration', 0)}s\n\n")
                
                for script_name, result in voi_results.items():
                    if script_name == '_summary':  # Skip summary (already shown)
                        continue
                    if isinstance(result, dict):
                        status_icon = "✅" if result.get('status') == 'success' else "❌" if result.get('status') == 'error' else "⚠️"
                        f.write(f"### {script_name} {status_icon}\n")
                        f.write(f"- **Status**: {result.get('status', 'unknown')}\n")
                        f.write(f"- **Duration**: {result.get('duration', 'N/A')}s\n")
                        if result.get('output'):
                            f.write(f"- **Output**: {result['output'][:200]}{'...' if len(result['output']) > 200 else ''}\n")
                        f.write("\n")
            
            # Data Quality Metrics
            f.write("## Data Quality Metrics\n\n")
            for table_name, metrics in self.report_data['data_quality_metrics'].items():
                f.write(f"### {table_name}\n")
                f.write(f"- **Table Uniqueness**: {metrics.get('_table_uniqueness', {}).get('uniqueness_pct', 'N/A')}%\n")
                f.write(f"- **Column Completeness**:\n")
                for col_name, col_metrics in metrics.items():
                    if col_name != '_table_uniqueness':
                        f.write(f"  - `{col_name}`: {col_metrics.get('completeness_pct', 'N/A')}%\n")
                f.write("\n")
            
            # Statistical Summaries
            f.write("## Statistical Summaries\n\n")
            for table_name, summaries in self.report_data['statistical_summaries'].items():
                f.write(f"### {table_name}\n")
                for col_name, stats in summaries.items():
                    if 'error' not in stats:
                        f.write(f"- **{col_name}**: count={stats.get('count', 'N/A')}, mean={stats.get('mean', 'N/A')}, stddev={stats.get('stddev', 'N/A')}\n")
                f.write("\n")
            
            # Step Execution Log
            f.write("## Step Execution Log\n\n")
            f.write("| Step | Status | Duration | Notes |\n")
            f.write("|------|--------|----------|-------|\n")
            for step in self.report_data['step_execution_log']:
                status_icon = "✅" if step.get('status') == 'success' else "❌" if step.get('status') == 'error' else "⚠️"
                f.write(f"| {step.get('name', 'unknown')} | {status_icon} {step.get('status', 'unknown')} | {step.get('duration', 'N/A')}s | {step.get('notes', '')} |\n")
            f.write("\n")
            
            # Warnings and Errors
            warnings = self.report_data['warnings_errors']['warnings']
            errors = self.report_data['warnings_errors']['errors']
            
            if warnings:
                f.write("## Warnings\n\n")
                for warning in warnings:
                    f.write(f"- ⚠️ {warning}\n")
                f.write("\n")
            
            if errors:
                f.write("## Errors\n\n")
                for error in errors:
                    f.write(f"- ❌ {error}\n")
                f.write("\n")
            
            # Data Lineage
            f.write("## Data Lineage\n\n")
            lineage = self.report_data['data_lineage']
            f.write("### Sources\n")
            for source, desc in lineage.get('sources', {}).items():
                f.write(f"- **{source}**: {desc}\n")
            f.write("\n### Outputs\n")
            for output, path in lineage.get('outputs', {}).items():
                f.write(f"- **{output}**: `{path}`\n")
            f.write("\n")
        
        return report_path
    
    def _generate_json_report(self) -> Path:
        """Generate JSON report for machine parsing."""
        report_path = self.log_dir / "build_report.json"
        
        with open(report_path, 'w') as f:
            json.dump(self.report_data, f, indent=2, default=str)
        
        return report_path
    
    def _has_errors(self) -> bool:
        """Check if there are any errors in the build."""
        return len(self.report_data['warnings_errors']['errors']) > 0
