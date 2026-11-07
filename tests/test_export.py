"""Data-contract tests for web export."""

import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

from barilink.pipeline import run_pipeline


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def _verify_web_data_contract(web_dir: Path):
    """Verify data contracts for exported web data."""
    manifest_path = web_dir / "manifest.json"
    assert manifest_path.exists(), "manifest.json must exist"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert "schema_version" in manifest
    assert "git_sha" in manifest
    assert "git_dirty" in manifest
    assert "files" in manifest

    # 1. Total size <= 25 MB
    total_bytes = sum(entry["byte_size"] for entry in manifest["files"].values())
    total_mb = total_bytes / (1024 * 1024)
    assert total_mb <= 25.0, f"Total size {total_mb:.2f} MB exceeds 25 MB budget"

    # 2. Manifest hash and byte size integrity
    for rel_name, meta in manifest["files"].items():
        file_p = web_dir / rel_name
        assert file_p.exists(), f"File in manifest missing on disk: {rel_name}"
        actual_size = file_p.stat().st_size
        assert actual_size == meta["byte_size"], f"Size mismatch for {rel_name}"
        actual_hash = _sha256(file_p)
        assert actual_hash == meta["sha256"], f"SHA-256 mismatch for {rel_name}"

    # 3. Model-visible files must NOT contain ground-truth columns
    forbidden_tokens = ["person_id", "household_id", "clean_"]
    for p in web_dir.glob("*.parquet"):
        df = pd.read_parquet(p)
        for col in df.columns:
            for token in forbidden_tokens:
                assert (
                    token not in col
                ), f"Forbidden truth column '{col}' found in model-visible file {p.name}"

    # 4. Records, Labels, Pairs, and Clusters integrity
    records_df = pd.read_parquet(web_dir / "records.parquet")
    valid_record_ids = set(records_df["record_id"].astype(str))
    assert len(valid_record_ids) == len(records_df), "record_id must be unique in records.parquet"

    eval_labels_path = web_dir / "eval" / "record_labels.parquet"
    assert eval_labels_path.exists(), "eval/record_labels.parquet must exist"
    labels_df = pd.read_parquet(eval_labels_path)
    assert (
        labels_df["record_id"].nunique() == len(labels_df)
    ), "record_id must be unique in record_labels.parquet"
    assert len(labels_df) == len(records_df), (
        f"Row count mismatch: record_labels ({len(labels_df)}) != records ({len(records_df)})"
    )
    assert set(labels_df["record_id"].astype(str)) == valid_record_ids, (
        "record_id sets must match between records and record_labels"
    )

    pairs_df = pd.read_parquet(web_dir / "pairs.parquet")
    for r_l in pairs_df["record_id_l"].astype(str):
        assert r_l in valid_record_ids, f"record_id_l {r_l} not in records"
    for r_r in pairs_df["record_id_r"].astype(str):
        assert r_r in valid_record_ids, f"record_id_r {r_r} not in records"

    clusters_df = pd.read_parquet(web_dir / "clusters_by_threshold.parquet")
    for r in clusters_df["record_id"].astype(str):
        assert r in valid_record_ids, f"Cluster record_id {r} not in records"

    # 5. Every t_link has exactly one cluster_id per record; rows = n_thresholds x n_records
    n_thresholds = clusters_df["t_link"].nunique()
    n_records = len(records_df)
    assert len(clusters_df) == n_thresholds * n_records, (
        f"clusters rows ({len(clusters_df)}) != thresholds ({n_thresholds}) x records ({n_records})"
    )

    eval_thresh_path = web_dir / "eval" / "threshold_table.parquet"
    assert eval_thresh_path.exists(), "eval/threshold_table.parquet must exist"
    thresh_table_df = pd.read_parquet(eval_thresh_path)
    assert set(clusters_df["t_link"].unique()) == set(thresh_table_df["t_link"].unique()), (
        "Distinct t_link set in clusters_by_threshold must equal threshold_table t_link set"
    )

    for t_val, grp in clusters_df.groupby("t_link"):
        assert len(grp) == len(
            records_df
        ), f"t_link={t_val} has {len(grp)} rows, expected {len(records_df)}"
        assert (
            grp["record_id"].nunique() == len(records_df)
        ), f"t_link={t_val} has duplicate records"


def test_ci_web_export_data_contract(tmp_path: Path):
    """Run pipeline smoke-test under tmp_path and verify web data contracts."""
    data_dir = tmp_path / "data"
    results_dir = tmp_path / "results"
    web_dir = tmp_path / "web_data"

    run_pipeline(
        profile="ci",
        run_name="ci_test",
        config_path="configs/ci.yaml",
        base_data_dir=str(data_dir),
        base_results_dir=str(results_dir),
        web_dir=str(web_dir),
    )

    _verify_web_data_contract(web_dir)


@pytest.mark.publish
def test_publish_web_export_data_contract():
    """Verify data contracts on full published holdout_5 web assets."""
    pub_web_dir = Path("web/public/data")
    assert (
        pub_web_dir.exists()
    ), "web/public/data does not exist. Run 'pipeline --profile publish' first."
    _verify_web_data_contract(pub_web_dir)
