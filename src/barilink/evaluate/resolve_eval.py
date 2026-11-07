"""Resolve parameter selection and evaluation harness integration (reads ground truth)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from barilink.resolve.graph import build_resolved_graph, select_resolve_parameters


def run_resolve_select(
    run_name: str = "demo",
    config_path: str = "configs/default.yaml",
    base_data_dir: str = "data/generated",
    base_results_dir: str = "results",
) -> dict[str, Any]:
    """Execute resolve parameter selection on development dataset (authorized to read truth)."""
    cfg_p = Path(config_path)
    config = {}
    if cfg_p.exists():
        with open(cfg_p, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

    resolve_cfg = config.get("resolve", {})
    max_gap = int(resolve_cfg.get("max_birth_year_gap", 10))

    run_dir = Path(base_data_dir) / run_name
    manifest_p = run_dir / "manifest.json"
    if manifest_p.exists():
        with open(manifest_p, "r", encoding="utf-8") as f:
            m_data = json.load(f)
            if m_data.get("role") == "holdout":
                raise ValueError(f"Cannot run select mode on holdout dataset '{run_name}'.")

    records_path = run_dir / "registry" / "records.parquet"
    splink_dir = Path(base_results_dir) / run_name / "splink_v1"
    preds_path = splink_dir / "predictions.parquet"
    out_dir = Path(base_results_dir) / run_name / "splink_v1_resolved"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not records_path.exists():
        raise FileNotFoundError(f"Records not found at {records_path}")
    if not preds_path.exists():
        raise FileNotFoundError(f"Splink predictions not found at {preds_path}")

    records_df = pd.read_parquet(records_path)
    preds_df = pd.read_parquet(preds_path)

    truth_dir = run_dir / "truth"
    record_truth_df = pd.read_parquet(truth_dir / "record_truth.parquet")
    true_pairs_df = pd.read_parquet(truth_dir / "true_pairs.parquet")
    doppel_df = pd.read_parquet(truth_dir / "doppelganger_person_pairs.parquet")

    print(f"Sweeping resolve grid on dev run '{run_name}'...")
    best_params, grid_df = select_resolve_parameters(
        predictions_df=preds_df,
        records_df=records_df,
        record_truth_df=record_truth_df,
        true_pairs_df=true_pairs_df,
        doppelganger_person_pairs_df=doppel_df,
        max_birth_year_gap=max_gap,
        output_dir=out_dir,
    )

    sel_path = Path(base_results_dir) / "splink_v1_resolved" / "selected_thresholds.json"
    sel_path.parent.mkdir(parents=True, exist_ok=True)
    with open(sel_path, "w", encoding="utf-8") as f:
        json.dump(best_params, f, indent=2)

    t_l = best_params["t_link"]
    t_b = best_params["t_bridge"]
    clusters_df, res_log_df = build_resolved_graph(
        predictions_df=preds_df,
        records_df=records_df,
        t_link=t_l,
        t_bridge=t_b,
        max_birth_year_gap=max_gap,
    )
    clusters_df.to_parquet(out_dir / "clusters.parquet", index=False)
    res_log_df.to_parquet(out_dir / "resolution_log.parquet", index=False)

    return best_params
