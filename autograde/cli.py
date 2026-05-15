"""
cli.py – Command-line interface for autograde.

Usage:
    autograde <repo_path>
"""

import os
import subprocess
import sys
import tempfile
from urllib.parse import urlparse

from autograde.checks import CHECKS, CheckResult


def _format(result: CheckResult) -> str:
    tag = "[PASS]" if result.passed else "[FAIL]"
    return f"{tag} {result.name}: {result.message}"


def _looks_like_remote_url(path: str) -> bool:
    if path.startswith("git@"):
        return True

    parsed = urlparse(path)
    if parsed.scheme in {"http", "https", "ssh", "git"}:
        return bool(parsed.netloc)
    if parsed.scheme == "file":
        return bool(parsed.path)

    if ":" in path and "@" in path.split(":", 1)[0]:
        return True

    return False


def _ensure_local_main_branch(repo_path: str) -> None:
    result = subprocess.run(
        ["git", "branch", "--list", "main"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0 and result.stdout.strip():
        return

    result = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/main"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        subprocess.run(
            ["git", "branch", "main", "origin/main"],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )


def _prepare_repo_path(repo_path: str) -> tuple[str, tempfile.TemporaryDirectory | None]:
    if os.path.exists(repo_path):
        return repo_path, None

    if not _looks_like_remote_url(repo_path):
        return repo_path, None

    temp_dir = tempfile.TemporaryDirectory()
    clone_path = temp_dir.name
    result = subprocess.run(
        ["git", "clone", repo_path, clone_path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        temp_dir.cleanup()
        raise RuntimeError(
            f"Could not clone remote repository '{repo_path}': "
            f"{result.stderr.strip() or result.stdout.strip()}"
        )

    _ensure_local_main_branch(clone_path)
    return clone_path, temp_dir


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: autograde <repo_path>")
        sys.exit(2)

    repo_path = sys.argv[1]
    temp_dir = None

    try:
        repo_path, temp_dir = _prepare_repo_path(repo_path)
    except RuntimeError as exc:
        print(_format(CheckResult(name="is_git_repo", passed=False, message=str(exc))))
        print("\n0/4 checks passed.")
        sys.exit(1)

    try:
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
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()


if __name__ == "__main__":
    main()
