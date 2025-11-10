from pathlib import Path

import pytest

from labtools.data.sync import sync_data_modules

pytestmark = pytest.mark.unit


def test_sync_data_modules(tmp_path: Path):
    source = tmp_path / "source" / "data"
    dest = tmp_path / "dest"
    loader_dir = source / "loaders"
    loader_dir.mkdir(parents=True)
    (loader_dir / "base.py").write_text("class Loader: ...", encoding="utf-8")

    sync_data_modules(source_root=source, destination_root=dest, modules=["loaders"])

    copied = dest / "loaders" / "base.py"
    assert copied.exists()
    assert "class Loader" in copied.read_text(encoding="utf-8")

