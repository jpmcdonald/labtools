import os
from pathlib import Path

import pytest

from labtools.core_modules.run_context import RunContext

pytestmark = pytest.mark.unit


def test_run_context_sets_environment(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("LAB_RUN_ID", raising=False)
    ctx = RunContext(env="test")
    assert os.getenv("LAB_RUN_ID") == ctx.run_id
    assert os.getenv("LAB_RUN_TOKEN") == ctx.run_token
    # Register a temporary artifact
    artifact = tmp_path / "artifact.txt"
    artifact.write_text("content")
    artifact_hash = ctx.register_artifact(artifact)
    assert len(artifact_hash) == 64  # sha256 hex
    summary = ctx.finalize_run()
    assert summary["run_id"] == ctx.run_id

