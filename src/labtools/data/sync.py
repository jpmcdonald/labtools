"""Utilities for importing reusable data modules."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable


def sync_data_modules(source_root: Path, destination_root: Path, modules: Iterable[str]) -> None:
    """Copy selected data utilities from the legacy `src/data` tree.

    Parameters
    ----------
    source_root:
        Path pointing to `src/data` within the sanitized source checkout.
    destination_root:
        Location where modules should be staged (e.g., `src/labtools/data_modules`).
    modules:
        Iterable of directories or files to copy (e.g., `["loaders", "quality/checks.py"]`).
    """

    source_root = source_root.resolve()
    destination_root = destination_root.resolve()
    destination_root.mkdir(parents=True, exist_ok=True)

    for module in modules:
        module_path = source_root / module
        if not module_path.exists():
            raise FileNotFoundError(f"Data module '{module}' not found under {source_root}")

        target_path = destination_root / module_path.name
        if target_path.exists():
            if target_path.is_dir():
                shutil.rmtree(target_path)
            else:
                target_path.unlink()

        if module_path.is_dir():
            shutil.copytree(module_path, target_path)
        else:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(module_path, target_path)


