"""Proof of CI safety in an isolated clone and clean virtual environment."""

import os
import shutil
import subprocess
import sys
import tempfile

if __name__ == "__main__":
    print("Starting fresh clone and venv test...")

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    tmp_dir = tempfile.mkdtemp(prefix="barilink_clone_test_")
    try:
        print(f"Cloning from {repo_root} to: {tmp_dir}")
        subprocess.check_call(["git", "clone", repo_root, tmp_dir])

        # Copy uncommitted / untracked files into the clone so it represents
        # the candidate working tree
        for root, dirs, files in os.walk(repo_root):
            if any(
                skip in root
                for skip in [
                    ".venv",
                    ".git",
                    "__pycache__",
                    "web/public/data",
                    "data/generated",
                    "results/ci",
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

        # Ensure web/public/data/.gitkeep exists in the clone
        os.makedirs(os.path.join(tmp_dir, "web", "public", "data"), exist_ok=True)
        with open(os.path.join(tmp_dir, "web", "public", "data", ".gitkeep"), "w") as f:
            pass

        print("Creating fresh venv in clone...")
        venv_dir = os.path.join(tmp_dir, ".fresh_venv")
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
        if sys.platform == "win32":
            python_bin = os.path.join(venv_dir, "Scripts", "python.exe")
            pytest_bin = os.path.join(venv_dir, "Scripts", "pytest.exe")
        else:
            python_bin = os.path.join(venv_dir, "bin", "python")
            pytest_bin = os.path.join(venv_dir, "bin", "pytest")

        print("Installing editable package with dev dependencies...")
        subprocess.check_call(
            [python_bin, "-m", "pip", "install", "--quiet", "-e", tmp_dir + "[dev]"]
        )

        print("Running pytest -q -m 'not publish' in fresh clone...")
        p_res = subprocess.run(
            [pytest_bin, "-q", "-m", "not publish"],
            cwd=tmp_dir,
            capture_output=True,
            text=True,
        )
        print(p_res.stdout)
        if p_res.returncode != 0:
            print("Pytest STDERR:", p_res.stderr)
            raise RuntimeError("Pytest failed in fresh clone")

        print("Running python -m barilink.cli pipeline --profile ci in fresh clone...")
        ci_res = subprocess.run(
            [python_bin, "-m", "barilink.cli", "pipeline", "--profile", "ci"],
            cwd=tmp_dir,
            capture_output=True,
            text=True,
        )
        print(ci_res.stdout)
        if ci_res.returncode != 0:
            print("CI pipeline STDERR:", ci_res.stderr)
            raise RuntimeError("CI pipeline failed in fresh clone")

        print("SUCCESS: Both pytest and CI pipeline succeeded in a fresh clone from scratch!")
    finally:
        print(f"Cleaning up temporary directory: {tmp_dir}")
        shutil.rmtree(tmp_dir, ignore_errors=True)

