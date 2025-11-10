from pathlib import Path

import pytest

from labtools.core.sync import sync_core

pytestmark = pytest.mark.unit


def test_sync_core(tmp_path: Path):
    source = tmp_path / "source" / "core"
    dest = tmp_path / "dest"
    module_dir = source / "utils"
    module_dir.mkdir(parents=True)
    (module_dir / "__init__.py").write_text("def foo():\n    return 1\n", encoding="utf-8")

    sync_core(source_root=source, destination_root=dest, modules=["utils"])

    copied = dest / "utils" / "__init__.py"
    assert copied.exists()
    assert "def foo" in copied.read_text(encoding="utf-8")

