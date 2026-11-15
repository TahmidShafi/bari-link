"""Reproduce all bari-link experiment runs, confirmation tables, and summaries."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def run_cmd(args: list[str]) -> None:
    cmd = [sys.executable, *args]
    print(f"+ {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, check=True)


def clean_sweep_outputs() -> None:
    """Delete all sweep-generated outputs so nothing is read from stale state."""
    runs = ["demo", *[f"holdout_{i}" for i in range(10)], "stress_0"]
    for run_name in runs:
        shutil.rmtree(Path("data/generated") / run_name, ignore_errors=True)
        shutil.rmtree(Path("results") / run_name, ignore_errors=True)

    for model in (
        "splink_v1",
        "splink_v2",
        "splink_v3",
        "splink_v3_no_tf",
        "splink_v3_no_kinship",
        "splink_v3_1",
        "splink_k",
    ):
        shutil.rmtree(Path("results/models") / model, ignore_errors=True)

    for resolved in (
        "splink_v1_resolved",
        "splink_v3_resolved",
        "splink_v3_1_resolved",
        "splink_k_resolved",
    ):
        sel = Path("results") / resolved / "selected_thresholds.json"
        if sel.exists():
            sel.unlink()

    shutil.rmtree(Path("results/holdout_confirm"), ignore_errors=True)
    for summary_file in (
        "confirm_table.json",
        "household_table.json",
        "leakage_comparison.json",
        "h1_dev_outcome.json",
        "h2_dev_outcome.json",
        "preregistration.json",
        "untrained_params_audit.json",
    ):
        p = Path("results/summary") / summary_file
        if p.exists():
            p.unlink()


def main() -> int:
    clean_sweep_outputs()

    # 1. Build synthetic populations
    run_cmd(
        [
            "-m",
            "barilink.cli",
            "build",
            "--config",
            "configs/default.yaml",
            "--run-name",
            "demo",
            "--seed-offset",
            "0",
            "--role",
            "dev",
        ]
    )
    for i in range(5):
        run_cmd(
            [
                "-m",
                "barilink.cli",
                "build",
                "--config",
                "configs/default.yaml",
                "--run-name",
                f"holdout_{i}",
                "--seed-offset",
                str(1000 + i),
                "--role",
                "holdout",
            ]
        )
    for i in range(5, 10):
        run_cmd(
            [
                "-m",
                "barilink.cli",
                "build",
                "--config",
                "configs/default.yaml",
                "--run-name",
                f"holdout_{i}",
                "--seed-offset",
                str(1000 + i),
                "--role",
                "holdout",
            ]
        )
    run_cmd(
        [
            "-m",
            "barilink.cli",
            "build",
            "--config",
            "configs/stress.yaml",
            "--run-name",
            "stress_0",
            "--seed-offset",
            "0",
            "--role",
            "stress",
        ]
    )

    # 2. Train Splink models on demo
    for model in (
        "splink_v1",
        "splink_v2",
        "splink_v3",
        "splink_v3_no_tf",
        "splink_v3_no_kinship",
        "splink_v3_1",
        "splink_k",
    ):
        run_cmd(
            [
                "-m",
                "barilink.cli",
                "link",
                "train",
                "--config",
                "configs/default.yaml",
                "--run-name",
                "demo",
                "--model",
                model,
                "--threads",
                "1",
            ]
        )

    # 3. Predict & resolve on demo (dev threshold selection)
    for model in ("splink_v1", "splink_v3", "splink_v3_1", "splink_k"):
        run_cmd(
            [
                "-m",
                "barilink.cli",
                "link",
                "predict",
                "--config",
                "configs/default.yaml",
                "--run-name",
                "demo",
                "--model",
                model,
                "--threads",
                "1",
            ]
        )
        run_cmd(
            [
                "-m",
                "barilink.cli",
                "resolve",
                "--mode",
                "select",
                "--run-name",
                "demo",
                "--base-method",
                model,
                "--config",
                "configs/default.yaml",
            ]
        )
    run_cmd(
        [
            "-m",
            "barilink.cli",
            "evaluate",
            "batch",
            "--runs",
            "demo",
            "--methods",
            "splink_v1",
            "splink_v1_resolved",
            "splink_v2",
            "splink_v3",
            "splink_v3_resolved",
            "splink_v3_1",
            "splink_v3_1_resolved",
            "splink_k",
            "splink_k_resolved",
            "--threads",
            "1",
        ]
    )

    # 4. Deterministic baseline on holdout_5..9
    for i in range(5, 10):
        run_cmd(
            [
                "-m",
                "barilink.cli",
                "baseline",
                "--method",
                "exact_or_phone",
                "--run-name",
                f"holdout_{i}",
            ]
        )
        run_cmd(
            [
                "-m",
                "barilink.cli",
                "evaluate",
                "--run-name",
                f"holdout_{i}",
                "--method",
                "exact_or_phone",
                "--mode",
                "report",
            ]
        )

    # 5. Batch evaluation across holdouts and stress_0
    run_cmd(
        [
            "-m",
            "barilink.cli",
            "evaluate",
            "batch",
            "--runs",
            "holdout_0..holdout_4",
            "--methods",
            "splink_v1",
            "splink_v1_resolved",
            "--threads",
            "1",
        ]
    )
    run_cmd(
        [
            "-m",
            "barilink.cli",
            "evaluate",
            "batch",
            "--runs",
            "holdout_5..holdout_9",
            "--methods",
            "splink_v3_1",
            "splink_v3_1_resolved",
            "splink_k",
            "splink_k_resolved",
            "--threads",
            "1",
        ]
    )
    run_cmd(
        [
            "-m",
            "barilink.cli",
            "evaluate",
            "batch",
            "--runs",
            "stress_0",
            "--methods",
            "splink_v1",
            "splink_v2",
            "splink_v3",
            "splink_v3_no_tf",
            "splink_v3_no_kinship",
            "splink_v3_resolved",
            "splink_v3_1_resolved",
            "splink_k_resolved",
            "--threads",
            "1",
        ]
    )

    # 6. Stress table & curves, H3 confirm table, household confirmation
    run_cmd(["-m", "barilink.cli", "evaluate", "stress", "--run-name", "stress_0"])
    run_cmd(["-m", "barilink.cli", "evaluate", "confirm", "--runs", "holdout_5..holdout_9"])
    run_cmd(
        [
            "-m",
            "barilink.cli",
            "evaluate",
            "household-confirm",
            "--runs",
            "holdout_5",
            "holdout_6",
            "holdout_7",
            "holdout_8",
            "holdout_9",
            "--threshold",
            "5.0",
        ]
    )

    # 7. Summary JSONs & audits
    run_cmd(
        [
            "-m",
            "barilink.cli",
            "evaluate",
            "summarize",
            "--results-dir",
            "results",
            "--data-dir",
            "data/generated",
            "--output-dir",
            "results/summary",
        ]
    )
    run_cmd(["scripts/generate_preregistration_json.py"])
    run_cmd(["-m", "barilink.evaluate.audit_untrained"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
