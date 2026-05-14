"""
test_cli.py – Integration tests for the autograde CLI.
"""

import subprocess
import sys


def run_autograde(args: list[str], cwd=None):
    return subprocess.run(
        [sys.executable, "-m", "autograde.cli", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )


class TestCLI:
    def test_exits_2_with_no_args(self):
        result = run_autograde([])
        assert result.returncode == 2
        assert "Usage" in result.stdout

    def test_all_pass_prints_summary(self, git_repo_with_remote):
        result = run_autograde([git_repo_with_remote])
        assert "checks passed" in result.stdout

    def test_output_contains_pass_fail_tags(self, git_repo_with_remote):
        result = run_autograde([git_repo_with_remote])
        lines = result.stdout.strip().splitlines()
        check_lines = [l for l in lines if l.startswith("[")]
        assert all(l.startswith("[PASS]") or l.startswith("[FAIL]")
                   for l in check_lines)

    def test_exits_1_when_checks_fail(self, tmp_dir):
        result = run_autograde([tmp_dir])
        assert result.returncode == 1

    def test_exits_0_when_all_checks_pass(self, git_repo_with_remote):
        result = run_autograde([git_repo_with_remote])
        assert result.returncode == 0
