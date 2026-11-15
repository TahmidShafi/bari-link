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

    for method_or_resolved in (
        "exact",
        "exact_or_phone",
        "phone",
        "no_link",
        "splink_v1",
        "splink_v2",
        "splink_v3",
        "splink_v3_no_tf",
        "splink_v3_no_kinship",
        "splink_v3_1",
        "splink_k",
        "splink_v1_resolved",
        "splink_v3_resolved",
        "splink_v3_1_resolved",
        "splink_k_resolved",
    ):
        sel = Path("results") / method_or_resolved / "selected_thresholds.json"
        if sel.exists():
            sel.unlink()

    ablation_md = Path("results/holdout/ablation_table.md")
    if ablation_md.exists():
        ablation_md.unlink()

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

    # 3. Predict, select thresholds, & resolve on demo (dev threshold selection)
    resolved_bases = {"splink_v1", "splink_v3", "splink_v3_1", "splink_k"}
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
                "evaluate",
                "--run-name",
                "demo",
                "--method",
                model,
                "--mode",
                "select",
            ]
        )
        if model in resolved_bases:
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
            "splink_v1_resolved",
            "splink_v3_resolved",
            "splink_v3_1_resolved",
            "splink_k_resolved",
            "--threads",
            "1",
        ]
    )

    # 4. Deterministic baselines: all four on demo (select) and holdout_0..4 (report);
    #    exact_or_phone on holdout_5..9 (report)
    for method in ("exact", "exact_or_phone", "phone", "no_link"):
        run_cmd(["-m", "barilink.cli", "baseline", "--method", method, "--run-name", "demo"])
        run_cmd(
            [
                "-m",
                "barilink.cli",
                "evaluate",
                "--run-name",
                "demo",
                "--method",
                method,
                "--mode",
                "select",
            ]
        )
    for i in range(5):
        for method in ("exact", "exact_or_phone", "phone", "no_link"):
            run_cmd(
                ["-m", "barilink.cli", "baseline", "--method", method, "--run-name", f"holdout_{i}"]
            )
            run_cmd(
                [
                    "-m",
                    "barilink.cli",
                    "evaluate",
                    "--run-name",
                    f"holdout_{i}",
                    "--method",
                    method,
                    "--mode",
                    "report",
                ]
            )
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
            "splink_v2",
            "splink_v3",
            "splink_v3_no_kinship",
            "splink_v3_no_tf",
            "splink_v3_resolved",
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
            "splink_v3_1",
            "splink_v3_1_resolved",
            "splink_k",
            "splink_k_resolved",
            "--threads",
            "1",
        ]
    )

    # 5b. Diagnostics, blocking, golden records, and clerical review simulation
    run_cmd(
        [
            "-m",
            "barilink.cli",
            "evaluate",
            "diagnose",
            "--run-name",
            "demo",
            "--method",
            "splink_v1",
        ]
    )
    run_cmd(
        ["-m", "barilink.cli", "link", "diagnose", "--run-name", "demo", "--model", "splink_v1"]
    )
    run_cmd(
        [
            "-m",
            "barilink.cli",
            "evaluate",
            "blocking",
            "--run-name",
            "holdout_0",
            "--method",
            "splink_v1",
        ]
    )
    run_cmd(
        [
            "-m",
            "barilink.cli",
            "link",
            "diagnose",
            "--run-name",
            "holdout_0",
            "--model",
            "splink_v1",
        ]
    )
    run_cmd(
        [
            "-m",
            "barilink.cli",
            "golden",
            "--run-name",
            "holdout_0",
            "--method",
            "splink_v1_resolved",
        ]
    )
    run_cmd(
        [
            "-m",
            "barilink.cli",
            "review",
            "--run-name",
            "holdout_0",
            "--method",
            "splink_v1_resolved",
        ]
    )

    # 6. Ablation table, stress table & curves, H3 confirm table, household confirmation
    run_cmd(["-m", "barilink.cli", "evaluate", "ablation", "--runs", "holdout_0..holdout_4"])
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
