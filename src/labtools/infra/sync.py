"""Utilities for importing Terraform/IaC modules into labtools templates."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable


def sync_modules(source_root: Path, destination_root: Path, modules: Iterable[str]) -> None:
    """Copy selected Terraform modules from a filtered source checkout into templates.

    Parameters
    ----------
    source_root:
        The root path containing extracted tooling (e.g., `source-sparse/tools/infra`).
    destination_root:
        The labtools templates directory where modules should be staged (e.g., `templates/infra`).
    modules:
        Iterable of module relative paths to copy (e.g., `modules/networking`).
    """

    source_root = source_root.resolve()
    destination_root = destination_root.resolve()
    destination_root.mkdir(parents=True, exist_ok=True)

    for module in modules:
        module_path = source_root / module
        if not module_path.exists():
            raise FileNotFoundError(f"Module '{module}' not found under {source_root}")

        target_path = destination_root / module
        if target_path.exists():
            shutil.rmtree(target_path)

        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(module_path, target_path)


