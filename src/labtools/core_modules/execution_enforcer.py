"""Execution Enforcer for LabTools Compliance

Implements Section 25.3 of LabTools specification:
- Python Runtime Hooks for transparent enforcement
- PEP 578 audit hooks for I/O monitoring
- Anti-bypass mechanisms to prevent throwaway code
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Set, Optional
import logging


class ExecutionEnforcer:
    """Enforces LabTools execution policies and prevents bypass.
    
    This class implements the anti-bypass mechanisms that ensure
    all governed I/O occurs within a proper run context.
    """
    
    def __init__(self, allowed_paths: Optional[List[Path]] = None):
        """Initialize execution enforcer.
        
        Args:
            allowed_paths: List of allowed paths for I/O operations
        """
        self.allowed_paths = set(allowed_paths or [])
        self.audit_hooks_enabled = False
        self.logger = logging.getLogger(__name__)
        
    def setup_audit_hooks(self):
        """Set up PEP 578 audit hooks for I/O monitoring."""
        if self.audit_hooks_enabled:
            return
            
        # Add audit hook for file operations
        sys.addaudithook(self._audit_hook)
        self.audit_hooks_enabled = True
        self.logger.info("Audit hooks enabled for I/O monitoring")
    
    def _audit_hook(self, event: str, args: tuple):
        """Audit hook for monitoring I/O operations.
        
        Args:
            event: Audit event name
            args: Event arguments
        """
        if event == 'open':
            self._audit_file_open(args)
        elif event == 'subprocess.Popen':
            self._audit_subprocess(args)
        elif event == 'import':
            self._audit_import(args)
    
    def _audit_file_open(self, args: tuple):
        """Audit file open operations."""
        if len(args) < 1:
            return
        
        # Skip if args[0] is not a string or path-like object
        if not isinstance(args[0], (str, bytes, os.PathLike)):
            return
            
        file_path = Path(args[0])
        
        # Check if file is in allowed paths
        if not self._is_path_allowed(file_path):
            self.logger.warning(f"File access outside allowed paths: {file_path}")
    
    def _audit_subprocess(self, args: tuple):
        """Audit subprocess creation."""
        if len(args) < 1:
            return
            
        cmd = args[0]
        if isinstance(cmd, (list, tuple)):
            cmd = ' '.join(cmd)
        
        # Check for direct python execution
        if 'python' in str(cmd) and 'lab run' not in str(cmd):
            self.logger.warning(f"Direct python execution detected: {cmd}")
            self.logger.warning("Use 'lab run ...' to execute code properly")
    
    def _audit_import(self, args: tuple):
        """Audit module imports."""
        if len(args) < 1:
            return
            
        module_name = args[0]
        
        # Check for suspicious imports that might indicate throwaway code
        suspicious_patterns = ['exec', 'eval', 'compile', 'globals', 'locals']
        if any(pattern in module_name for pattern in suspicious_patterns):
            self.logger.warning(f"Suspicious import detected: {module_name}")
    
    def _is_path_allowed(self, path: Path) -> bool:
        """Check if path is in allowed paths."""
        if not self.allowed_paths:
            return True  # No restrictions if no allowed paths set
        
        try:
            path = path.resolve()
            return any(path.is_relative_to(allowed) for allowed in self.allowed_paths)
        except (OSError, ValueError):
            return False
    
    def validate_run_context(self) -> bool:
        """Validate run context before allowing execution.
        
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
    
    def block_throwaway_execution(self):
        """Block execution outside of proper run context."""
        if not self.validate_run_context():
            sys.exit(1)
    
    def check_throwaway_patterns(self, script_path: Path) -> List[str]:
        """Check script for throwaway code patterns.
        
        Args:
            script_path: Path to script to check
            
        Returns:
            List of detected throwaway patterns
        """
        if not script_path.exists():
            return []
        
        patterns = [
            (r'print\(.*\)', 'Print statements (use logging instead)'),
            (r'# TODO.*', 'TODO comments (implement or remove)'),
            (r'# FIXME.*', 'FIXME comments (fix or remove)'),
            (r'import.*\*', 'Wildcard imports (import specific modules)'),
            (r'exec\(', 'Dynamic execution (use proper function calls)'),
            (r'eval\(', 'Dynamic evaluation (use proper parsing)'),
            (r'globals\(\)', 'Global variable access (use proper scope)'),
            (r'locals\(\)', 'Local variable access (use proper scope)'),
        ]
        
        violations = []
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            import re
            for i, line in enumerate(content.split('\n'), 1):
                for pattern, description in patterns:
                    if re.search(pattern, line):
                        violations.append(f"Line {i}: {description}")
        except Exception as e:
            violations.append(f"Error reading file: {e}")
        
        return violations
    
    def enforce_license_headers(self, script_path: Path) -> bool:
        """Check if script has proper license headers.
        
        Args:
            script_path: Path to script to check
            
        Returns:
            True if license header is present, False otherwise
        """
        if not script_path.exists():
            return False
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for license header patterns
            license_patterns = [
                'AGPL-3.0-only',
                'MIT License',
                'Apache License',
                'Copyright',
                'License:',
            ]
            
            return any(pattern in content for pattern in license_patterns)
        except Exception:
            return False
    
    def enforce_dvc_stage(self, script_path: Path) -> bool:
        """Check if script has corresponding DVC stage.
        
        Args:
            script_path: Path to script to check
            
        Returns:
            True if DVC stage exists, False otherwise
        """
        # Look for dvc.yaml or .dvc files
        dvc_files = [
            Path("dvc.yaml"),
            Path(".dvc"),
            script_path.with_suffix('.dvc'),
        ]
        
        return any(path.exists() for path in dvc_files)
    
    def enforce_tests(self, script_path: Path) -> bool:
        """Check if script has corresponding tests.
        
        Args:
            script_path: Path to script to check
            
        Returns:
            True if tests exist, False otherwise
        """
        # Look for test files
        test_patterns = [
            f"test_{script_path.stem}.py",
            f"{script_path.stem}_test.py",
            f"tests/test_{script_path.stem}.py",
        ]
        
        return any(Path(pattern).exists() for pattern in test_patterns)


def setup_sitecustomize():
    """Set up sitecustomize.py hook for automatic enforcement.
    
    This function should be called from sitecustomize.py to automatically
    enforce run context validation for every Python process.
    """
    enforcer = ExecutionEnforcer()
    enforcer.block_throwaway_execution()
    enforcer.setup_audit_hooks()
