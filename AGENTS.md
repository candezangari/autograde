# AGENTS.md

## Environment & Tooling
- Use **`uv`** for all dependency management. Never use `pip` directly.
  - Add dependencies: `uv add <package>`
  - Run scripts: `uv run python ...`
  - Run tests: `uv run pytest`
  - Use **`pytest`** for all testing. Test files live in `tests/`.

## Project Overview
`autograde` is a CLI tool that inspects a target Git repository and checks whether
a set of required conditions hold. It exits with code 0 if all checks pass,
and a non-zero code if any check fails.

## Code Conventions
- Entry point: `autograde/cli.py` (function `main()`), registered as the `autograde` console script.
- Each check is a standalone function in `autograde/checks.py` with signature:
  `def check_<name>(repo_path: str) -> CheckResult`.
- `CheckResult` is a named tuple: `(name: str, passed: bool, message: str)`.
- New checks must be registered in the `CHECKS` list inside `autograde/checks.py`.

## Workflow Rules

1. **Spec first**: before implementing any new check, add a spec entry in `specs.md`.
2. **Tests before code**: write a failing test in `tests/` before implementing the check.
3. **One check per commit**: keep commits atomic and descriptive.
4. **Never break existing tests**: run `uv run pytest` before committing.

## Running the Tool

```bash
uv run autograde /path/to/target-repo
```

## Running the Test Suite

```bash
uv run pytest
# or with verbose output:
uv run pytest -v
```

## Adding a New Check

1. Write the spec in `checks.md` (add a new section).
2. Write a test in `tests/test_checks.py`.
3. Implement the function in `autograde/checks.py`.
4. Register it in the `CHECKS` list.
5. Run `uv run pytest` to confirm everything is green.
