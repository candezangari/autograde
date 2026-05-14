"""
checks.py – Individual repository checks for autograde.

Each check function has the signature:
    check_<name>(repo_path: str) -> CheckResult

CheckResult is a NamedTuple with fields:
    name    (str)   – human-readable check identifier
    passed  (bool)  – whether the check passed
    message (str)   – short description of the result
"""

import subprocess
from typing import NamedTuple


class CheckResult(NamedTuple):
    name: str
    passed: bool
    message: str


def _run(cmd: list[str], cwd: str) -> subprocess.CompletedProcess:
    """Run a git command, capturing output, never raising on non-zero exit."""
    try:
        return subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        # cwd does not exist
        return subprocess.CompletedProcess(cmd, returncode=128, stdout="", stderr="")


# ---------------------------------------------------------------------------
# Check implementations
# ---------------------------------------------------------------------------

def check_is_git_repo(repo_path: str) -> CheckResult:
    """Check that repo_path is a valid Git repository."""
    result = _run(["git", "rev-parse", "--git-dir"], cwd=repo_path)
    if result.returncode == 0:
        return CheckResult(
            name="is_git_repo",
            passed=True,
            message="Directory is a valid Git repository.",
        )
    return CheckResult(
        name="is_git_repo",
        passed=False,
        message="Not a Git repository (or path does not exist).",
    )


def check_main_branch_exists(repo_path: str) -> CheckResult:
    """Check that the 'main' branch exists locally."""
    result = _run(["git", "branch", "--list", "main"], cwd=repo_path)
    if result.returncode == 0 and result.stdout.strip():
        return CheckResult(
            name="main_branch_exists",
            passed=True,
            message="Branch 'main' exists locally.",
        )
    return CheckResult(
        name="main_branch_exists",
        passed=False,
        message="Branch 'main' does not exist locally.",
    )


def check_feature_branch_on_remote(repo_path: str) -> CheckResult:
    """Check that the 'feature' branch exists on the 'origin' remote."""
    result = _run(
        ["git", "ls-remote", "--heads", "origin", "feature"],
        cwd=repo_path,
    )
    if result.returncode != 0:
        return CheckResult(
            name="feature_branch_on_remote",
            passed=False,
            message=(
                "Could not contact remote 'origin' or no remote configured. "
                f"({result.stderr.strip()})"
            ),
        )
    if result.stdout.strip():
        return CheckResult(
            name="feature_branch_on_remote",
            passed=True,
            message="Branch 'feature' exists on remote 'origin'.",
        )
    return CheckResult(
        name="feature_branch_on_remote",
        passed=False,
        message="Branch 'feature' not found on remote 'origin'.",
    )


def check_file1_exists_on_main(repo_path: str) -> CheckResult:
    """Check that file1.txt is tracked on the 'main' branch."""
    result = _run(["git", "show", "main:file1.txt"], cwd=repo_path)
    if result.returncode == 0:
        return CheckResult(
            name="file1_exists_on_main",
            passed=True,
            message="'file1.txt' exists on branch 'main'.",
        )
    return CheckResult(
        name="file1_exists_on_main",
        passed=False,
        message="'file1.txt' not found on branch 'main'.",
    )


# ---------------------------------------------------------------------------
# Registry – order matters for display
# ---------------------------------------------------------------------------

CHECKS = [
    check_is_git_repo,
    check_main_branch_exists,
    check_feature_branch_on_remote,
    check_file1_exists_on_main,
]
