"""
test_checks.py – Automated tests for autograde check functions.

Each test follows the spec in specs/checks.md.
"""

import pytest

from autograde.checks import (
    CheckResult,
    check_feature_branch_on_remote,
    check_file1_exists_on_main,
    check_is_git_repo,
    check_main_branch_exists,
)


# ---------------------------------------------------------------------------
# check_is_git_repo
# ---------------------------------------------------------------------------

class TestIsGitRepo:
    def test_passes_for_valid_repo(self, git_repo):
        result = check_is_git_repo(git_repo)
        assert isinstance(result, CheckResult)
        assert result.name == "is_git_repo"
        assert result.passed is True
        assert "valid" in result.message.lower()

    def test_fails_for_plain_directory(self, tmp_dir):
        result = check_is_git_repo(tmp_dir)
        assert result.passed is False
        assert "not a git repository" in result.message.lower()

    def test_fails_for_nonexistent_path(self, tmp_path):
        result = check_is_git_repo(str(tmp_path / "does_not_exist"))
        assert result.passed is False


# ---------------------------------------------------------------------------
# check_main_branch_exists
# ---------------------------------------------------------------------------

class TestMainBranchExists:
    def test_passes_when_main_exists(self, git_repo):
        result = check_main_branch_exists(git_repo)
        assert result.name == "main_branch_exists"
        assert result.passed is True
        assert "main" in result.message

    def test_fails_when_main_absent(self, tmp_path):
        """Repo initialised with a different default branch name."""
        import subprocess
        repo = tmp_path / "repo"
        repo.mkdir()
        path = str(repo)

        def git(*args):
            subprocess.run(["git", *args], cwd=path, check=True,
                           capture_output=True)

        git("init", "-b", "trunk")
        git("config", "user.email", "t@t.com")
        git("config", "user.name", "T")
        (repo / "f.txt").write_text("x")
        git("add", "f.txt")
        git("commit", "-m", "init")

        result = check_main_branch_exists(path)
        assert result.passed is False
        assert "does not exist" in result.message.lower()


# ---------------------------------------------------------------------------
# check_feature_branch_on_remote
# ---------------------------------------------------------------------------

class TestFeatureBranchOnRemote:
    def test_passes_when_feature_exists_on_remote(self, git_repo_with_remote):
        result = check_feature_branch_on_remote(git_repo_with_remote)
        assert result.name == "feature_branch_on_remote"
        assert result.passed is True
        assert "feature" in result.message

    def test_fails_when_no_remote_configured(self, git_repo):
        """Local-only repo has no remote → should fail gracefully."""
        result = check_feature_branch_on_remote(git_repo)
        assert result.passed is False
        # message should explain the problem, not crash
        assert result.message  # non-empty

    def test_fails_when_feature_absent_from_remote(self, tmp_path):
        """Remote exists but has no 'feature' branch."""
        import subprocess

        bare = tmp_path / "remote.git"
        bare.mkdir()
        subprocess.run(["git", "init", "--bare", "-b", "main", str(bare)],
                       check=True, capture_output=True)

        local = tmp_path / "local"
        local.mkdir()
        path = str(local)

        def git(*args):
            subprocess.run(["git", *args], cwd=path, check=True,
                           capture_output=True)

        git("clone", str(bare), ".")
        git("config", "user.email", "t@t.com")
        git("config", "user.name", "T")
        (local / "f.txt").write_text("x")
        git("add", "f.txt")
        git("commit", "-m", "init")
        git("push", "origin", "main")

        result = check_feature_branch_on_remote(path)
        assert result.passed is False
        assert "not found" in result.message.lower()


# ---------------------------------------------------------------------------
# check_file1_exists_on_main
# ---------------------------------------------------------------------------

class TestFile1ExistsOnMain:
    def test_passes_when_file1_on_main(self, git_repo):
        result = check_file1_exists_on_main(git_repo)
        assert result.name == "file1_exists_on_main"
        assert result.passed is True
        assert "file1.txt" in result.message

    def test_fails_when_file1_absent(self, git_repo_no_file1):
        result = check_file1_exists_on_main(git_repo_no_file1)
        assert result.passed is False
        assert "not found" in result.message.lower()

    def test_reads_from_git_history_not_working_tree(self, git_repo):
        """Even if we delete file1.txt from the working tree, check still passes
        because it reads from git history."""
        import os
        os.remove(f"{git_repo}/file1.txt")
        result = check_file1_exists_on_main(git_repo)
        assert result.passed is True


# ---------------------------------------------------------------------------
# CheckResult structure
# ---------------------------------------------------------------------------

class TestCheckResult:
    def test_is_named_tuple(self, git_repo):
        result = check_is_git_repo(git_repo)
        assert hasattr(result, "name")
        assert hasattr(result, "passed")
        assert hasattr(result, "message")
        assert isinstance(result.passed, bool)
        assert isinstance(result.name, str)
        assert isinstance(result.message, str)
