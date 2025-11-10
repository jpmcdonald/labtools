from pathlib import Path

import pytest

from labtools.runtime.sync import sync_runtime_modules

pytestmark = pytest.mark.unit


def test_sync_runtime_modules(tmp_path: Path):
    source = tmp_path / "source" / "runtime"
    dest = tmp_path / "dest"
    jobs = source / "jobs.py"
    jobs.parent.mkdir(parents=True)
    jobs.write_text("class SignalController: ...", encoding="utf-8")

    sync_runtime_modules(source_root=source, destination_root=dest, modules=["jobs.py"])

    copied = dest / "jobs.py"
    assert copied.exists()
    assert "SignalController" in copied.read_text(encoding="utf-8")

