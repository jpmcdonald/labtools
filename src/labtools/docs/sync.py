"""Utilities for importing documentation templates."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable


def sync_docs(source_root: Path, destination_root: Path, documents: Iterable[str]) -> None:
    """Copy documentation templates into the labtools templates directory."""

    source_root = source_root.resolve()
    destination_root = destination_root.resolve()
    destination_root.mkdir(parents=True, exist_ok=True)

    for document in documents:
        document_path = source_root / document
        if not document_path.exists():
            raise FileNotFoundError(f"Document '{document}' not found under {source_root}")

        target_path = destination_root / Path(document).name
        shutil.copy2(document_path, target_path)


