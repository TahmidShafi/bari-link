"""Oracle clerical review simulation and review-curve evaluation.

Simulates an oracle reviewer resolving top-K uncertainty-ranked pairs, applies
must-link/cannot-link constraints, re-resolves clusters, and tracks performance curves.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

import pandas as pd

from barilink.resolve.graph import build_resolved_graph, evaluate_resolved_clusters
from barilink.resolve.review import build_review_queue


def simulate_clerical_review(
    run_name: str = "holdout_0",
    method: str = "splink_v1_resolved",
    base_data_dir: str = "data/generated",
    base_results_dir: str = "results",
    k_values: Sequence[int] = (0, 50, 100, 250, 500),
    write_md: bool = True,
) -> pd.DataFrame:
    """Run budgeted oracle clerical review simulation across K per 10k records."""
    run_dir = Path(base_data_dir) / run_name
    records_path = run_dir / "registry" / "records.parquet"
    truth_path = run_dir / "truth" / "record_truth.parquet"
    true_pairs_path = run_dir / "truth" / "true_pairs.parquet"
    doppel_path = run_dir / "truth" / "doppelganger_person_pairs.parquet"

    res_dir = Path(base_results_dir) / run_name / method
    splink_dir = Path(base_results_dir) / run_name / "splink_v1"
    preds_path = splink_dir / "predictions.parquet"
    clusters_path = res_dir / "clusters.parquet"
    res_log_path = res_dir / "resolution_log.parquet"
    sel_path = Path(base_results_dir) / method / "selected_thresholds.json"

    if not sel_path.exists():
        raise FileNotFoundError(f"Selected thresholds file not found at {sel_path}")
    if not records_path.exists():
        raise FileNotFoundError(f"Records parquet not found at {records_path}")
    if not truth_path.exists():
        raise FileNotFoundError(f"Record truth file not found at {truth_path}")
    if not preds_path.exists():
        raise FileNotFoundError(f"Predictions parquet not found at {preds_path}")

    # Load frozen thresholds
    with open(sel_path, "r", encoding="utf-8") as f:
        sel = json.load(f)
    t_link = float(sel["t_link"])
    t_bridge = float(sel["t_bridge"])

    # Load data
    records_df = pd.read_parquet(records_path)
    truth_df = pd.read_parquet(truth_path)
    true_pairs_df = pd.read_parquet(true_pairs_path)
    doppel_df = pd.read_parquet(doppel_path) if doppel_path.exists() else None
    preds_df = pd.read_parquet(preds_path)
    clusters_df = pd.read_parquet(clusters_path)
    res_log_df = pd.read_parquet(res_log_path) if res_log_path.exists() else None

    rec_person_map = dict(zip(truth_df["record_id"].astype(str), truth_df["person_id"].astype(str)))
    total_true_unique = truth_df["person_id"].nunique()
    n_records = len(records_df)

    # Build or load review queue
    queue_path = res_dir / "review_queue.parquet"
    if queue_path.exists():
        queue_df = pd.read_parquet(queue_path)
    else:
        queue_df = build_review_queue(
            predictions_df=preds_df,
            clusters_df=clusters_df,
            resolution_log_df=res_log_df,
            t_link=t_link,
            output_path=queue_path,
        )

    curve_rows = []
    prev_cost = None
    non_monotonic_notes = []

    for k in sorted(k_values):
        k_pairs = round(k * n_records / 10000)
        n_merges = 0
        n_splits = 0

        if k_pairs == 0:
            # Baseline unreviewed clusters
            metrics = evaluate_resolved_clusters(
                clusters_df=clusters_df,
                record_truth_df=truth_df,
                true_pairs_df=true_pairs_df,
                doppelganger_person_pairs_df=doppel_df,
            )
        else:
            reviewed_subset = queue_df.iloc[: min(k_pairs, len(queue_df))]
            must_links = []
            cannot_links = []

            for _, r in reviewed_subset.iterrows():
                u = str(r["record_id_l"])
                v = str(r["record_id_r"])
                p_u = rec_person_map.get(u)
                p_v = rec_person_map.get(v)

                if p_u is not None and p_v is not None and p_u == p_v:
                    must_links.append((u, v))
                    n_merges += 1
                else:
                    cannot_links.append((u, v))
                    n_splits += 1

            # Re-run resolution steps 2-4 with oracle constraints
            k_clusters_df, _ = build_resolved_graph(
                predictions_df=preds_df,
                records_df=records_df,
                t_link=t_link,
                t_bridge=t_bridge,
                must_link_pairs=must_links,
                cannot_link_pairs=cannot_links,
            )

            metrics = evaluate_resolved_clusters(
                clusters_df=k_clusters_df,
                record_truth_df=truth_df,
                true_pairs_df=true_pairs_df,
                doppelganger_person_pairs_df=doppel_df,
            )

        reach_err = (
            (metrics["dedup_reach"] - total_true_unique) / total_true_unique * 100.0
            if total_true_unique > 0
            else 0.0
        )
        cost = metrics["expected_cost"]

        if prev_cost is not None and cost > prev_cost:
            diff = cost - prev_cost
            note = (
                f"Non-monotonic cost increase at K={k}: cost rose from "
                f"{prev_cost:.1f} to {cost:.1f} (+{diff:.1f})."
            )
            non_monotonic_notes.append(note)
        prev_cost = cost

        curve_rows.append(
            {
                "k_per_10k": k,
                "pairs_reviewed": k_pairs,
                "merges": n_merges,
                "splits": n_splits,
                "cluster_precision": metrics["cluster_precision"],
                "cluster_recall": metrics["cluster_recall"],
                "cluster_f1": metrics["cluster_f1"],
                "expected_cost": cost,
                "false_merge_clusters": metrics["false_merge_clusters"],
                "dedup_reach": metrics["dedup_reach"],
                "reach_error_pct": reach_err,
            }
        )

    curve_df = pd.DataFrame(curve_rows)
    curve_df.to_parquet(res_dir / "review_curve.parquet", index=False)

    if write_md:
        charts_dir = res_dir / "charts"
        charts_dir.mkdir(parents=True, exist_ok=True)
        _export_review_chart_html(curve_df, charts_dir / "review_curve.html")

        md_path = res_dir / "review_summary.md"
        lines = [
            f"# Budgeted Clerical Review Summary: `{method}` on `{run_name}`",
            "",
            f"**Total Records ($N$)**: {n_records:,}  ",
            f"**Review Queue Size**: {len(queue_df):,} uncertainty-ranked pairs  ",
            f"**Operational Thresholds**: $t_{{\\text{{link}}}} = {t_link:.1f}$, "
            f"$t_{{\\text{{bridge}}}} = {t_bridge:.1f}$  ",
            "",
            "---",
            "",
            "## 1. Review Curve Table",
            "",
            (
                "| Budget ($K$ per 10k) | Pairs Reviewed | Merges (True Pairs) | "
                "Splits (False Pairs) | Cluster Precision | Cluster Recall | "
                "Cluster F1 | Expected Cost | Reach Error % |"
            ),
            "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]

        for _, r in curve_df.iterrows():
            lines.append(
                f"| **{int(r['k_per_10k'])}** | {int(r['pairs_reviewed']):,} | "
                f"{int(r['merges']):,} | {int(r['splits']):,} | "
                f"{r['cluster_precision']:.4f} | {r['cluster_recall']:.4f} | "
                f"{r['cluster_f1']:.4f} | {r['expected_cost']:.1f} | {r['reach_error_pct']:+.2f}% |"
            )

        lines.extend(
            [
                "",
                "---",
                "",
                "## 2. Review Dynamics & Monotonicity Analysis",
            ]
        )

        if non_monotonic_notes:
            lines.append("### Observed Non-Monotonic Steps:")
            for n in non_monotonic_notes:
                lines.append(f"- {n}")
            lines.append(
                "\n*Analysis*: Transitive closure on oracle must-link constraints can occasionally "
                "bridge weak multi-edge components prior to cannot-link pruning, momentarily "
                "increasing cluster false merges before higher review budgets resolve ambiguities."
            )
        else:
            lines.append(
                "Expected operational cost decreased monotonically across all simulated "
                "review budgets."
            )

        lines.extend(
            [
                "",
                "### Efficiency Insights:",
                (
                    f"- Prioritising cut edges ({len(queue_df[queue_df['is_cut_edge']]):,} pairs) "
                    f"and boundary pairs ($|w - t_{{\\text{{link}}}}| \\le 6.0$) provides field "
                    "staff with high-yield clerical review targets."
                ),
                (
                    f"- At $K = 500$ pairs per 10k "
                    f"({round(500 * n_records / 10000)} pairs reviewed), "
                    f"cluster F1 reaches {curve_df.iloc[-1]['cluster_f1']:.4f} with expected cost "
                    f"reduced to {curve_df.iloc[-1]['expected_cost']:.1f}."
                ),
            ]
        )

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    return curve_df


def _export_review_chart_html(curve_df: pd.DataFrame, out_html: Path) -> None:
    """Generate standalone interactive HTML chart showing expected cost and F1 vs review budget K."""  # noqa: E501
    records_json = curve_df.to_json(orient="records")

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Clerical Review Performance Curve</title>
  <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      margin: 24px;
      background: #fafafa;
    }}
    h1 {{ font-size: 20px; color: #111; margin-bottom: 8px; }}
    .subtitle {{ color: #555; margin-bottom: 20px; font-size: 14px; }}
    #vis {{
      background: white;
      padding: 16px;
      border-radius: 8px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }}
  </style>
</head>
<body>
  <h1>Budgeted Clerical Review Performance Curve</h1>
  <div class="subtitle">
    Expected operational cost and Cluster F1 as a function of review budget K per 10,000 records.
  </div>
  <div id="vis"></div>

  <script>
    const data = {records_json};
    const spec = {{
      "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
      "data": {{ "values": data }},
      "width": 600,
      "height": 340,
      "encoding": {{
        "x": {{
          "field": "k_per_10k",
          "type": "quantitative",
          "title": "Review Budget K (pairs per 10k records)"
        }}
      }},
      "layer": [
        {{
          "mark": {{ "type": "line", "color": "#d95f02", "point": true }},
          "encoding": {{
            "y": {{
              "field": "expected_cost",
              "type": "quantitative",
              "title": "Expected Cost (Asymmetric 5:1)"
            }}
          }}
        }},
        {{
          "mark": {{ "type": "line", "color": "#1b9e77", "point": true, "strokeDash": [4, 4] }},
          "encoding": {{
            "y": {{
              "field": "cluster_f1",
              "type": "quantitative",
              "title": "Cluster F1",
              "axis": {{ "orient": "right" }}
            }}
          }}
        }}
      ],
      "resolve": {{ "scale": {{ "y": "independent" }} }}
    }};
    vegaEmbed('#vis', spec);
  </script>
</body>
</html>
"""
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html_content)
