import json
from datetime import datetime
from pathlib import Path

import pytest

from labtools.core_modules.diagnostics import DiagnosticsEngine

pytestmark = pytest.mark.unit


def test_run_diagnostics_placeholder(tmp_path: Path):
    engine = DiagnosticsEngine()
    artifact = tmp_path / "artifact.txt"
    artifact.write_text("sample")

    result = engine.run_diagnostics(1, [artifact])
    assert result["level"] == 1
    assert result["artifacts_analyzed"] == 1
    assert "structure_check" in result


def test_generate_evidence_bundle(tmp_path: Path):
    engine = DiagnosticsEngine()
    bundle_path = engine.generate_evidence_bundle("test-run")
    assert bundle_path.exists()
    data = bundle_path.read_text()
    assert '"run_id": "test-run"' in data
    # Update timestamp to simulate caller behaviour
    updated = json.loads(data)
    updated["timestamp"] = datetime.utcnow().isoformat()
    bundle_path.write_text(json.dumps(updated))


