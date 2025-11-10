"""
Infrastructure module synchronization and helpers.

The infra subpackage provides utilities to stage Terraform and IaC assets
extracted from a legacy repository into the reusable labtools templates.
"""

from .sync import sync_modules

__all__ = ["sync_modules"]


