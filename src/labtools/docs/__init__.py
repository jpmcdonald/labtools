"""
Documentation template utilities for labtools.

Provides helpers to import sanitized markdown templates from a legacy project
and make them available to new lab scaffolds.
"""

from .sync import sync_docs

__all__ = ["sync_docs"]


