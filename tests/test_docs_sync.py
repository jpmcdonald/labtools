from pathlib import Path

import pytest

from labtools.docs.sync import sync_docs

pytestmark = pytest.mark.unit


def test_sync_docs(tmp_path: Path):
    source = tmp_path / "source"
    dest = tmp_path / "dest"
    document = source / "doc" / "templates" / "status-report.md"
    document.parent.mkdir(parents=True)
    document.write_text("# Status", encoding="utf-8")

    sync_docs(source_root=source, destination_root=dest, documents=["doc/templates/status-report.md"])

    copied = dest / "status-report.md"
    assert copied.exists()
    assert copied.read_text(encoding="utf-8") == "# Status"

