from pathlib import Path
from datetime import datetime

import pytest

from labtools.core_modules.build_reporter import BuildReporter

pytestmark = pytest.mark.unit


def test_build_reporter_initialization(tmp_path):
    reporter = BuildReporter(run_id="test-run", env="dev", datamart_path=":memory:", log_dir=tmp_path)
    # Simulate report generation with minimal inputs
    start = datetime.utcnow()
    end = datetime.utcnow()
    markdown_path, json_path = reporter.generate_comprehensive_report(
        config={"environments": {"dev": {"steps": {}}}},
        step_results=[],
        validation_results={},
        start_time=start,
        end_time=end,
    )
    assert Path(markdown_path).exists()
    assert Path(json_path).exists()

