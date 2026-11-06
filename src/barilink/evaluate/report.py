"""Evaluation orchestrator: threshold sweep, Dev/Holdout protocol, and artifact persistence."""

import hashlib
import json
from pathlib import Path
from typing import Any, Optional, Sequence

import numpy as np
import pandas as pd

from barilink.evaluate.clusters import UnionFind
from barilink.evaluate.contracts import validate_predictions
from barilink.evaluate.costs import (
    compute_clerical_review_load,
    compute_expected_cost,
    select_thresholds,
)
from barilink.evaluate.pairwise import (
    compute_pairwise_metrics_from_counts,
    evaluate_blocking,
)
from barilink.evaluate.reach import ReachSummary, compute_reach
from barilink.evaluate.strata import compute_strata_breakdowns


def run_threshold_sweep(
    predictions_df: pd.DataFrame,
    record_ids: Sequence[str],
    record_truth_df: pd.DataFrame,
    true_pairs_df: pd.DataFrame,
    doppelganger_person_pairs_df: Optional[pd.DataFrame] = None,
    cost_false_merge: float = 5.0,
    cost_missed_duplicate: float = 1.0,
    review_threshold_low: float = 0.5,
) -> tuple[pd.DataFrame, dict[float, UnionFind]]:
    """Run incremental Union-Find threshold sweep from 0.01 to 0.99.

    Args:
        predictions_df: Validated predictions DataFrame.
        record_ids: Full universe of record IDs.
        record_truth_df: Ground truth record metadata (record_id -> person_id).
        true_pairs_df: Ground truth true pairs (record_id_1, record_id_2).
        doppelganger_person_pairs_df: Doppelganger person pairs.
        cost_false_merge: Penalty c_fm.
        cost_missed_duplicate: Penalty c_md.
        review_threshold_low: Lower bound for clerical review load.

    Returns:
        Tuple of (sweep_df, snapshot_ufs).
    """
    total_records = len(record_ids)
    record_person_map = dict(
        zip(
            record_truth_df["record_id"].astype(str),
            record_truth_df["person_id"].astype(str),
        )
    )
    person_total_counts = dict(record_truth_df["person_id"].astype(str).value_counts())
    total_true_unique = record_truth_df["person_id"].nunique()

    # Ground truth true pairs set
    true_pairs_set: set[tuple[str, str]] = set()
    for _, r in true_pairs_df.iterrows():
        r1, r2 = str(r["record_id_1"]), str(r["record_id_2"])
        true_pairs_set.add((min(r1, r2), max(r1, r2)))
    total_true_pairs = len(true_pairs_set)

    # Doppelganger person pairs list
    doppel_pairs: list[tuple[str, str]] = []
    if doppelganger_person_pairs_df is not None and not doppelganger_person_pairs_df.empty:
        for _, r in doppelganger_person_pairs_df.iterrows():
            doppel_pairs.append((str(r["person_id_1"]), str(r["person_id_2"])))

    # Sort scored predictions by probability descending
    if not predictions_df.empty:
        sorted_preds = predictions_df.sort_values("match_probability", ascending=False).copy()
    else:
        sorted_preds = pd.DataFrame(columns=["record_id_l", "record_id_r", "match_probability"])

    # Thresholds: 0.99 down to 0.01 in steps of 0.01
    thresholds = [round(t * 0.01, 2) for t in range(99, 0, -1)]

    uf = UnionFind(
        record_ids=record_ids,
        record_person_map=record_person_map,
        person_total_counts=person_total_counts,
    )

    pred_idx = 0
    num_preds = len(sorted_preds)

    # Track edge-level matches
    edge_tp = 0
    edge_fp = 0

    rows: list[dict[str, Any]] = []
    snapshot_ufs: dict[float, UnionFind] = {}

    for t in thresholds:
        # Union all edges where match_probability >= t
        while pred_idx < num_preds and sorted_preds.iloc[pred_idx]["match_probability"] >= t:
            row = sorted_preds.iloc[pred_idx]
            u = str(row["record_id_l"])
            v = str(row["record_id_r"])
            uf.union(u, v)

            # Edge level
            pair = (min(u, v), max(u, v))
            if pair in true_pairs_set:
                edge_tp += 1
            else:
                edge_fp += 1
            pred_idx += 1

        # Query metrics at threshold t
        c_metrics = uf.compute_metrics(
            total_records=total_records,
            doppelganger_person_pairs=doppel_pairs,
        )

        pw = compute_pairwise_metrics_from_counts(
            tp=uf.cluster_tp,
            fp=uf.cluster_fp,
            total_true_pairs=total_true_pairs,
            edge_tp=edge_tp,
            edge_fp=edge_fp,
        )

        exp_cost = compute_expected_cost(
            fp=pw.fp,
            fn=pw.fn,
            cost_false_merge=cost_false_merge,
            cost_missed_duplicate=cost_missed_duplicate,
        )

        # Clerical review pairs with review_threshold_low <= p < 1.0 (or t_p99)
        rev_count = compute_clerical_review_load(
            predictions_df=predictions_df,
            total_records=total_records,
            t_low=review_threshold_low,
            t_high=1.0,
        )

        reach_err_pct = (
            ((c_metrics.dedup_reach - total_true_unique) / total_true_unique) * 100.0
            if total_true_unique > 0
            else 0.0
        )

        rows.append(
            {
                "threshold": t,
                "tp": pw.tp,
                "fp": pw.fp,
                "fn": pw.fn,
                "precision": pw.precision,
                "recall": pw.recall,
                "f1": pw.f1,
                "edge_tp": pw.edge_tp,
                "edge_fp": pw.edge_fp,
                "edge_fn": pw.edge_fn,
                "edge_precision": pw.edge_precision,
                "edge_recall": pw.edge_recall,
                "edge_f1": pw.edge_f1,
                "bcubed_precision": c_metrics.bcubed_precision,
                "bcubed_recall": c_metrics.bcubed_recall,
                "bcubed_f1": c_metrics.bcubed_f1,
                "false_merge_clusters": c_metrics.false_merge_clusters,
                "false_merged_records": c_metrics.false_merged_records,
                "split_persons": c_metrics.split_persons,
                "doppelganger_false_merge_rate": c_metrics.doppelganger_false_merge_rate,
                "review_pairs_per_10k": rev_count,
                "expected_cost": exp_cost,
                "dedup_reach": c_metrics.dedup_reach,
                "reach_error_pct": reach_err_pct,
            }
        )

    sweep_df = pd.DataFrame(rows).sort_values("threshold").reset_index(drop=True)
    return sweep_df, snapshot_ufs


def generate_evaluation_report(
    method_name: str,
    run_name: str,
    mode: str,
    predictions_df: pd.DataFrame,
    candidate_pair_count: int,
    base_data_dir: str | Path = "data/generated",
    base_results_dir: str | Path = "results",
    config: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Execute complete evaluation, persist metrics, and format human-readable report.

    Args:
        method_name: Name of the linkage method (e.g. exact, phone, exact_or_phone).
        run_name: Run folder name (e.g. demo, holdout).
        mode: Either 'select' (dev run) or 'report' (holdout run).
        predictions_df: Unvalidated or validated predictions DataFrame.
        candidate_pair_count: Number of candidate pairs compared.
        base_data_dir: Base directory holding generated runs.
        base_results_dir: Base directory holding results.
        config: Optional configuration dict.
    """
    config = config or {}
    eval_cfg = config.get("evaluation", {})
    cost_fm = float(eval_cfg.get("cost_false_merge", 5.0))
    cost_md = float(eval_cfg.get("cost_missed_duplicate", 1.0))
    review_low = float(eval_cfg.get("review_threshold_low", 0.5))

    run_dir = Path(base_data_dir) / run_name
    reg_dir = run_dir / "registry"
    truth_dir = run_dir / "truth"
    manifest_path = run_dir / "manifest.json"

    # Load manifest and check role
    role = "dev"
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
            role = manifest_data.get("role", "dev")

    if mode == "select" and role == "holdout":
        raise ValueError(
            f"Cannot run evaluate in 'select' mode on run '{run_name}' with role 'holdout'. "
            "Threshold selection is only permitted on development runs."
        )

    # Load data
    records_df = pd.read_parquet(reg_dir / "records.parquet")
    record_truth_df = pd.read_parquet(truth_dir / "record_truth.parquet")
    true_pairs_df = pd.read_parquet(truth_dir / "true_pairs.parquet")
    doppel_df = pd.read_parquet(truth_dir / "doppelganger_person_pairs.parquet")
    corr_log_df = pd.read_parquet(truth_dir / "corruption_log.parquet")

    # Validate predictions contract
    clean_preds_df = validate_predictions(
        predictions_df=predictions_df,
        records_df=records_df,
        candidate_pair_count=candidate_pair_count,
    )

    record_ids = records_df["record_id"].astype(str).tolist()

    # Blocking metrics
    true_pairs_set = {
        (
            min(str(r["record_id_1"]), str(r["record_id_2"])),
            max(str(r["record_id_1"]), str(r["record_id_2"])),
        )
        for _, r in true_pairs_df.iterrows()
    }
    cand_true_count = 0
    if not clean_preds_df.empty:
        for _, r in clean_preds_df.iterrows():
            p = (
                min(str(r["record_id_l"]), str(r["record_id_r"])),
                max(str(r["record_id_l"]), str(r["record_id_r"])),
            )
            if p in true_pairs_set:
                cand_true_count += 1

    blocking_metrics = evaluate_blocking(
        candidate_pairs=candidate_pair_count,
        total_records=len(record_ids),
        candidate_true_pairs=cand_true_count,
        total_true_pairs=len(true_pairs_set),
    )

    # Incremental threshold sweep
    sweep_df, _ = run_threshold_sweep(
        predictions_df=clean_preds_df,
        record_ids=record_ids,
        record_truth_df=record_truth_df,
        true_pairs_df=true_pairs_df,
        doppelganger_person_pairs_df=doppel_df,
        cost_false_merge=cost_fm,
        cost_missed_duplicate=cost_md,
        review_threshold_low=review_low,
    )

    results_base = Path(base_results_dir)
    method_select_file = results_base / method_name / "selected_thresholds.json"
    target_out_dir = results_base / run_name / method_name
    target_out_dir.mkdir(parents=True, exist_ok=True)

    threshold_source_run = run_name
    threshold_sha256 = ""

    if mode == "select":
        selection = select_thresholds(
            sweep_df, cost_false_merge=cost_fm, cost_missed_duplicate=cost_md
        )
        t_cost = selection.t_cost
        t_p99 = selection.t_p99

        sel_dict = {
            "method": method_name,
            "dev_run": run_name,
            "t_cost": t_cost,
            "t_p99": t_p99,
            "min_cost": selection.min_cost,
            "t_p99_explanation": selection.t_p99_explanation,
        }
        method_select_file.parent.mkdir(parents=True, exist_ok=True)
        sel_json_str = json.dumps(sel_dict, indent=2)
        with open(method_select_file, "w", encoding="utf-8") as f:
            f.write(sel_json_str)
        threshold_sha256 = hashlib.sha256(sel_json_str.encode("utf-8")).hexdigest()
    else:  # mode == "report"
        if not method_select_file.exists():
            raise FileNotFoundError(
                f"Selected thresholds file not found at {method_select_file.resolve()}. "
                "You must run evaluate in 'select' mode on dev run before reporting on holdout."
            )
        with open(method_select_file, "r", encoding="utf-8") as f:
            raw_sel = f.read()
            sel_dict = json.loads(raw_sel)
            threshold_sha256 = hashlib.sha256(raw_sel.encode("utf-8")).hexdigest()

        threshold_source_run = sel_dict.get("dev_run", "unknown")
        t_cost = float(sel_dict["t_cost"])
        t_p99 = float(sel_dict["t_p99"]) if sel_dict.get("t_p99") is not None else None

    # Retrieve metrics at operational threshold t_cost
    t_row = sweep_df[np.isclose(sweep_df["threshold"], t_cost)].iloc[0]

    # Build operational clusters at t_cost
    uf_cost = UnionFind(record_ids)
    above_cost = clean_preds_df[clean_preds_df["match_probability"] >= t_cost]
    for _, r in above_cost.iterrows():
        uf_cost.union(str(r["record_id_l"]), str(r["record_id_r"]))

    cost_clusters_df = pd.DataFrame(
        [{"record_id": rid, "cluster_id": uf_cost.find(rid)} for rid in record_ids]
    )

    # Reach summary at t_cost
    reach_summary = compute_reach(cost_clusters_df, record_truth_df)

    # Strata breakdown at t_cost
    strata_df = compute_strata_breakdowns(
        clusters_df=cost_clusters_df,
        record_truth_df=record_truth_df,
        true_pairs_df=true_pairs_df,
        corruption_log_df=corr_log_df,
        predictions_df=clean_preds_df,
        threshold=t_cost,
    )

    # Construct final metrics dictionary
    metrics: dict[str, Any] = {
        "schema_version": "1.0",
        "method": method_name,
        "run_name": run_name,
        "run_role": role,
        "mode": mode,
        "thresholds_source_run": threshold_source_run,
        "thresholds_sha256": threshold_sha256,
        "operational_thresholds": {
            "t_cost": t_cost,
            "t_p99": t_p99,
        },
        "blocking": {
            "candidate_pairs": blocking_metrics.candidate_pairs,
            "total_possible_pairs": blocking_metrics.total_possible_pairs,
            "reduction_ratio": blocking_metrics.reduction_ratio,
            "pair_completeness": blocking_metrics.pair_completeness,
            "pair_quality": blocking_metrics.pair_quality,
        },
        "headline_metrics_at_t_cost": {
            "cluster_precision": float(t_row["precision"]),
            "cluster_recall": float(t_row["recall"]),
            "cluster_f1": float(t_row["f1"]),
            "edge_precision": float(t_row["edge_precision"]),
            "edge_recall": float(t_row["edge_recall"]),
            "edge_f1": float(t_row["edge_f1"]),
            "bcubed_precision": float(t_row["bcubed_precision"]),
            "bcubed_recall": float(t_row["bcubed_recall"]),
            "bcubed_f1": float(t_row["bcubed_f1"]),
            "false_merge_clusters": int(t_row["false_merge_clusters"]),
            "false_merged_records": int(t_row["false_merged_records"]),
            "split_persons": int(t_row["split_persons"]),
            "doppelganger_false_merge_rate": float(t_row["doppelganger_false_merge_rate"]),
            "expected_cost": float(t_row["expected_cost"]),
            "review_pairs_per_10k": float(t_row["review_pairs_per_10k"]),
            "dedup_reach": int(t_row["dedup_reach"]),
            "reach_error_pct": float(t_row["reach_error_pct"]),
        },
        "reach": {
            "overall_dedup_reach": reach_summary.overall_dedup_reach,
            "overall_true_unique": reach_summary.overall_true_unique,
            "overall_naive_records": reach_summary.overall_naive_records,
            "overall_reach_error_pct": reach_summary.overall_reach_error_pct,
            "by_module": reach_summary.by_module,
        },
    }

    # Write output files
    # 1. metrics.json
    with open(target_out_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    # 2. threshold_table.parquet
    sweep_df.to_parquet(target_out_dir / "threshold_table.parquet", engine="pyarrow", index=False)

    # 3. strata.parquet
    strata_df.to_parquet(target_out_dir / "strata.parquet", engine="pyarrow", index=False)

    # 4. report.md
    sel_for_report = sel_dict if mode == "report" else None
    report_md = _build_report_markdown(metrics, reach_summary, sel_for_report)
    with open(target_out_dir / "report.md", "w", encoding="utf-8") as f:
        f.write(report_md)

    return metrics


def _build_report_markdown(
    metrics: dict[str, Any],
    reach_summary: ReachSummary,
    sel_dict: Optional[dict[str, Any]] = None,
) -> str:
    """Format human-readable evaluation report markdown."""
    m_head = metrics["headline_metrics_at_t_cost"]
    blk = metrics["blocking"]
    op = metrics["operational_thresholds"]

    t_p99_str = f"{op['t_p99']:.2f}" if op["t_p99"] is not None else "N/A"
    t_p99_note = ""
    if sel_dict and sel_dict.get("t_p99_explanation"):
        t_p99_note = f"\n> **Note on $t_{{p99}}$**: {sel_dict['t_p99_explanation']}\n"
    elif op["t_p99"] is None:
        t_p99_note = (
            "\n> **Note on $t_{p99}$**: "
            "No threshold achieved monotonic cluster precision >= 0.99.\n"
        )

    sha_note = ""
    if metrics["mode"] == "report":
        sha_note = (
            f"- **Threshold Source Run**: `{metrics['thresholds_source_run']}`\n"
            f"- **Thresholds SHA-256**: `{metrics['thresholds_sha256'][:16]}...`\n"
        )

    prec_row = (
        f"| **Precision** | **{m_head['cluster_precision']:.4f}** | "
        f"{m_head['edge_precision']:.4f} | {m_head['bcubed_precision']:.4f} |"
    )
    rec_row = (
        f"| **Recall** | **{m_head['cluster_recall']:.4f}** | "
        f"{m_head['edge_recall']:.4f} | {m_head['bcubed_recall']:.4f} |"
    )
    f1_row = (
        f"| **F1 Score** | **{m_head['cluster_f1']:.4f}** | "
        f"{m_head['edge_f1']:.4f} | **{m_head['bcubed_f1']:.4f}** |"
    )
    overall_row = (
        f"| **Overall Population** | **{reach_summary.overall_naive_records:,}** | "
        f"**{reach_summary.overall_dedup_reach:,}** | "
        f"**{reach_summary.overall_true_unique:,}** | "
        f"**{reach_summary.overall_reach_error_pct:+.2f}%** |"
    )

    md = f"""# Evaluation Report: {metrics['method']} ({metrics['run_name']})

- **Dataset Role**: `{metrics['run_role']}`
- **Evaluation Mode**: `{metrics['mode']}`
{sha_note}- **Selected $t_{{\\text{{cost}}}}$**: `{op['t_cost']:.2f}`
- **Selected $t_{{p99}}$**: `{t_p99_str}`
{t_p99_note}
## Headline Metrics at Operational Threshold ($t_{{\\text{{cost}}}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
{prec_row}
{rec_row}
{f1_row}

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **{m_head['doppelganger_false_merge_rate'] * 100.0:.2f}%** |
| **False-Merge Clusters** | {m_head['false_merge_clusters']} |
| **False-Merged Records (Minority)** | {m_head['false_merged_records']} |
| **Split Persons** | {m_head['split_persons']} |
| **Asymmetric Expected Cost ($5 \\cdot FP + 1 \\cdot FN$)** | {m_head['expected_cost']:,.1f} |
| **Clerical Review Load (per 10k records)** | {m_head['review_pairs_per_10k']:.1f} |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
{overall_row}
"""
    for mod, data in reach_summary.by_module.items():
        m_row = (
            f"| `{mod}` | {data['naive_record_count']:,} | {data['dedup_reach']:,} | "
            f"{data['true_unique_persons']:,} | {data['reach_error_pct']:+.2f}% |\n"
        )
        md += m_row

    md += f"""
## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: {blk['candidate_pairs']:,} / {blk['total_possible_pairs']:,}
- **Reduction Ratio**: {blk['reduction_ratio'] * 100.0:.4f}%
- **Pair Completeness (Recall Ceiling)**: {blk['pair_completeness'] * 100.0:.2f}%
- **Pair Quality**: {blk['pair_quality'] * 100.0:.2f}%
"""
    return md
