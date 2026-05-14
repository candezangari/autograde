# autograde

A Python command-line tool that inspects a target Git repository and reports
whether a set of required conditions hold.

## Checks

| Check | Description |
|---|---|
| `is_git_repo` | The target path is a valid Git repository |
| `main_branch_exists` | A branch named `main` exists locally |
| `feature_branch_on_remote` | A branch named `feature` exists on remote `origin` |
| `file1_exists_on_main` | `file1.txt` is tracked on branch `main` |

## Requirements

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) for dependency management

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd autograde

# Install the package (creates a virtual environment automatically)
uv sync
```

## Running the Tool

```bash
uv run autograde /path/to/target-repo
```

**Example output:**

```
[PASS] is_git_repo: Directory is a valid Git repository.
[PASS] main_branch_exists: Branch 'main' exists locally.
[PASS] feature_branch_on_remote: Branch 'feature' exists on remote 'origin'.
[PASS] file1_exists_on_main: 'file1.txt' exists on branch 'main'.

4/4 checks passed.
```

Exit code is `0` when all checks pass, `1` if any fail, `2` if called with
wrong arguments.

## Running the Test Suite

```bash
uv run pytest
# verbose
uv run pytest -v
```

## Project Structure

```
autograde/
├── autograde/          # Source package
│   ├── __init__.py
│   ├── checks.py       # Individual check functions
│   └── cli.py          # CLI entry point
├── specs/
│   └── checks.md       # Behavioral specifications
├── tests/
│   ├── conftest.py     # Shared pytest fixtures
│   ├── test_checks.py  # Unit tests for check functions
│   └── test_cli.py     # Integration tests for the CLI
├── AGENTS.md           # Instructions for AI coding agents
├── README.md
└── pyproject.toml
```

## Adding New Checks

See [`AGENTS.md`](AGENTS.md) for the full workflow.
