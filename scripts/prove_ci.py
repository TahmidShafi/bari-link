"""Proof of CI safety in a clean clone from committed HEAD.

Intended workflow:
1. Make local changes.
2. Commit locally: git commit -m "..."
3. Run this proof: python scripts/prove_ci.py
4. Push to remote: git push

For pre-commit testing of candidate working tree changes:
python scripts/prove_ci.py --worktree
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile


def main() -> None:
    parser = argparse.ArgumentParser(description="Proof of CI safety in a clean clone.")
    parser.add_argument(
        "--worktree",
        action="store_true",
        help="Include candidate working tree changes for pre-commit verification.",
    )
    args = parser.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # 1. Inspect uncommitted changes
    status_out = subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        text=True,
    ).strip()

    if status_out and not args.worktree:
        print("\n" + "!" * 72)
        print("WARNING: Working tree has uncommitted changes.")
        print("These uncommitted changes are NOT included in this proof.")
        print("This script tests committed HEAD only.")
        print("Intended workflow: commit locally -> run prove_ci.py -> push.")
        print("(Use --worktree to test candidate working tree changes before committing)")
        print("!" * 72 + "\n")

    head_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        text=True,
    ).strip()

    tmp_dir = tempfile.mkdtemp(prefix="barilink_prove_ci_")
    try:
        print(f"Clone Path: {tmp_dir}")
        print(f"HEAD SHA:   {head_sha}")

        # 2. Clone committed HEAD
        subprocess.check_call(
            ["git", "clone", repo_root, tmp_dir],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if args.worktree:
            print("  Applying candidate working tree changes to clone for verification...")
            for root, dirs, files in os.walk(repo_root):
                norm_root = root.replace("\\", "/")
                if any(
                    skip in norm_root
                    for skip in [
                        ".venv",
                        ".git",
                        "__pycache__",
                        "web/public/data",
                        "data/generated",
                        "results/ci",
                        "results/demo",
                        "results/holdout_",
                        "results/stress_",
                    ]
                ):
                    continue
                rel = os.path.relpath(root, repo_root)
                dst_dir = os.path.join(tmp_dir, rel)
                os.makedirs(dst_dir, exist_ok=True)
                for f in files:
                    src_f = os.path.join(root, f)
                    dst_f = os.path.join(dst_dir, f)
                    shutil.copy2(src_f, dst_f)
            # Commit the candidate changes in the clone's temporary repo
            subprocess.check_call(["git", "add", "-A"], cwd=tmp_dir, stdout=subprocess.DEVNULL)
            subprocess.check_call(
                ["git", "commit", "-m", "candidate changes for pre-commit verification"],
                cwd=tmp_dir,
                stdout=subprocess.DEVNULL,
            )

        # 3. Assert untracked data directories are absent
        assert not os.path.exists(
            os.path.join(tmp_dir, "data", "generated")
        ), "Assertion failed: data/generated/ exists in clean clone!"
        assert not os.path.exists(
            os.path.join(tmp_dir, "results", "holdout_5", "splink_k_resolved", "metrics.json")
        ) and not os.path.exists(
            os.path.join(tmp_dir, "results", "holdout_5", "household")
        ), "Assertion failed: results/holdout_5/ experiment data exists in clean clone!"
        print("  ✓ Asserted absence of data/generated/ and results/holdout_5/ experiment data")

        # 4. Create fresh virtual environment inside the clone
        venv_dir = os.path.join(tmp_dir, ".fresh_venv")
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
        if sys.platform == "win32":
            python_bin = os.path.join(venv_dir, "Scripts", "python.exe")
            pytest_bin = os.path.join(venv_dir, "Scripts", "pytest.exe")
            ruff_bin = os.path.join(venv_dir, "Scripts", "ruff.exe")
        else:
            python_bin = os.path.join(venv_dir, "bin", "python")
            pytest_bin = os.path.join(venv_dir, "bin", "pytest")
            ruff_bin = os.path.join(venv_dir, "bin", "ruff")

        # 5. Install package in editable mode with dev dependencies
        print("  Installing dependencies in fresh venv...")
        subprocess.check_call(
            [python_bin, "-m", "pip", "install", "--quiet", "-e", tmp_dir + "[dev]"]
        )

        # 6. Run ruff check .
        print("  Running: ruff check .")
        subprocess.check_call([ruff_bin, "check", "."], cwd=tmp_dir)

        # 7. Run pytest -q -m "not publish and not artifacts"
        print("  Running: pytest -q -m 'not publish and not artifacts'")
        p_res = subprocess.run(
            [pytest_bin, "-q", "-m", "not publish and not artifacts"],
            cwd=tmp_dir,
            capture_output=True,
            text=True,
        )
        if p_res.returncode != 0:
            print("Pytest stdout:\n", p_res.stdout)
            print("Pytest stderr:\n", p_res.stderr)
            raise RuntimeError("Pytest failed in fresh clone")

        # Extract and print pytest summary line
        pytest_lines = [line.strip() for line in p_res.stdout.splitlines() if line.strip()]
        pytest_summary = pytest_lines[-1] if pytest_lines else "No pytest output"
        print(f"  Pytest Summary: {pytest_summary}")

        # 8. Run python -m barilink.cli pipeline --profile ci
        print("  Running: python -m barilink.cli pipeline --profile ci")
        subprocess.check_call(
            [python_bin, "-m", "barilink.cli", "pipeline", "--profile", "ci"],
            cwd=tmp_dir,
            stdout=subprocess.DEVNULL,
        )

        # 9. Assert no tracked files modified
        print("  Running: git diff --exit-code")
        subprocess.check_call(["git", "diff", "--exit-code"], cwd=tmp_dir)

        print("\n" + "=" * 70)
        print("CI PROOF PASSED: Test suite & pipeline execute cleanly in isolation!")
        print(f"Clone Path:     {tmp_dir}")
        print(f"HEAD SHA:       {head_sha}")
        print(f"Pytest Summary: {pytest_summary}")
        print("=" * 70 + "\n")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
