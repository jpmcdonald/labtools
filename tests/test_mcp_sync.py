from pathlib import Path

import pytest

from labtools.mcp.sync import sync_mcp_tools

pytestmark = pytest.mark.unit


def test_sync_mcp_tools(tmp_path: Path):
    source = tmp_path / "source" / "mcp"
    dest = tmp_path / "dest"
    tool_dir = source / "orchestrator"
    tool_dir.mkdir(parents=True)
    (tool_dir / "__init__.py").write_text("def orchestrate():\n    return True", encoding="utf-8")

    sync_mcp_tools(source_root=source, destination_root=dest, modules=["orchestrator"])

    copied = dest / "orchestrator" / "__init__.py"
    assert copied.exists()
    assert "def orchestrate" in copied.read_text(encoding="utf-8")

