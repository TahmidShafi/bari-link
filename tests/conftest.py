"""Pytest configuration and tracked mutation session guard."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest


def _sha256_file(path: str | Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def _is_git_repo(root: Path) -> bool:
    """Check if directory is inside a git repository."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=root,
            capture_output=True,
            text=True,
        )
        return res.returncode == 0 and res.stdout.strip() == "true"
    except Exception:
        return False


def pytest_sessionstart(session: pytest.Session) -> None:
    """Snapshot git tracked modifications and file hashes at session start."""
    repo_root = Path(session.config.rootpath)
    if not _is_git_repo(repo_root):
        session.config._git_guard_skip = True
        print("\n[git-guard] No .git repository detected; skipping mutation guard.")
        return

    session.config._git_guard_skip = False
    try:
        # 1. Snapshot all currently modified tracked files
        mod_out = subprocess.check_output(
            ["git", "ls-files", "-m"],
            cwd=repo_root,
            text=True,
        )
        initial_modified = set(line.strip() for line in mod_out.splitlines() if line.strip())

        # 2. Snapshot hashes of all tracked files in results/, configs/, and src/
        tracked_out = subprocess.check_output(
            ["git", "ls-files", "results/", "configs/", "src/"],
            cwd=repo_root,
            text=True,
        )
        tracked_files = [line.strip() for line in tracked_out.splitlines() if line.strip()]

        initial_hashes: dict[str, str] = {}
        for rel_p in tracked_files:
            full_p = repo_root / rel_p
            if full_p.is_file():
                initial_hashes[rel_p] = _sha256_file(full_p)

        session.config._git_guard_state = {
            "initial_modified": initial_modified,
            "initial_hashes": initial_hashes,
            "repo_root": repo_root,
        }
    except Exception as e:
        session.config._git_guard_skip = True
        print(f"\n[git-guard] Error initializing git guard ({e}); skipping.")


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Verify that no tracked file was modified during the test session."""
    if getattr(session.config, "_git_guard_skip", True):
        return

    state = getattr(session.config, "_git_guard_state", None)
    if not state:
        return

    repo_root = state["repo_root"]
    initial_modified = state["initial_modified"]
    initial_hashes = state["initial_hashes"]

    violations: list[str] = []

    try:
        # Check newly modified tracked files across entire repo
        curr_mod_out = subprocess.check_output(
            ["git", "ls-files", "-m"],
            cwd=repo_root,
            text=True,
        )
        current_modified = set(
            line.strip() for line in curr_mod_out.splitlines() if line.strip()
        )
        newly_modified = current_modified - initial_modified
        for f in sorted(newly_modified):
            violations.append(f"Newly modified tracked file: {f}")

        # Check hash alterations in results/, configs/, src/
        for rel_p, orig_hash in initial_hashes.items():
            full_p = repo_root / rel_p
            if not full_p.exists():
                violations.append(f"Tracked file was deleted during tests: {rel_p}")
            else:
                curr_hash = _sha256_file(full_p)
                if curr_hash != orig_hash and rel_p not in newly_modified:
                    violations.append(f"Tracked file content altered during tests: {rel_p}")

    except Exception as e:
        print(f"\n[git-guard] Warning: failed during session finish check: {e}")
        return

    if violations:
        msg = (
            "\n" + "=" * 70 + "\n"
            "GIT MUTATION GUARD FAILURE:\n"
            "The test session modified tracked repository files:\n"
            + "\n".join(f"  - {v}" for v in violations)
            + "\n\nAll test outputs must be written under tmp_path. "
            "Tests must never modify tracked files."
            + "\n" + "=" * 70
        )
        pytest.exit(msg, returncode=1)
