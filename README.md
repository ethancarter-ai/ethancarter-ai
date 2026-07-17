# diffcov

Show whether the lines in your **current diff** are covered by tests, without converting the whole report by untouched files.

## About

`diffcov` ships a small CLI that can render coverage for the exact changed lines between two git refs. By combining a parsed patch with Python's `coverage` data, it isolates the signal that matters during code review and local development.

## Features

- Base-diff aware reporting, scoped to added lines
- Per-file and overall diff coverage percentage
- Runs in the README's installed environment via `pyproject.toml`
- Built with typed data structures and Rich output

## Installation

### From source

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

### Via pip (after publish)

```bash
pip install diffcov
```

## Usage

```bash
# Report diff coverage between main and current working tree
diffcov report --base main

# Experimentally run coverage for an app package, then report
diffcov report --base main --source app --run-coverage
```

## Project structure

```
diffcov/
  src/diffcov/
    __init__.py
    cli.py
    coverage_report.py
    diff.py
  tests/
  pyproject.toml
```

## Tags / keywords

python, coverage, git-diff, developer-tools, cli, testing
