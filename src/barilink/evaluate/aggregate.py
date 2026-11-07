"""Multi-holdout evaluation aggregation across seeds with Wilson 95% confidence interval."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional, Sequence

import numpy as np
import pandas as pd


def parse_runs_argument(runs_arg: Sequence[str] | str) -> list[str]:
    """Parse runs argument which can be a range like 'holdout_0..holdout_4' or a list of runs."""
    if isinstance(runs_arg, str):
        tokens = [runs_arg]
    else:
        tokens = list(runs_arg)

    parsed_runs: list[str] = []
    for tok in tokens:
        # Check for range syntax: e.g., holdout_0..holdout_4
        m = re.match(r"^([a-zA-Z0-9_\-]+)_(\d+)\.\.([a-zA-Z0-9_\-]+)_(\d+)$", tok)
        if m:
            prefix1, start_s, prefix2, end_s = m.groups()
            if prefix1 == prefix2:
                start_i = int(start_s)
                end_i = int(end_s)
                for i in range(start_i, end_i + 1):
                    parsed_runs.append(f"{prefix1}_{i}")
                continue
        # Check general range prefix..prefix
        m_simple = re.match(r"^(\d+)\.\.(\d+)$", tok)
        if m_simple:
            s_i, e_i = int(m_simple.group(1)), int(m_simple.group(2))
            for i in range(s_i, e_i + 1):
                parsed_runs.append(f"holdout_{i}")
            continue

        parsed_runs.append(tok)

    return parsed_runs


def compute_wilson_ci(k: int, n: int, confidence: float = 0.95) -> tuple[float, float, float]:
    """Compute Wilson score confidence interval.

    Returns:
        (p_hat, ci_low, ci_high)
    """
    if n <= 0:
        return 0.0, 0.0, 0.0
    p_hat = k / n
    z = 1.95996398454  # 95% critical value
    denom = 1.0 + (z**2) / n
    center = (p_hat + (z**2) / (2.0 * n)) / denom
    half_w = (z / denom) * np.sqrt((p_hat * (1.0 - p_hat) / n) + (z**2) / (4.0 * (n**2)))
    ci_low = max(0.0, center - half_w)
    ci_high = min(1.0, center + half_w)
    return p_hat, ci_low, ci_high


def aggregate_holdout_metrics(
    runs: Sequence[str] | str = "holdout_0..holdout_4",
    methods: Optional[Sequence[str]] = None,
    base_data_dir: str = "data/generated",
    base_results_dir: str = "results",
    update_comparison_md: bool = True,
) -> dict[str, dict]:
    """Aggregate evaluation metrics across multiple holdout runs."""
    run_list = parse_runs_argument(runs)
    if not run_list:
        raise ValueError("No valid runs provided for aggregation.")

    if methods is None:
        methods = ["no_link", "exact", "phone", "exact_or_phone", "splink_v1"]

    results: dict[str, dict] = {}

    for method in methods:
        results[method] = {
            "cluster_precision": [],
            "cluster_recall": [],
            "cluster_f1": [],
            "pair_completeness": [],
            "reach_error_pct": [],
            "review_pairs_per_10k": [],
            "doppel_merged": 0,
            "doppel_total": 0,
            "t_cost_weight": None,
            "t_cost_prob": None,
            "t_p99_weight": None,
            "t_p99_prob": None,
            "t_link": None,
            "t_bridge": None,
        }

        for run_name in run_list:
            res_dir = Path(base_results_dir) / run_name / method
            metrics_p = res_dir / "metrics.json"
            if not metrics_p.exists():
                continue

            with open(metrics_p, "r", encoding="utf-8") as f:
                m = json.load(f)

            h = m.get("headline_metrics_at_t_cost", {})
            op = m.get("operational_thresholds", {})
            blk = m.get("blocking", {})

            results[method]["cluster_precision"].append(h.get("cluster_precision", 0.0))
            results[method]["cluster_recall"].append(h.get("cluster_recall", 0.0))
            results[method]["cluster_f1"].append(h.get("cluster_f1", 0.0))
            results[method]["pair_completeness"].append(blk.get("pair_completeness", 0.0))
            results[method]["reach_error_pct"].append(h.get("reach_error_pct", 0.0))
            results[method]["review_pairs_per_10k"].append(h.get("review_pairs_per_10k", 0.0))

            if results[method]["t_cost_weight"] is None:
                results[method]["t_cost_weight"] = op.get("t_cost_weight")
                results[method]["t_cost_prob"] = op.get("t_cost_prob", op.get("t_cost"))
                results[method]["t_p99_weight"] = op.get("t_p99_weight")
                results[method]["t_p99_prob"] = op.get("t_p99_prob", op.get("t_p99"))
                results[method]["t_link"] = op.get("t_link")
                results[method]["t_bridge"] = op.get("t_bridge")

            # Doppelgangers
            truth_p = Path(base_data_dir) / run_name / "truth" / "doppelganger_person_pairs.parquet"
            if truth_p.exists():
                doppel_df = pd.read_parquet(truth_p)
                n_doppels = len(doppel_df)
                rate = h.get("doppelganger_false_merge_rate", 0.0)
                merged = round(rate * n_doppels)
                results[method]["doppel_merged"] += merged
                results[method]["doppel_total"] += n_doppels

    summary: dict[str, dict] = {}
    for method, vals in results.items():
        if not vals["cluster_precision"]:
            continue
        p_mean = float(np.mean(vals["cluster_precision"]))
        p_sd = (
            float(np.std(vals["cluster_precision"], ddof=1))
            if len(vals["cluster_precision"]) > 1
            else 0.0
        )
        r_mean = float(np.mean(vals["cluster_recall"]))
        r_sd = (
            float(np.std(vals["cluster_recall"], ddof=1))
            if len(vals["cluster_recall"]) > 1
            else 0.0
        )
        f1_mean = float(np.mean(vals["cluster_f1"]))
        f1_sd = float(np.std(vals["cluster_f1"], ddof=1)) if len(vals["cluster_f1"]) > 1 else 0.0
        pc_mean = float(np.mean(vals["pair_completeness"])) if vals["pair_completeness"] else 0.0
        reach_mean = float(np.mean(vals["reach_error_pct"]))
        reach_sd = (
            float(np.std(vals["reach_error_pct"], ddof=1))
            if len(vals["reach_error_pct"]) > 1
            else 0.0
        )
        rev_mean = float(np.mean(vals["review_pairs_per_10k"]))

        k = vals["doppel_merged"]
        n = vals["doppel_total"]
        p_hat, ci_low, ci_high = compute_wilson_ci(k, n)

        summary[method] = {
            "precision_mean": p_mean,
            "precision_sd": p_sd,
            "recall_mean": r_mean,
            "recall_sd": r_sd,
            "f1_mean": f1_mean,
            "f1_sd": f1_sd,
            "pair_completeness": pc_mean,
            "reach_error_mean": reach_mean,
            "reach_error_sd": reach_sd,
            "review_pairs_per_10k": rev_mean,
            "doppel_merged": k,
            "doppel_total": n,
            "doppel_rate": p_hat,
            "doppel_ci_low": ci_low,
            "doppel_ci_high": ci_high,
            "t_cost_weight": vals["t_cost_weight"],
            "t_cost_prob": vals["t_cost_prob"],
            "t_p99_weight": vals["t_p99_weight"],
            "t_p99_prob": vals["t_p99_prob"],
            "t_link": vals["t_link"],
            "t_bridge": vals["t_bridge"],
        }

    if update_comparison_md and summary:
        comp_md_path = Path(base_results_dir) / "holdout" / "baseline_comparison.md"
        comp_md_path.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            (
                "# Holdout Baseline Comparison Report: Probabilistic Linkage & "
                f"Resolution vs. Baselines ({len(run_list)}-Seed Uncertainty)"
            ),
            "",
            (
                "This benchmark evaluates the performance of probabilistic linkage and entity "
                f"resolution across {len(run_list)} independent holdout seeds "
                f"({', '.join(run_list)})."
            ),
            "",
            "---",
            "",
            "## 1. Multi-Seed Summary Comparison Table",
            "",
            (
                "| Method | Cluster Precision (mean ± sd) | Cluster Recall (mean ± sd) | "
                "Cluster F1 (mean ± sd) | Pair Completeness | "
                "Doppelganger FM Pooled Rate [Wilson 95% CI] | Reach Error % (mean ± sd) | "
                "Review Pairs per 10k | $t_{\\text{cost}}$ / Thresholds | $t_{\\text{p99}}$ |"
            ),
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]

        for method, s in summary.items():
            p_str = f"{s['precision_mean']:.4f} ± {s['precision_sd']:.4f}"
            r_str = f"{s['recall_mean']:.4f} ± {s['recall_sd']:.4f}"
            f1_str = f"{s['f1_mean']:.4f} ± {s['f1_sd']:.4f}"
            pc_str = (
                f"{s['pair_completeness'] * 100:.2f}%" if s["pair_completeness"] > 0 else "0.00%"
            )
            d_str = (
                f"{s['doppel_rate'] * 100:.2f}% "
                f"[{s['doppel_ci_low'] * 100:.2f}%, {s['doppel_ci_high'] * 100:.2f}%]"
            )
            reach_str = f"{s['reach_error_mean']:+.2f}% ± {s['reach_error_sd']:.2f}%"
            rev_str = f"{s['review_pairs_per_10k']:.1f}"

            if method == "splink_v1_resolved":
                t_str = (
                    f"$t_{{\\text{{link}}}}={s['t_link']:.1f}$ / "
                    f"$t_{{\\text{{bridge}}}}={s['t_bridge']:.1f}$"
                )
                tp99_str = "resolved"
            elif s["t_cost_weight"] is not None:
                t_str = f"{s['t_cost_weight']:.2f} / {s['t_cost_prob']:.6f}"
                tp99_str = (
                    f"{s['t_p99_weight']:.2f} / {s['t_p99_prob']:.6f}"
                    if s["t_p99_weight"] is not None
                    else "none"
                )
            else:
                t_str = "none"
                tp99_str = "none"

            lines.append(
                f"| `{method}` | {p_str} | {r_str} | {f1_str} | {pc_str} | "
                f"{d_str} | {reach_str} | {rev_str} | {t_str} | {tp99_str} |"
            )

        lines.extend(
            [
                "",
                (
                    "> Note: B-cubed is reported only in `metrics.json` because "
                    "singleton-heavy data inflate it (`no_link` scores about 0.86)."
                ),
                "",
            ]
        )

        with open(comp_md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    return summary
