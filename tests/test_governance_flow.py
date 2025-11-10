from pathlib import Path

import pytest

from labtools.core_modules.run_context import RunContext
from labtools.core_modules.execution_enforcer import ExecutionEnforcer
from labtools.core_modules.diagnostics import DiagnosticsEngine

pytestmark = pytest.mark.governance


def test_governance_flow(tmp_path: Path, monkeypatch):
    # Establish run context
    ctx = RunContext(env="dev", diag_level=2)
    artifact = tmp_path / "artifact.txt"
    artifact.write_text("test", encoding="utf-8")
    ctx.register_artifact(artifact)

    # Diagnostics at level 1 should analyse artifact
    engine = DiagnosticsEngine()
    result = engine.run_diagnostics(1, [artifact])
    assert result["artifacts_analyzed"] == 1

    # Execution enforcer should validate context
    enforcer = ExecutionEnforcer()
    assert enforcer.validate_run_context()

    # Remove required env var and ensure validation fails
    monkeypatch.delenv("LAB_RUN_ID", raising=False)
    assert not enforcer.validate_run_context()

    # Finalize run and ensure summary contains artefact information
    summary = ctx.finalize_run()
    assert summary["artifacts"]
    assert summary["diag_level"] == 2

