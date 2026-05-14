# Specs: `autograde` checks

## `is_git_repo`

Verify if the url belongs to a valid github url.

It takes a single `repo_path: str` and runs `git rev-parse --git-dir` inside it. If git exits 0, it passes. If the path doesn't exist, isn't a directory, or isn't a repo, if git doesn't recognize it, that's a FAIL. It should never raise an unhandled exception regardless of what's at that path.

- [PASS] is_git_repo: Directory is a valid Git repository.
- [FAIL] is_git_repo: Not a Git repository (or path does not exist).

---

## `main_branch_exists`

Checks that a branch named `main` exists locally. Not that we're currently on it — just that it exists.

Runs `git branch --list main` inside the repo. If there's any output, the branch is there and it passes. If the repo uses `master`, `trunk`, or anything else, that's a FAIL — we specifically need `main`. Should fail cleanly if the repo is broken, no uncaught exceptions.

- [PASS] main_branch_exists: Branch 'main' exists locally.
- [FAIL] main_branch_exists: Branch 'main' does not exist locally.


---

## `feature_branch_on_remote`

This one looks at the remote, not the local branches. We want to know if `feature` was pushed to `origin`.

Runs `git ls-remote --heads origin feature`. If there's output, the branch is on the remote and it passes. Two failure cases: the branch isn't there, or the remote can't be contacted (no remote configured, unreachable, etc.). Both are a FAIL, but the second one should include a message explaining what went wrong — don't just say "not found" when the real issue is there's no remote at all.

```
[PASS] feature_branch_on_remote: Branch 'feature' exists on remote 'origin'.
[FAIL] feature_branch_on_remote: Branch 'feature' not found on remote 'origin'.
```

---

## `file1_exists_on_main`

Checks that `file1.txt` is committed on `main`. We don't care about the working tree — this reads straight from git history.

Runs `git show main:file1.txt`. If it exits 0, the file is in the tree of `main` and it passes. Fails if the file isn't committed there, or if `main` doesn't exist. Important: don't use `os.path.exists` or anything that touches the filesystem directly — it needs to work even if the file has been deleted locally.

- [PASS] file1_exists_on_main: 'file1.txt' exists on branch 'main'.
- [FAIL] file1_exists_on_main: 'file1.txt' not found on branch 'main'.

---

## CLI behavior

The tool takes a single positional argument (the repo path), prints each check result on its own line with a `[PASS]` or `[FAIL]` prefix, and ends with a summary line like `X/Y checks passed.` 