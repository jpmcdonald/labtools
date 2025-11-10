from pathlib import Path

import pytest

from labtools.requirements.sync import sync_requirements

pytestmark = pytest.mark.unit


def test_sync_requirements(tmp_path: Path):
    source = tmp_path / "source" / "requirements"
    dest = tmp_path / "dest"
    source.mkdir(parents=True)
    (source / "requirements.txt").write_text("click>=8.1\n", encoding="utf-8")

    sync_requirements(source_root=source, destination_root=dest, files=["requirements.txt"])

    copied = dest / "requirements.txt"
    assert copied.exists()
    assert "click>=8.1" in copied.read_text(encoding="utf-8")


def test_sync_requirements_missing_file(tmp_path: Path):
    source = tmp_path / "source" / "requirements"
    dest = tmp_path / "dest"
    source.mkdir(parents=True)

    try:
        sync_requirements(source_root=source, destination_root=dest, files=["missing.txt"])
    except FileNotFoundError as exc:
        assert "missing.txt" in str(exc)
    else:
        raise AssertionError("Expected FileNotFoundError for missing requirements file")

