import pytest

from labtools.core_modules.validation_runner import ValidationRunner


@pytest.mark.unit
def test_validation_runner_handles_missing_directory(tmp_path):
    runner = ValidationRunner(validation_dir=tmp_path / "missing")
    scripts = runner.discover_validation_scripts()
    assert scripts == []


@pytest.mark.integration
def test_validation_runner_executes_script(tmp_path):
    validation_dir = tmp_path / "validation"
    validation_dir.mkdir()
    script_path = validation_dir / "simple_validation.py"
    script_path.write_text(
        "if __name__ == '__main__':\n"
        "    print('validation ok')\n",
        encoding="utf-8",
    )

    runner = ValidationRunner(validation_dir=validation_dir, env="dev")
    results = runner.run_all_validations()
    assert "simple_validation" in results
    assert results["simple_validation"]["exit_code"] == 0
    assert results["_summary"]["success_count"] == 1

