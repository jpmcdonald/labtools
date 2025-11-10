from pathlib import Path

import pytest

from labtools.shell.sync import sync_helpers

pytestmark = pytest.mark.unit


def test_sync_helpers(tmp_path: Path):
    source = tmp_path / "source"
    dest = tmp_path / "dest"
    source.mkdir()
    dest.mkdir()
    helper = source / "lib" / "logging.sh"
    helper.parent.mkdir(parents=True)
    helper.write_text("#!/usr/bin/env bash\necho log", encoding="utf-8")

    sync_helpers(source_root=source, destination_root=dest, helpers=["lib/logging.sh"])

    copied = dest / "logging.sh"
    assert copied.exists()
    assert copied.read_text(encoding="utf-8").startswith("#!/usr/bin/env bash")

