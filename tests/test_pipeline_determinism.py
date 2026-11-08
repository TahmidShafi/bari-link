"""Determinism regression test: Run the CI-profile pipeline across different PYTHONHASHSEED values.

Asserts identical person cluster IDs, household cluster IDs, and evaluation metrics.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pandas as pd


def test_pipeline_determinism_across_hashseeds(tmp_path):
    python_exe = sys.executable

    run_1_dir = tmp_path / "run_hash_1"
    run_999_dir = tmp_path / "run_hash_999"

    cmd_base = [
        python_exe,
        "-m",
        "barilink.cli",
        "pipeline",
        "--profile",
        "ci",
        "--run-name",
        "ci_test",
    ]

    # Subprocess 1: PYTHONHASHSEED=1
    env_1 = os.environ.copy()
    env_1["PYTHONHASHSEED"] = "1"
    cmd_1 = cmd_base + [
        "--data-dir",
        str(run_1_dir / "data"),
        "--results-dir",
        str(run_1_dir / "results"),
        "--web-dir",
        str(run_1_dir / "web_data"),
    ]
    proc_1 = subprocess.run(
        cmd_1,
        env=env_1,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc_1.returncode == 0, (
        f"Run with PYTHONHASHSEED=1 failed:\n{proc_1.stderr}\n{proc_1.stdout}"
    )

    # Subprocess 2: PYTHONHASHSEED=999
    env_999 = os.environ.copy()
    env_999["PYTHONHASHSEED"] = "999"
    cmd_999 = cmd_base + [
        "--data-dir",
        str(run_999_dir / "data"),
        "--results-dir",
        str(run_999_dir / "results"),
        "--web-dir",
        str(run_999_dir / "web_data"),
    ]
    proc_999 = subprocess.run(
        cmd_999,
        env=env_999,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc_999.returncode == 0, (
        f"Run with PYTHONHASHSEED=999 failed:\n{proc_999.stderr}\n{proc_999.stdout}"
    )

    # 1. Compare Person Cluster IDs (record_id -> cluster_id)
    p_path1 = run_1_dir / "results" / "ci_test" / "splink_k_resolved" / "clusters.parquet"
    p_path999 = run_999_dir / "results" / "ci_test" / "splink_k_resolved" / "clusters.parquet"
    clusters_1 = pd.read_parquet(p_path1)
    clusters_999 = pd.read_parquet(p_path999)

    c1_sorted = clusters_1.sort_values("record_id").reset_index(drop=True)
    c999_sorted = clusters_999.sort_values("record_id").reset_index(drop=True)

    pd.testing.assert_frame_equal(c1_sorted, c999_sorted, check_like=False)

    # 2. Compare Household Cluster IDs (person cluster_id -> household_id)
    hh_path1 = run_1_dir / "results" / "ci_test" / "household" / "household_clusters.parquet"
    hh_path999 = run_999_dir / "results" / "ci_test" / "household" / "household_clusters.parquet"
    hh_clusters_1 = pd.read_parquet(hh_path1)
    hh_clusters_999 = pd.read_parquet(hh_path999)

    hh1_sorted = hh_clusters_1.sort_values("cluster_id").reset_index(drop=True)
    hh999_sorted = hh_clusters_999.sort_values("cluster_id").reset_index(drop=True)

    pd.testing.assert_frame_equal(hh1_sorted, hh999_sorted, check_like=False)

    # 3. Compare Person Linkage Metrics
    m1_file = run_1_dir / "results" / "ci_test" / "splink_k_resolved" / "metrics.json"
    m999_file = run_999_dir / "results" / "ci_test" / "splink_k_resolved" / "metrics.json"
    with open(m1_file, "r", encoding="utf-8") as f:
        p_m1 = json.load(f)["headline_metrics_at_t_cost"]
    with open(m999_file, "r", encoding="utf-8") as f:
        p_m999 = json.load(f)["headline_metrics_at_t_cost"]

    assert p_m1 == p_m999

    # 4. Compare Household Inference Metrics
    hh_m1_file = run_1_dir / "results" / "ci_test" / "household" / "household_metrics.json"
    hh_m999_file = run_999_dir / "results" / "ci_test" / "household" / "household_metrics.json"
    with open(hh_m1_file, "r", encoding="utf-8") as f:
        hh_m1 = json.load(f)
    with open(hh_m999_file, "r", encoding="utf-8") as f:
        hh_m999 = json.load(f)

    assert hh_m1 == hh_m999
