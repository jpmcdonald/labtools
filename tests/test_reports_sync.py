from pathlib import Path

import pytest

from labtools.reports.sync import sync_reports

pytestmark = pytest.mark.unit


def test_sync_reports(tmp_path: Path):
    source = tmp_path / "source" / "reports"
    dest = tmp_path / "dest"
    generator_dir = source / "generator"
    generator_dir.mkdir(parents=True)
    (generator_dir / "__init__.py").write_text("def generate():\n    return {}", encoding="utf-8")

    sync_reports(source_root=source, destination_root=dest, modules=["generator"])

    copied = dest / "generator" / "__init__.py"
    assert copied.exists()
    assert "def generate" in copied.read_text(encoding="utf-8")

