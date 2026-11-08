"""Evaluation datasets generation for web UI overlay."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Optional, Sequence

import networkx as nx
import pandas as pd

from barilink.evaluate.clusters import evaluate_clusters
from barilink.evaluate.costs import compute_expected_cost
from barilink.evaluate.pairwise import compute_pairwise_metrics_from_counts
from barilink.resolve.review import build_review_queue


def _evaluate_variant_clusters(
    clusters_df: pd.DataFrame,
    variant_name: str,
    truth_records_df: pd.DataFrame,
    total_true_pairs: int,
    true_person_count: int,
    naive_records_count: int,
    record_person_map: dict[str, str],
    doppel_pairs_df: Optional[pd.DataFrame],
    pairs_df: Optional[pd.DataFrame] = None,
    resolution_logs_by_thresh: Optional[dict[float, pd.DataFrame]] = None,
) -> list[dict[str, Any]]:
    """Evaluate cluster metrics across threshold groups for a specific variant."""
    rows: list[dict[str, Any]] = []
    t_link_groups = clusters_df.groupby("t_link")

    for t_val, group_df in t_link_groups:
        c_metrics = evaluate_clusters(
            clusters_df=group_df,
            record_truth_df=truth_records_df,
            doppelganger_person_pairs_df=doppel_pairs_df,
        )

        cluster_records = group_df.groupby("cluster_id")["record_id"].apply(list)
        cluster_tp = 0
        cluster_fp = 0
        for _, rids in cluster_records.items():
            if len(rids) <= 1:
                continue
            p_counts = Counter(
                record_person_map.get(str(rid))
                for rid in rids
                if str(rid) in record_person_map
            )
            c_size = len(rids)
            c_pairs = (c_size * (c_size - 1)) // 2
            c_true = sum((cnt * (cnt - 1)) // 2 for cnt in p_counts.values())
            c_false = c_pairs - c_true
            cluster_tp += c_true
            cluster_fp += c_false

        pw = compute_pairwise_metrics_from_counts(
            tp=cluster_tp,
            fp=cluster_fp,
            total_true_pairs=total_true_pairs,
            edge_tp=0,
            edge_fp=0,
        )
        expected_cost = compute_expected_cost(
            fp=pw.fp,
            fn=pw.fn,
            cost_false_merge=5.0,
            cost_missed_duplicate=1.0,
        )
        dedup_reach = group_df["cluster_id"].nunique()

        q_size = 0
        if pairs_df is not None and not pairs_df.empty:
            res_log = None
            if resolution_logs_by_thresh is not None:
                res_log = resolution_logs_by_thresh.get(float(t_val))
            q_df = build_review_queue(
                predictions_df=pairs_df,
                clusters_df=group_df,
                resolution_log_df=res_log,
                t_link=float(t_val),
                window_delta=6.0,
            )
            q_size = len(q_df)

        rows.append(
            {
                "t_link": float(t_val),
                "precision": float(pw.precision),
                "recall": float(pw.recall),
                "f1": float(pw.f1),
                "expected_cost": float(expected_cost),
                "false_merge_clusters": int(c_metrics.false_merge_clusters),
                "doppelganger_false_merge_rate": float(
                    c_metrics.doppelganger_false_merge_rate
                ),
                "dedup_reach": int(dedup_reach),
                "true_reach": int(true_person_count),
                "naive_reach": int(naive_records_count),
                "review_queue_size": int(q_size),
                "variant": variant_name,
            }
        )

    return rows


def _build_raw_clusters_by_threshold(
    pairs_df: pd.DataFrame,
    all_record_ids: Sequence[str],
    t_link_values: Sequence[float],
) -> pd.DataFrame:
    """Precompute live union-find (connected components) on raw candidate edges."""
    dfs: list[pd.DataFrame] = []
    sorted_ids = sorted(all_record_ids)

    for t_val in t_link_values:
        sub_pairs = pairs_df[pairs_df["match_weight"] >= t_val]
        G = nx.Graph()
        G.add_nodes_from(sorted_ids)

        for _, row in sub_pairs.iterrows():
            u = str(row["record_id_l"])
            v = str(row["record_id_r"])
            if u != v:
                G.add_edge(u, v)

        comp_rows: list[dict[str, Any]] = []
        for comp_idx, comp in enumerate(nx.connected_components(G)):
            c_id = f"raw_{comp_idx}"
            for r in comp:
                comp_rows.append(
                    {"record_id": r, "cluster_id": c_id, "t_link": float(t_val)}
                )

        dfs.append(pd.DataFrame(comp_rows))

    return pd.concat(dfs, ignore_index=True)


def build_eval_export_datasets(
    run_data_dir: Path,
    clusters_by_thresh_df: pd.DataFrame,
    eval_out_dir: Path,
    clusters_by_thresh_noconstraint_df: Optional[pd.DataFrame] = None,
    pairs_df: Optional[pd.DataFrame] = None,
    resolution_logs_by_thresh: Optional[dict[float, pd.DataFrame]] = None,
    resolution_logs_noconstraint_by_thresh: Optional[dict[float, pd.DataFrame]] = None,
) -> None:
    """Precompute evaluation files (threshold table and record labels) for web UI."""
    eval_out_dir.mkdir(parents=True, exist_ok=True)

    truth_records_path = run_data_dir / "truth" / "record_truth.parquet"
    truth_pairs_path = run_data_dir / "truth" / "true_pairs.parquet"
    if not truth_records_path.exists() or not truth_pairs_path.exists():
        raise FileNotFoundError("Truth records or true pairs missing for eval export.")

    truth_records_df = pd.read_parquet(truth_records_path)
    truth_pairs_df = pd.read_parquet(truth_pairs_path)
    doppel_pairs_path = run_data_dir / "truth" / "doppelganger_person_pairs.parquet"
    doppel_pairs_df = (
        pd.read_parquet(doppel_pairs_path) if doppel_pairs_path.exists() else None
    )

    record_person_map = dict(
        zip(
            truth_records_df["record_id"].astype(str),
            truth_records_df["person_id"].astype(str),
        )
    )
    total_true_pairs = len(truth_pairs_df)
    true_person_count = truth_records_df["person_id"].nunique()
    naive_records_count = len(truth_records_df)

    # 1. Precompute eval threshold table across variants
    threshold_eval_rows: list[dict[str, Any]] = []

    # Variant A: constraint (default champion resolution)
    constraint_rows = _evaluate_variant_clusters(
        clusters_df=clusters_by_thresh_df,
        variant_name="constraint",
        truth_records_df=truth_records_df,
        total_true_pairs=total_true_pairs,
        true_person_count=true_person_count,
        naive_records_count=naive_records_count,
        record_person_map=record_person_map,
        doppel_pairs_df=doppel_pairs_df,
        pairs_df=pairs_df,
        resolution_logs_by_thresh=resolution_logs_by_thresh,
    )
    threshold_eval_rows.extend(constraint_rows)

    # Variant B: no_constraint (counterfactual with listed_as_other_member disabled)
    if clusters_by_thresh_noconstraint_df is not None:
        noconstraint_rows = _evaluate_variant_clusters(
            clusters_df=clusters_by_thresh_noconstraint_df,
            variant_name="no_constraint",
            truth_records_df=truth_records_df,
            total_true_pairs=total_true_pairs,
            true_person_count=true_person_count,
            naive_records_count=naive_records_count,
            record_person_map=record_person_map,
            doppel_pairs_df=doppel_pairs_df,
            pairs_df=pairs_df,
            resolution_logs_by_thresh=resolution_logs_noconstraint_by_thresh,
        )
        threshold_eval_rows.extend(noconstraint_rows)

    # Variant C: raw (live union-find over pairs edges without resolution)
    if pairs_df is not None:
        all_ids = list(truth_records_df["record_id"].astype(str).unique())
        t_values = sorted(clusters_by_thresh_df["t_link"].unique())
        raw_clusters_df = _build_raw_clusters_by_threshold(
            pairs_df=pairs_df,
            all_record_ids=all_ids,
            t_link_values=t_values,
        )
        raw_rows = _evaluate_variant_clusters(
            clusters_df=raw_clusters_df,
            variant_name="raw",
            truth_records_df=truth_records_df,
            total_true_pairs=total_true_pairs,
            true_person_count=true_person_count,
            naive_records_count=naive_records_count,
            record_person_map=record_person_map,
            doppel_pairs_df=doppel_pairs_df,
            pairs_df=pairs_df,
            resolution_logs_by_thresh=None,
        )
        threshold_eval_rows.extend(raw_rows)

    threshold_table_df = pd.DataFrame(threshold_eval_rows)
    threshold_table_df.to_parquet(eval_out_dir / "threshold_table.parquet", index=False)

    # 2. Precompute eval record labels (ground-truth record_id, person_id, household_id)
    record_labels_df = truth_records_df[
        ["record_id", "person_id", "household_id"]
    ].copy()
    record_labels_df.to_parquet(eval_out_dir / "record_labels.parquet", index=False)
