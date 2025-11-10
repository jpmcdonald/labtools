"""Utilities for importing requirements files."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable


def sync_requirements(source_root: Path, destination_root: Path, files: Iterable[str]) -> None:
    """Copy requirements files from the source export into the labtools repository."""

    source_root = source_root.resolve()
    destination_root = destination_root.resolve()
    destination_root.mkdir(parents=True, exist_ok=True)

    for file_name in files:
        source_file = source_root / file_name
        if not source_file.exists():
            raise FileNotFoundError(f"Requirements file '{file_name}' not found under {source_root}")

        target_file = destination_root / source_file.name
        shutil.copy2(source_file, target_file)


