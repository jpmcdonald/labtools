import os
from pathlib import Path

import pytest

from labtools.core_modules.execution_enforcer import ExecutionEnforcer

pytestmark = pytest.mark.unit


def test_execution_enforcer_validates_context(monkeypatch):
    enforcer = ExecutionEnforcer()
    # Without run context the validation should fail
    monkeypatch.delenv("LAB_RUN_ID", raising=False)
    monkeypatch.delenv("LAB_RUN_TOKEN", raising=False)
    assert not enforcer.validate_run_context()

    monkeypatch.setenv("LAB_RUN_ID", "test")
    monkeypatch.setenv("LAB_RUN_TOKEN", "token")
    assert enforcer.validate_run_context()


def test_execution_enforcer_detects_throwaway_patterns(tmp_path: Path):
    script = tmp_path / "script.py"
    script.write_text("print('hello world')\n")
    enforcer = ExecutionEnforcer()
    violations = enforcer.check_throwaway_patterns(script)
    assert any("Print statements" in violation for violation in violations)

