from click.testing import CliRunner
import pytest

from labtools.cli import main

pytestmark = pytest.mark.unit


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Reusable tooling for building new lab environments." in result.output


def test_infra_help():
    runner = CliRunner()
    result = runner.invoke(main, ["infra", "--help"])
    assert result.exit_code == 0
    assert "Infrastructure module utilities." in result.output


def test_shell_help():
    runner = CliRunner()
    result = runner.invoke(main, ["shell", "--help"])
    assert result.exit_code == 0
    assert "Shell helper utilities." in result.output


def test_docs_help():
    runner = CliRunner()
    result = runner.invoke(main, ["docs", "--help"])
    assert result.exit_code == 0
    assert "Documentation template utilities." in result.output


def test_core_help():
    runner = CliRunner()
    result = runner.invoke(main, ["core", "--help"])
    assert result.exit_code == 0
    assert "Core Python module utilities." in result.output


def test_data_help():
    runner = CliRunner()
    result = runner.invoke(main, ["data", "--help"])
    assert result.exit_code == 0
    assert "Data utility synchronization." in result.output


def test_reports_help():
    runner = CliRunner()
    result = runner.invoke(main, ["reports", "--help"])
    assert result.exit_code == 0
    assert "Reporting utility synchronization." in result.output


def test_mcp_help():
    runner = CliRunner()
    result = runner.invoke(main, ["mcp", "--help"])
    assert result.exit_code == 0
    assert "MCP tool synchronization." in result.output


def test_runtime_help():
    runner = CliRunner()
    result = runner.invoke(main, ["runtime", "--help"])
    assert result.exit_code == 0
    assert "Runtime orchestration synchronization." in result.output


def test_requirements_help():
    runner = CliRunner()
    result = runner.invoke(main, ["requirements", "--help"])
    assert result.exit_code == 0
    assert "Requirements file synchronization." in result.output


def test_cli_infra_sync_command(tmp_path):
    source = tmp_path / "source"
    dest = tmp_path / "dest"
    (source / "modules" / "networking").mkdir(parents=True)
    (source / "modules" / "networking" / "main.tf").write_text("# module", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "infra",
            "sync",
            str(source),
            str(dest),
            "--module",
            "modules/networking",
        ],
    )
    assert result.exit_code == 0, result.output
    copied_file = dest / "modules" / "networking" / "main.tf"
    assert copied_file.exists()


