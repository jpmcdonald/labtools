"""Run Context Management for LabTools Compliance

Implements Section 25.1 of LabTools specification:
- Run Context Contract with required environment variables
- Artifact tracking and evidence collection
- Run finalization and manifest generation
"""

import os
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid


class RunContext:
    """Manages run context and enforces LabTools compliance.
    
    Every governed action (DB/file/graph/report/feature/model/ledger) 
    must occur within a verified Run Context.
    """
    
    def __init__(self, run_id: Optional[str] = None, diag_level: int = 3, 
                 ruleset: str = "default", env: str = "test"):
        """Initialize run context.
        
        Args:
            run_id: Unique run identifier (generated if not provided)
            diag_level: Diagnostics level (0-9)
            ruleset: Ruleset version identifier
            env: Environment (test/dev/stage/lab/audit)
        """
        self.diag_level = diag_level
        self.ruleset = ruleset
        self.env = env
        self.run_id = run_id or self._generate_run_id()
        self.start_time = datetime.now()
        self.artifacts: List[Dict[str, Any]] = []
        self.audit_log: List[Dict[str, Any]] = []
        self.run_token = self._generate_run_token()
        
        # Set required environment variables
        self._set_environment_variables()
        
    def _generate_run_id(self) -> str:
        """Generate unique run ID with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}_{self.env}_{uuid.uuid4().hex[:8]}"
    
    def _generate_run_token(self) -> str:
        """Generate short-lived run token."""
        return f"lab_{uuid.uuid4().hex[:16]}"
    
    def _set_environment_variables(self):
        """Set required environment variables for governed I/O.
        
        Returns:
            Dictionary of environment variables for subprocess execution.
        """
        os.environ['LAB_RUN_ID'] = self.run_id
        os.environ['LAB_RUN_TOKEN'] = self.run_token
        os.environ['LAB_DIAG'] = str(self.diag_level)
        os.environ['LAB_RULESET'] = self.ruleset
        os.environ['GIT_SHA'] = self._get_git_sha()
        os.environ['DVC_REV'] = self._get_dvc_rev()
        return os.environ.copy()
        
    def _get_git_sha(self) -> str:
        """Get current git commit SHA."""
        try:
            import subprocess
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "unknown"
    
    def _get_dvc_rev(self) -> str:
        """Get current DVC revision."""
        try:
            import subprocess
            result = subprocess.run(['dvc', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "unknown"
    
    def validate_context(self) -> bool:
        """Validate that run context is properly initialized.
        
        Returns:
            True if context is valid, False otherwise
        """
        required_vars = ['LAB_RUN_ID', 'LAB_RUN_TOKEN', 'LAB_DIAG', 'LAB_RULESET']
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            print(f"ERROR: Missing required run context variables: {missing}")
            print("Use 'lab run ...' to execute code.")
            return False
        
        return True
    
    def register_artifact(self, path: Path, artifact_type: str = "file", 
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """Register an artifact created during this run.
        
        Args:
            path: Path to the artifact
            artifact_type: Type of artifact (file, model, report, etc.)
            metadata: Additional metadata about the artifact
            
        Returns:
            Artifact hash for tracking
        """
        if not path.exists():
            raise FileNotFoundError(f"Artifact not found: {path}")
        
        # Calculate file hash
        artifact_hash = self._calculate_file_hash(path)
        
        artifact_info = {
            'path': str(path),
            'type': artifact_type,
            'hash': artifact_hash,
            'size': path.stat().st_size,
            'created_at': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.artifacts.append(artifact_info)
        
        # Log artifact creation
        self.audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'artifact_created',
            'artifact_path': str(path),
            'artifact_hash': artifact_hash,
            'artifact_type': artifact_type
        })
        
        return artifact_hash
    
    def _calculate_file_hash(self, path: Path) -> str:
        """Calculate SHA-256 hash of file."""
        hash_sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def log_operation(self, operation: str, details: Dict[str, Any]):
        """Log an operation for audit trail.
        
        Args:
            operation: Type of operation performed
            details: Additional details about the operation
        """
        self.audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': operation,
            'details': details
        })
    
    def finalize_run(self) -> Dict[str, Any]:
        """Finalize run and create evidence manifest.
        
        Returns:
            Run summary with artifacts and audit log
        """
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        run_summary = {
            'run_id': self.run_id,
            'diag_level': self.diag_level,
            'ruleset': self.ruleset,
            'env': self.env,
            'start_time': self.start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'artifacts': self.artifacts,
            'audit_log': self.audit_log,
            'git_sha': os.getenv('GIT_SHA', 'unknown'),
            'dvc_rev': os.getenv('DVC_REV', 'unknown')
        }
        
        # Save run summary to logs
        self._save_run_summary(run_summary)
        
        return run_summary
    
    def _save_run_summary(self, run_summary: Dict[str, Any]):
        """Save run summary to logs directory."""
        logs_dir = Path("logs/runs") / self.run_id
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Save run summary
        with open(logs_dir / "run_summary.json", 'w') as f:
            json.dump(run_summary, f, indent=2)
        
        # Save artifact manifest
        with open(logs_dir / "artifact_manifest.json", 'w') as f:
            json.dump(self.artifacts, f, indent=2)
        
        # Save audit log
        with open(logs_dir / "audit_log.json", 'w') as f:
            json.dump(self.audit_log, f, indent=2)
        
        print(f"Run context finalized: {self.run_id}")
        print(f"Evidence saved to: {logs_dir}")


def validate_run_context() -> bool:
    """Validate run context for current process.
    
    This function should be called by any governed I/O operation
    to ensure it's running within a proper run context.
    
    Returns:
        True if context is valid, False otherwise
    """
    required_vars = ['LAB_RUN_ID', 'LAB_RUN_TOKEN']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print("ERROR: Missing required run context variables:", missing)
        print("Use 'lab run ...' to execute code.")
        return False
    
    return True
