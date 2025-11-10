"""Utilities for importing reusable shell helpers."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable


def sync_helpers(source_root: Path, destination_root: Path, helpers: Iterable[str]) -> None:
    """Copy selected shell helper scripts into the labtools repository.

    Parameters
    ----------
    source_root:
        Root directory containing the extracted shell helpers (e.g., `wair-sparse/scripts`).
    destination_root:
        Path where the helpers should be staged (e.g., `scripts/lib`).
    helpers:
        Iterable of relative file paths to copy (e.g., `lib/logging.sh`).
    """

    source_root = source_root.resolve()
    destination_root = destination_root.resolve()
    destination_root.mkdir(parents=True, exist_ok=True)

    for helper in helpers:
        helper_path = source_root / helper
        if not helper_path.exists():
            raise FileNotFoundError(f"Shell helper '{helper}' not found under {source_root}")

        target_path = destination_root / Path(helper).name
        shutil.copy2(helper_path, target_path)


