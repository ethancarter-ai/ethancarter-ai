# diffcov docs

## Concepts

- **Diff coverage**: percentage of changed files and changed lines that are touched by tests.
- **Base ref**: the older git ref to diff against, usually `main`.

## Troubleshooting

- If `report` shows no diff, ensure you have uncommitted changes or are comparing against a valid ref.
- If `--run-coverage` shows 0%, ensure the measured package is importable from `--source` and that tests actually execute it.
