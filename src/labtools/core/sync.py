"""Utilities for importing core Python modules."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable


def sync_core(source_root: Path, destination_root: Path, modules: Iterable[str]) -> None:
    """Copy selected Python modules/packages from the legacy `src/core` tree.

    Parameters
    ----------
    source_root:
        Path pointing to the filtered source checkout `src/core`.
    destination_root:
        Path under labtools where the modules should be staged (e.g., `src/labtools/core_modules`).
    modules:
        Iterable of module names (e.g., `["utils", "config"]`) relative to `source_root`.
    """

    source_root = source_root.resolve()
    destination_root = destination_root.resolve()
    destination_root.mkdir(parents=True, exist_ok=True)

    for module in modules:
        module_path = source_root / module
        if not module_path.exists():
            raise FileNotFoundError(f"Core module '{module}' not found under {source_root}")

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


