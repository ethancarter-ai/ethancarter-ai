from pathlib import Path
from typing import Optional

import typer
from git import Repo
from rich.console import Console
from rich.table import Table

from diffcov.coverage_report import FileCoverage, summarize_results

app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()


@app.command()
def report(
    base: str = typer.Option("main", help="Base ref for diff, e.g. main or HEAD~1"),
    source: Optional[str] = typer.Option(None, help="Module/package to run under coverage"),
    run_coverage: bool = typer.Option(False, help="Attempt to run coverage for source module"),
) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    repo = Repo(repo_root)

    try:
        diff_text = repo.git.diff(base, repo.head.commit.hexsha)
    except Exception as exc:
        console.print(f"[red]Unable to compute diff from {base}: {exc}[/red]")
        raise typer.Exit(1)

    if not diff_text:
        console.print("[yellow]No diff detected[/yellow]")
        raise typer.Exit(0)

    entries = parse_diff(diff_text)

    coverage_data: dict[str, set[int]] = {}
    if run_coverage and source:
        coverage_data = _coverage_from_module(repo_root, Path(source))

    rows: list[FileCoverage] = []
    for entry in entries:
        if not entry.get("additions"):
            continue
        diff_total = len(entry["additions"])
        covered_in_diff = 0
        covered_lines: set[int] = set()
        covered = coverage_data.get(entry["path"], set())
        for (_p, _ln, ln_no) in entry["additions"]:
            if ln_no in covered:
                covered_in_diff += 1
                covered_lines.add(ln_no)
        rows.append(
            FileCoverage(
                file=entry["path"],
                diff_lines=[],
                covered_lines=covered_lines,
                covered_in_diff=covered_in_diff,
                diff_total=diff_total,
            )
        )

    summary = summarize_results(rows)
    _print_report(rows, summary)


def parse_diff(diff_text: str) -> list[dict]:
    entries: list[dict] = []
    current: dict | None = None

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            if current and current.get("path"):
                entries.append(current)
            current = None
            continue
        if line.startswith("+++ b/"):
            current = {"path": line[6:].split("\t", 1)[0], "additions": []}
            continue
        if line.startswith("@@") and current:
            current["_pending_hunk"] = True
            continue
        if line.startswith("+") and current and not line.startswith(("+++ ", "+++b/")):
            ln_no = _next_line_no(current)
            current.setdefault("additions", []).append((current["path"], line[1:], ln_no))
            continue

    if current and current.get("path"):
        entries.append(current)

    entries = [e for e in entries if e.get("path")]
    return entries


def _next_line_no(entry: dict) -> int:
    additions = entry.get("additions", [])
    if not additions:
        return 1
    _p, _ln, previous_no = additions[-1]
    return int(previous_no) + 1


def _coverage_from_module(repo_root: Path, module_root: Path) -> dict[str, set[int]]:
    coverage_data: dict[str, set[int]] = {}
    candidates = list(module_root.rglob(".coverage")) if module_root.exists() else []
    if not candidates:
        return coverage_data

    try:
        import coverage as cov_module

        for candidate in candidates:
            try:
                cov_obj = cov_module.Coverage(data_file=str(candidate))
                cov_obj.load()
            except Exception:
                continue
            for filename in getattr(cov_obj, "data", {}).measured_files() or []:
                coverage = cov_obj.analysis2(filename) or ([], [], [])
                _summary, executable, _missing = coverage
                covered = {int(ln) for ln in executable if str(ln).isdigit()}
                coverage_data[filename] = coverage_data.get(filename, set()) | covered
    except Exception:
        pass

    return coverage_data


def _print_report(rows: list[FileCoverage], summary: dict) -> None:
    if not rows:
        console.print("[yellow]No added lines to report[/yellow]")
        return

    table = Table(title="diffcov")
    table.add_column("file", style="cyan", no_wrap=False)
    table.add_column("diff lines", justify="right")
    table.add_column("covered", justify="right")
    table.add_column("%", justify="right")

    for row in rows:
        pct = f"{row.percent:.0f}%"
        color = "green" if row.percent >= 80 else "yellow" if row.percent >= 40 else "red"
        table.add_row(row.file, str(row.diff_total), str(row.covered_in_diff), f"[{color}]{pct}[/{color}]")

    console.print(table)
    summary_text = (
        f"Files changed {summary['files_changed']}, "
        f"diff lines {summary['diff_lines_total']}, "
        f"covered {summary['covered_in_diff']}, "
        f"overall {summary['diff_coverage_pct']:.1f}%"
    )
    console.print(f"[bold]{summary_text}[/bold]")


if __name__ == "__main__":
    app()
