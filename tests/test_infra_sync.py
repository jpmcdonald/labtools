from pathlib import Path

import pytest

from labtools.infra.sync import sync_modules

pytestmark = pytest.mark.unit


def test_sync_modules(tmp_path: Path):
    source = tmp_path / "source"
    dest = tmp_path / "dest"
    module = source / "modules" / "networking"
    module.mkdir(parents=True)
    (module / "main.tf").write_text('module "networking" {}', encoding="utf-8")

    sync_modules(source_root=source, destination_root=dest, modules=["modules/networking"])

    copied = dest / "modules" / "networking" / "main.tf"
    assert copied.exists()
    assert copied.read_text(encoding="utf-8") == 'module "networking" {}'

