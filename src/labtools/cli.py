"""Command-line interface for labtools."""

from __future__ import annotations

import pathlib
from typing import Optional

import click

from .core import sync_core
from .data import sync_data_modules
from .docs import sync_docs
from .infra import sync_modules
from .mcp import sync_mcp_tools
from .reports import sync_reports
from .requirements import sync_requirements
from .runtime import sync_runtime_modules
from .shell import sync_helpers
from .scaffold import create_project


@click.group()
def main() -> None:
    """Reusable tooling for building new lab environments."""


@main.command("init")
@click.argument("destination", type=click.Path(file_okay=False, path_type=pathlib.Path))
@click.option(
    "--template",
    default="default",
    help="Name of the project template to apply (default: default).",
)
@click.option(
    "--config",
    type=click.Path(dir_okay=False, exists=False, path_type=pathlib.Path),
    help="Optional YAML configuration file to customize the template.",
)
def init_command(destination: pathlib.Path, template: str, config: Optional[pathlib.Path]) -> None:
    """Initialise a new lab project in DESTINATION."""

    create_project(destination=destination, template_name=template, config_path=config)
    click.echo(f"Lab project created at {destination}")


@main.group()
def infra() -> None:
    """Infrastructure module utilities."""


@infra.command("sync")
@click.argument("source", type=click.Path(file_okay=False, exists=True, path_type=pathlib.Path))
@click.argument("destination", type=click.Path(file_okay=False, path_type=pathlib.Path))
@click.option(
    "--module",
    "modules",
    multiple=True,
    required=True,
    help="Relative module path under the source (e.g., modules/networking).",
)
def infra_sync(source: pathlib.Path, destination: pathlib.Path, modules: tuple[str, ...]) -> None:
    """Copy Terraform/IaC modules from a filtered source export into labtools templates."""

    sync_modules(source_root=source, destination_root=destination, modules=modules)
    click.echo(f"Copied {len(modules)} module(s) from {source} to {destination}")


@main.group()
def shell() -> None:
    """Shell helper utilities."""


@shell.command("sync")
@click.argument("source", type=click.Path(file_okay=False, exists=True, path_type=pathlib.Path))
@click.argument("destination", type=click.Path(file_okay=False, path_type=pathlib.Path))
@click.option(
    "--helper",
    "helpers",
    multiple=True,
    required=True,
    help="Relative helper file under the source (e.g., lib/logging.sh).",
)
def shell_sync(source: pathlib.Path, destination: pathlib.Path, helpers: tuple[str, ...]) -> None:
    """Copy shell helper scripts from a filtered source export."""

    sync_helpers(source_root=source, destination_root=destination, helpers=helpers)
    click.echo(f"Copied {len(helpers)} helper file(s) from {source} to {destination}")


@main.group()
def docs() -> None:
    """Documentation template utilities."""


@docs.command("sync")
@click.argument("source", type=click.Path(file_okay=False, exists=True, path_type=pathlib.Path))
@click.argument("destination", type=click.Path(file_okay=False, path_type=pathlib.Path))
@click.option(
    "--document",
    "documents",
    multiple=True,
    required=True,
    help="Relative document path under the source (e.g., doc/templates/status-report.md).",
)
def docs_sync(source: pathlib.Path, destination: pathlib.Path, documents: tuple[str, ...]) -> None:
    """Copy documentation templates from a filtered source export."""

    sync_docs(source_root=source, destination_root=destination, documents=documents)
    click.echo(f"Copied {len(documents)} document template(s) from {source} to {destination}")


@main.group()
def core() -> None:
    """Core Python module utilities."""


@core.command("sync")
@click.argument("source", type=click.Path(file_okay=False, exists=True, path_type=pathlib.Path))
@click.argument("destination", type=click.Path(file_okay=False, path_type=pathlib.Path))
@click.option(
    "--module",
    "modules",
    multiple=True,
    required=True,
    help="Module/package under src/core to copy (e.g., utils).",
)
def core_sync(source: pathlib.Path, destination: pathlib.Path, modules: tuple[str, ...]) -> None:
    """Copy core Python modules from a filtered source export."""

    sync_core(source_root=source, destination_root=destination, modules=modules)
    click.echo(f"Copied {len(modules)} core module(s) from {source} to {destination}")


@main.group()
def data() -> None:
    """Data utility synchronization."""


@data.command("sync")
@click.argument("source", type=click.Path(file_okay=False, exists=True, path_type=pathlib.Path))
@click.argument("destination", type=click.Path(file_okay=False, path_type=pathlib.Path))
@click.option(
    "--module",
    "modules",
    multiple=True,
    required=True,
    help="Module under src/data to copy (e.g., loaders).",
)
def data_sync(source: pathlib.Path, destination: pathlib.Path, modules: tuple[str, ...]) -> None:
    """Copy data loaders, cleaners, and related utilities."""

    sync_data_modules(source_root=source, destination_root=destination, modules=modules)
    click.echo(f"Copied {len(modules)} data module(s) from {source} to {destination}")


@main.group()
def reports() -> None:
    """Reporting utility synchronization."""


@reports.command("sync")
@click.argument("source", type=click.Path(file_okay=False, exists=True, path_type=pathlib.Path))
@click.argument("destination", type=click.Path(file_okay=False, path_type=pathlib.Path))
@click.option(
    "--module",
    "modules",
    multiple=True,
    required=True,
    help="Module under src/reports to copy (e.g., generator).",
)
def reports_sync(source: pathlib.Path, destination: pathlib.Path, modules: tuple[str, ...]) -> None:
    """Copy report generator components."""

    sync_reports(source_root=source, destination_root=destination, modules=modules)
    click.echo(f"Copied {len(modules)} report module(s) from {source} to {destination}")


@main.group()
def mcp() -> None:
    """MCP tool synchronization."""


@mcp.command("sync")
@click.argument("source", type=click.Path(file_okay=False, exists=True, path_type=pathlib.Path))
@click.argument("destination", type=click.Path(file_okay=False, path_type=pathlib.Path))
@click.option(
    "--module",
    "modules",
    multiple=True,
    required=True,
    help="Module under src/mcp to copy (e.g., orchestrator).",
)
def mcp_sync(source: pathlib.Path, destination: pathlib.Path, modules: tuple[str, ...]) -> None:
    """Copy MCP tools from a filtered source export."""

    sync_mcp_tools(source_root=source, destination_root=destination, modules=modules)
    click.echo(f"Copied {len(modules)} MCP module(s) from {source} to {destination}")


@main.group()
def runtime() -> None:
    """Runtime orchestration synchronization."""


@runtime.command("sync")
@click.argument("source", type=click.Path(file_okay=False, exists=True, path_type=pathlib.Path))
@click.argument("destination", type=click.Path(file_okay=False, path_type=pathlib.Path))
@click.option(
    "--module",
    "modules",
    multiple=True,
    required=True,
    help="Module under src/runtime to copy (e.g., jobs.py).",
)
def runtime_sync(source: pathlib.Path, destination: pathlib.Path, modules: tuple[str, ...]) -> None:
    """Copy runtime orchestration primitives from a filtered source export."""

    sync_runtime_modules(source_root=source, destination_root=destination, modules=modules)
    click.echo(f"Copied {len(modules)} runtime module(s) from {source} to {destination}")


@main.group()
def requirements() -> None:
    """Requirements file synchronization."""


@requirements.command("sync")
@click.argument("source", type=click.Path(file_okay=False, exists=True, path_type=pathlib.Path))
@click.argument("destination", type=click.Path(file_okay=False, path_type=pathlib.Path))
@click.option(
    "--file",
    "files",
    multiple=True,
    required=True,
    help="Requirements file name to copy (e.g., requirements.txt).",
)
def requirements_sync(source: pathlib.Path, destination: pathlib.Path, files: tuple[str, ...]) -> None:
    """Copy requirements files from a filtered source export."""

    sync_requirements(source_root=source, destination_root=destination, files=files)
    click.echo(f"Copied {len(files)} requirements file(s) from {source} to {destination}")

