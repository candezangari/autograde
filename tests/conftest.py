"""
conftest.py – Shared pytest fixtures for autograde tests.
"""

import subprocess
import tempfile
import os
import pytest


@pytest.fixture()
def tmp_dir(tmp_path):
    """Return a temporary directory path (non-git)."""
    return str(tmp_path)


@pytest.fixture()
def git_repo(tmp_path):
    """
    Create a minimal git repository with:
      - a 'main' branch
      - file1.txt committed on main
    Returns the repo path as a string.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    path = str(repo)

    def git(*args):
        subprocess.run(["git", *args], cwd=path, check=True,
                       capture_output=True)

    git("init", "-b", "main")
    git("config", "user.email", "test@example.com")
    git("config", "user.name", "Test User")

    (repo / "file1.txt").write_text("hello\n")
    git("add", "file1.txt")
    git("commit", "-m", "Initial commit")

    return path


@pytest.fixture()
def git_repo_no_file1(tmp_path):
    """
    A git repo with 'main' but WITHOUT file1.txt.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    path = str(repo)

    def git(*args):
        subprocess.run(["git", *args], cwd=path, check=True,
                       capture_output=True)

    git("init", "-b", "main")
    git("config", "user.email", "test@example.com")
    git("config", "user.name", "Test User")

    (repo / "readme.md").write_text("no file1 here\n")
    git("add", "readme.md")
    git("commit", "-m", "Initial commit without file1.txt")

    return path


@pytest.fixture()
def git_repo_with_remote(tmp_path):
    """
    Two repos: a 'remote' bare repo with a 'feature' branch,
    and a local clone of it that has 'main' and file1.txt.
    Returns the local clone path.
    """
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
    git("config", "user.email", "test@example.com")
    git("config", "user.name", "Test User")

    (local / "file1.txt").write_text("hello\n")
    git("add", "file1.txt")
    git("commit", "-m", "Initial commit")
    git("push", "origin", "main")

    # create feature branch on remote
    git("checkout", "-b", "feature")
    (local / "feature.txt").write_text("feature work\n")
    git("add", "feature.txt")
    git("commit", "-m", "Feature work")
    git("push", "origin", "feature")
    git("checkout", "main")

    return path
