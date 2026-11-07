"""Batch evaluation orchestrator across multiple runs and linkage/resolution methods."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional, Sequence

import pandas as pd

from barilink.evaluate.aggregate import parse_runs_argument
from barilink.evaluate.report import (
    generate_evaluation_report,
    generate_resolved_evaluation_report,
)
from barilink.link.model import predict_splink_model
from barilink.link.normalise import export_features
from barilink.resolve.graph import build_resolved_graph, precompute_ui_clusters


def run_batch_evaluation(
    runs: Sequence[str] | str = "holdout_0..holdout_4",
    methods: Optional[Sequence[str]] = None,
    base_data_dir: str | Path = "data/generated",
    base_results_dir: str | Path = "results",
    threads: int = 1,
) -> None:
    """Batch predict, resolve, and evaluate methods across specified runs."""
    run_list = parse_runs_argument(runs)
    if methods is None:
        methods = [
            "splink_v1",
            "splink_v2",
            "splink_v3",
            "splink_v3_no_tf",
            "splink_v3_no_kinship",
            "splink_v3_resolved",
        ]
    else:
        flat_methods = []
        for m in methods:
            for item in str(m).split(","):
                item_s = item.strip()
                if item_s:
                    flat_methods.append(item_s)
        methods = flat_methods

    for run_name in run_list:
        run_dir = Path(base_data_dir) / run_name
        feat_path = run_dir / "registry" / "features.parquet"
        if not feat_path.exists():
            print(f"Generating features for '{run_name}'...")
            features_df = export_features(run_name, base_data_dir)
        else:
            features_df = pd.read_parquet(feat_path)

        records_path = run_dir / "registry" / "records.parquet"
        records_df = pd.read_parquet(records_path)

        for method in methods:
            print(f"\n=== Batch Evaluation: {method} on {run_name} ===")
            t0 = time.time()

            if method.endswith("_resolved"):
                base_method = method.replace("_resolved", "")
                base_preds_path = (
                    Path(base_results_dir) / run_name / base_method / "predictions.parquet"
                )
                if not base_preds_path.exists():
                    base_model_path = (
                        Path(base_results_dir) / "models" / base_method / "model.json"
                    )
                    print(f"  Scoring base predictions for {base_method}...")
                    base_preds_df, _, _ = predict_splink_model(
                        features_df=features_df,
                        model_settings_or_path=base_model_path,
                        run_name=run_name,
                        base_results_dir=str(base_results_dir),
                        method=base_method,
                        threads=threads,
                    )
                else:
                    base_preds_df = pd.read_parquet(base_preds_path)

                sel_path = Path(base_results_dir) / method / "selected_thresholds.json"
                if not sel_path.exists():
                    raise FileNotFoundError(f"Selected thresholds not found at {sel_path}")

                with open(sel_path, "r", encoding="utf-8") as f:
                    sel = json.load(f)
                t_l = float(sel["t_link"])
                t_b = float(sel["t_bridge"])

                out_dir = Path(base_results_dir) / run_name / method
                out_dir.mkdir(parents=True, exist_ok=True)

                apply_listed = (
                    "v3" in base_method
                    or "v3" in method
                    or "k" in base_method.lower().split("_")
                    or "k" in method.lower().split("_")
                    or "splink_k" in base_method
                    or "splink_k" in method
                )
                clusters_df, res_log_df = build_resolved_graph(
                    predictions_df=base_preds_df,
                    records_df=records_df,
                    t_link=t_l,
                    t_bridge=t_b,
                    max_birth_year_gap=10,
                    features_df=features_df,
                    apply_listed_as_other_member=apply_listed,
                )
                clusters_df.to_parquet(out_dir / "clusters.parquet", index=False)
                res_log_df.to_parquet(out_dir / "resolution_log.parquet", index=False)

                if run_name == "holdout_0":
                    precompute_ui_clusters(
                        predictions_df=base_preds_df,
                        records_df=records_df,
                        t_bridge=t_b,
                        output_path=out_dir / "resolved_by_threshold.parquet",
                        max_birth_year_gap=10,
                        features_df=features_df,
                        apply_listed_as_other_member=apply_listed,
                    )

                generate_resolved_evaluation_report(
                    run_name=run_name,
                    method=method,
                    base_data_dir=base_data_dir,
                    base_results_dir=base_results_dir,
                )
                print(f"  Resolved and evaluated in {time.time() - t0:.1f}s")

            elif method in ("no_link", "exact", "phone", "exact_or_phone"):
                from barilink.baselines.exact import run_exact_baseline
                from barilink.baselines.phone import (
                    run_exact_or_phone_baseline,
                    run_phone_baseline,
                )
                from barilink.evaluate.contracts import PairwisePredictions

                m_dir = Path(base_results_dir) / run_name / method
                m_dir.mkdir(parents=True, exist_ok=True)
                preds_path = m_dir / "predictions.parquet"
                if not preds_path.exists():
                    if method == "no_link":
                        n_rec = len(records_df)
                        cand_pairs = (n_rec * (n_rec - 1)) // 2
                        empty_df = pd.DataFrame(
                            columns=["record_id_l", "record_id_r", "match_probability"]
                        )
                        res = PairwisePredictions(
                            predictions_df=empty_df,
                            candidate_pair_count=cand_pairs,
                            metadata={
                                "method": "no_link",
                                "description": "Empty predictions baseline (no links)",
                            },
                        )
                    elif method == "exact":
                        res = run_exact_baseline(records_df)
                    elif method == "phone":
                        res = run_phone_baseline(records_df)
                    elif method == "exact_or_phone":
                        res = run_exact_or_phone_baseline(records_df)

                    preds_df = res.predictions_df
                    cand_count = res.candidate_pair_count
                    preds_df.to_parquet(preds_path, index=False)
                    meta = {
                        "method": method,
                        "run_name": run_name,
                        "candidate_pair_count": cand_count,
                        "scored_pair_count": len(preds_df),
                    }
                    with open(m_dir / "metadata.json", "w", encoding="utf-8") as f:
                        json.dump(meta, f, indent=2)
                else:
                    preds_df = pd.read_parquet(preds_path)
                    with open(m_dir / "metadata.json", "r", encoding="utf-8") as f:
                        cand_count = json.load(f).get("candidate_pair_count", len(preds_df))

                generate_evaluation_report(
                    method_name=method,
                    run_name=run_name,
                    mode="report",
                    predictions_df=preds_df,
                    candidate_pair_count=cand_count,
                    base_data_dir=base_data_dir,
                    base_results_dir=base_results_dir,
                    grid="weight",
                )
                print(f"  Evaluated baseline {method} in {time.time() - t0:.1f}s")

            else:
                model_path = Path(base_results_dir) / "models" / method / "model.json"
                if not model_path.exists():
                    raise FileNotFoundError(f"Model settings not found at {model_path}")

                preds_df, _, cand_count = predict_splink_model(
                    features_df=features_df,
                    model_settings_or_path=model_path,
                    run_name=run_name,
                    base_results_dir=str(base_results_dir),
                    method=method,
                    threads=threads,
                )
                generate_evaluation_report(
                    method_name=method,
                    run_name=run_name,
                    mode="report",
                    predictions_df=preds_df,
                    candidate_pair_count=cand_count,
                    base_data_dir=base_data_dir,
                    base_results_dir=base_results_dir,
                    grid="weight",
                )
                print(
                    f"  Scored ({len(preds_df):,} pairs) and evaluated in "
                    f"{time.time() - t0:.1f}s"
                )

