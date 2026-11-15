"""Deterministic run-level provenance writer for sweep stages."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional, Sequence

KEY_PACKAGES = ("splink", "duckdb", "numpy", "pandas", "pyarrow", "networkx")


def _git_commit() -> Optional[str]:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def _git_dirty() -> Optional[bool]:
    try:
        out = subprocess.check_output(
            [
                "git",
                "status",
                "--porcelain",
                "--",
                "src/",
                "scripts/",
                "configs/",
                "pyproject.toml",
                "requirements-lock.txt",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return bool(out.strip())
    except Exception:
        return None


def _file_sha256(path: Optional[str | Path]) -> Optional[str]:
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _read_manifest_seed_offset(data_dir: str | Path, run_name: str) -> Optional[int]:
    manifest_path = Path(data_dir) / run_name / "manifest.json"
    if not manifest_path.exists():
        return None
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        val = data.get("seed_offset")
        return int(val) if val is not None else None
    except Exception:
        return None


def write_run_provenance(
    run_dir: Path,
    command: str,
    cli_args: Sequence[str],
    seed_offset: Optional[int] = None,
    config_path: Optional[str | Path] = None,
    data_dir: str | Path = "data/generated",
    run_name: Optional[str] = None,
) -> Path:
    """Persist deterministic provenance.json (no timestamps) for a run stage."""
    run_dir.mkdir(parents=True, exist_ok=True)
    prov_path = run_dir / "provenance.json"

    if seed_offset is None and run_name:
        seed_offset = _read_manifest_seed_offset(data_dir, run_name)

    pkg_versions: dict[str, Optional[str]] = {}
    for pkg in KEY_PACKAGES:
        try:
            pkg_versions[pkg] = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            pkg_versions[pkg] = None

    args_list = list(cli_args)
    entry: dict[str, Any] = {
        "command": command,
        "cli_args": args_list,
        "seed_offset": seed_offset,
        "config_path": str(config_path) if config_path else None,
        "config_sha256": _file_sha256(config_path),
    }

    if prov_path.exists():
        data = json.loads(prov_path.read_text(encoding="utf-8"))
    else:
        data = {}

    stages: list[dict[str, Any]] = data.get("stages", [])
    stages = [
        s
        for s in stages
        if not (s.get("command") == command and s.get("cli_args") == args_list)
    ]
    stages.append(entry)

    payload = {
        "git_commit": _git_commit(),
        "git_dirty": _git_dirty(),
        "platform": sys.platform,
        "python_version": platform.python_version(),
        "packages": pkg_versions,
        "stages": stages,
    }
    prov_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return prov_path
