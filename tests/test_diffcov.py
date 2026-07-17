import pytest
from diffcov.coverage_report import FileCoverage, summarize_results


def test_empty_rows_returns_zero_summary():
    assert summarize_results([]) == {
        "files_changed": 0,
        "diff_lines_total": 0,
        "covered_in_diff": 0,
        "diff_coverage_pct": 0.0,
    }


def test_single_file_fully_covered():
    rows = [FileCoverage(file="a.py", diff_lines=["x", "y"], covered_lines={1, 2}, covered_in_diff=2, diff_total=2)]
    result = summarize_results(rows)
    assert result["files_changed"] == 1
    assert result["diff_coverage_pct"] == pytest.approx(100.0)


def test_partial_coverage():
    rows = [FileCoverage(file="a.py", diff_lines=["x", "y", "z"], covered_lines={1, 3}, covered_in_diff=2, diff_total=3)]
    result = summarize_results(rows)
    assert pytest.approx(result["diff_coverage_pct"], abs=1e-6) == (2 / 3 * 100)
