"""
test_cli.py – Integration tests for the autograde CLI.
"""

import subprocess
import sys
from pathlib import Path


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

    def test_accepts_git_remote_url(self, tmp_path):
        bare = tmp_path / "remote.git"
        bare.mkdir()
        subprocess.run(["git", "init", "--bare", "-b", "main", str(bare)],
                       check=True, capture_output=True)

        local = tmp_path / "local"
        local.mkdir()
        subprocess.run(["git", "clone", str(bare), str(local)],
                       check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"],
                       cwd=str(local), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"],
                       cwd=str(local), check=True, capture_output=True)

        (local / "file1.txt").write_text("hello\n")
        subprocess.run(["git", "add", "file1.txt"], cwd=str(local),
                       check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"],
                       cwd=str(local), check=True, capture_output=True)
        subprocess.run(["git", "push", "origin", "main"],
                       cwd=str(local), check=True, capture_output=True)

        subprocess.run(["git", "checkout", "-b", "feature"],
                       cwd=str(local), check=True, capture_output=True)
        (local / "feature.txt").write_text("feature work\n")
        subprocess.run(["git", "add", "feature.txt"], cwd=str(local),
                       check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Feature work"],
                       cwd=str(local), check=True, capture_output=True)
        subprocess.run(["git", "push", "origin", "feature"],
                       cwd=str(local), check=True, capture_output=True)

        remote_url = Path(bare).as_uri()
        result = run_autograde([remote_url])

        assert result.returncode == 0
        assert "checks passed" in result.stdout
