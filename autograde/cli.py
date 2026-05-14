"""
cli.py – Command-line interface for autograde.

Usage:
    autograde <repo_path>
"""

import sys

from autograde.checks import CHECKS, CheckResult


def _format(result: CheckResult) -> str:
    tag = "[PASS]" if result.passed else "[FAIL]"
    return f"{tag} {result.name}: {result.message}"


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: autograde <repo_path>")
        sys.exit(2)

    repo_path = sys.argv[1]
    results: list[CheckResult] = []

    for check_fn in CHECKS:
        try:
            result = check_fn(repo_path)
        except Exception as exc:  # noqa: BLE001
            result = CheckResult(
                name=check_fn.__name__,
                passed=False,
                message=f"Unexpected error: {exc}",
            )
        results.append(result)
        print(_format(result))

    passed = sum(1 for r in results if r.passed)
    total = len(results)
    print(f"\n{passed}/{total} checks passed.")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
