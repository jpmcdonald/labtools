"""Utilities for importing report generation modules."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable


def sync_reports(source_root: Path, destination_root: Path, modules: Iterable[str]) -> None:
    """Copy report generator components from the legacy `src/reports` tree."""

    source_root = source_root.resolve()
    destination_root = destination_root.resolve()
    destination_root.mkdir(parents=True, exist_ok=True)

    for module in modules:
        module_path = source_root / module
        if not module_path.exists():
            raise FileNotFoundError(f"Report module '{module}' not found under {source_root}")

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


