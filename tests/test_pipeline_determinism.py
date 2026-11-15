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


def test_household_2x_determinism_across_hashseeds(tmp_path):
    """Subprocess PYTHONHASHSEED=0 vs 12345 test for 2.0x household evidence & inference."""
    script = tmp_path / "run_hh_2x.py"
    script.write_text(
        """
import random
import sys
from pathlib import Path
import pandas as pd
from barilink.household.evidence import (
    DEFAULT_HOUSEHOLD_WEIGHTS,
    UnitProfile,
    build_household_evidence,
)
from barilink.household.infer import infer_households

out_dir = Path(sys.argv[1])
out_dir.mkdir(parents=True, exist_ok=True)

# 16-unit component (> max_size=12, <= 25) with tied 2.0x weights + 2 distinct husbands
profiles = {}
for i in range(16):
    cid = f"c_{i:04d}"
    husb = "h_alpha" if i == 0 else ("h_beta" if i == 15 else None)
    name_sk = "h_alpha" if i == 1 else ("h_beta" if i == 14 else f"n_{i}")
    profiles[cid] = UnitProfile(
        cluster_id=cid,
        record_ids=[f"r_{i}"],
        village_canon="v1",
        village_raw="v1",
        union_raw="u1",
        display_name=name_sk,
        display_name_skeleton=name_sk,
        name_skels={name_sk},
        roster_skels={"shared_a", "shared_b"},
        husband_name=husb,
        husband_skeleton=husb,
        has_husband=husb is not None,
        father_name=None,
        father_skeleton=None,
        inferred_sex="F" if husb is not None else "M",
        birth_year=1990,
        age=35.0,
        phones={"01700000000"},
        phone_sources={},
        modules={"upg_enrolment"},
        first_enrolment="2025-01-01",
        last_enrolment="2025-01-01",
    )

w2 = {k: v * 2.0 for k, v in DEFAULT_HOUSEHOLD_WEIGHTS.items()}
edges_df = build_household_evidence(profiles, weights=w2)
hh_df, log_df = infer_households(profiles, edges_df, t_hh=5.0)
edges_df.to_parquet(out_dir / "edges.parquet", index=False)
hh_df.to_parquet(out_dir / "hh.parquet", index=False)
log_df.to_parquet(out_dir / "log.parquet", index=False)

# Sparse 30-node component with tied min-cuts after BFS split (catches infer.py hash-order bug)
rng = random.Random(3)
tie_profiles = {
    f"c_{i:02d}": UnitProfile(
        cluster_id=f"c_{i:02d}",
        record_ids=[f"tr_{i}"],
        village_canon="v2",
        village_raw="v2",
        union_raw="u2",
        display_name=f"tn_{i}",
        display_name_skeleton=f"tn_{i}",
        name_skels={f"tn_{i}"},
        roster_skels=set(),
        husband_name=None,
        husband_skeleton=None,
        has_husband=False,
        father_name=None,
        father_skeleton=None,
        inferred_sex="M",
        birth_year=1990,
        age=35.0,
        phones=set(),
        phone_sources={},
        modules={"upg_enrolment"},
        first_enrolment="2025-01-01",
        last_enrolment="2025-01-01",
    )
    for i in range(30)
}
tie_edges = {(f"c_{i:02d}", f"c_{i+1:02d}") for i in range(29)}
for _ in range(35):
    a, b = rng.sample(range(30), 2)
    tie_edges.add((f"c_{min(a, b):02d}", f"c_{max(a, b):02d}"))
tie_ev = pd.DataFrame(
    [
        {
            "unit_id_l": u,
            "unit_id_r": v,
            "score": 8.0,
            "e1": True,
            "e2": False,
            "e3": False,
            "e4": False,
            "e5": False,
            "evidence_lineage": "{}",
        }
        for u, v in sorted(tie_edges)
    ]
)
tie_hh, tie_log = infer_households(tie_profiles, tie_ev, t_hh=5.0)
tie_hh.to_parquet(out_dir / "tie_hh.parquet", index=False)
tie_log.to_parquet(out_dir / "tie_log.parquet", index=False)
""",
        encoding="utf-8",
    )

    for seed in ("0", "12345"):
        env = os.environ.copy()
        env["PYTHONHASHSEED"] = seed
        proc = subprocess.run(
            [sys.executable, str(script), str(tmp_path / f"seed_{seed}")],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 0, f"PYTHONHASHSEED={seed} failed:\n{proc.stderr}"

    for fname in (
        "edges.parquet",
        "hh.parquet",
        "log.parquet",
        "tie_hh.parquet",
        "tie_log.parquet",
    ):
        df0 = pd.read_parquet(tmp_path / "seed_0" / fname)
        df1 = pd.read_parquet(tmp_path / "seed_12345" / fname)
        pd.testing.assert_frame_equal(df0, df1, check_like=False)

    log0 = pd.read_parquet(tmp_path / "seed_0" / "log.parquet")
    assert (log0["action"] == "max_size_cut").any()
    assert (log0["action"] == "cannot_household_cut").any()

