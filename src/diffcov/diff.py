import re
from pathlib import Path
from typing import Iterable


RE_PLUS_FILE = re.compile(r"^\+\+\+\s+b/(?P<path>[^\t]+)")
RE_PLUS_LINE = re.compile(r"^\+(?!\+\+)(?P<line>.+)$")
RE_MINUS_LINE = re.compile(r"^-(?!-)(?P<line>.+)$")
RE_HUNK = re.compile(r"^@@ .+ \+(\d+),?(\d+)? .*$")


def parse_diff(diff_text: str) -> list[dict]:
    entries = []
    current: dict | None = None
    line_no = None

    def reset() -> None:
        nonlocal current, line_no
        current = None
        line_no = None

    def start_hunk(match: re.Match[str]) -> None:
        nonlocal line_no
        line_no = int(match.group(1)) - 1

    def add_line(line: str) -> None:
        nonlocal line_no
        if current is None or line_no is None:
            return
        base = Path(current["path"])
        current.setdefault("additions", [])
        current["additions"].append((base, line, line_no))
        line_no += 1

    lines = diff_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("diff --git "):
            reset()
            i += 1
            continue

        if line.startswith("+++ b/"):
            m = RE_PLUS_FILE.match(line)
            if m:
                current = {"path": m.group("path")}
            i += 1
            continue

        if line.startswith("@@"):
            start_hunk(RE_HUNK.match(line))
            i += 1
            continue

        if line.startswith("+") and not line.startswith("+++"):
            if current:
                add_line(line[1:])
            i += 1
            continue

        if line.startswith("-"):
            if current:
                current.setdefault("lint", []).append(line[1:])
            i += 1
            continue

        if current:
            current.setdefault("context", []).append(line)
            i += 1
            continue

        i += 1

    for entry in (x for x in (current,) if x):
        entries.append(entry)

    return entries


def changed_paths(repo_root: Path) -> Iterable[Path]:
    repo_root = Path(repo_root).resolve()
    for path in repo_root.rglob("*"):
        if path.is_file() and ".git" in path.parts:
            continue
        yield path
