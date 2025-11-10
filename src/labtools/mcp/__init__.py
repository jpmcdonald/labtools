"""
MCP tool synchronization helpers.

Handles importing MCP (model control plane) utilities from a legacy `src/mcp`
tree into the labtools package.
"""

from .sync import sync_mcp_tools

__all__ = ["sync_mcp_tools"]


