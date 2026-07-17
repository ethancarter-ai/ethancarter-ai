from dataclasses import dataclass


@dataclass(frozen=True)
class FileCoverage:
    file: str
    diff_lines: list[str]
    covered_lines: set[int]
    covered_in_diff: int
    diff_total: int

    @property
    def percent(self) -> float:
        if self.diff_total <= 0:
            return 0.0
        return self.covered_in_diff / self.diff_total * 100.0


def summarize_results(rows: list[FileCoverage]) -> dict:
    if not rows:
        return {
            "files_changed": 0,
            "diff_lines_total": 0,
            "covered_in_diff": 0,
            "diff_coverage_pct": 0.0,
        }

    files_changed = len(rows)
    diff_lines_total = sum(r.diff_total for r in rows)
    covered_in_diff = sum(r.covered_in_diff for r in rows)
    diff_coverage_pct = (
        covered_in_diff / diff_lines_total * 100.0 if diff_lines_total else 0.0
    )

    return {
        "files_changed": files_changed,
        "diff_lines_total": diff_lines_total,
        "covered_in_diff": covered_in_diff,
        "diff_coverage_pct": diff_coverage_pct,
    }
