"""Uncertainty-ranked clerical review queue builder.

Strict segregation: This module reads only model-visible predictions and resolution logs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


def build_review_queue(
    predictions_df: pd.DataFrame,
    clusters_df: pd.DataFrame,
    resolution_log_df: Optional[pd.DataFrame] = None,
    t_link: float = 9.0,
    window_delta: float = 6.0,
    output_path: Optional[Path] = None,
) -> pd.DataFrame:
    """Build uncertainty-ranked review queue.

    Queue includes:
      - All cut edges from resolution_log.parquet (constraint cuts + bridge cuts).
      - Cross-cluster candidate pairs where t_link - 6.0 <= w <= t_link + 6.0.
      - Intra-cluster candidate pairs where w < t_link + 6.0 (kept links near threshold).

    Ranked by:
      1. Cut edges first (is_cut_edge == True).
      2. Ascending |match_weight - t_link| (maximum classification uncertainty).
      3. Deterministic record ID tiebreakers.
    """
    rec_cluster_map = dict(
        zip(clusters_df["record_id"].astype(str), clusters_df["cluster_id"].astype(str))
    )

    queue_items: dict[tuple[str, str], dict] = {}

    # 1. Add all cut edges
    if resolution_log_df is not None and not resolution_log_df.empty:
        for _, row in resolution_log_df.iterrows():
            u = str(row["record_id_l"])
            v = str(row["record_id_r"])
            u_s, v_s = min(u, v), max(u, v)
            w = float(row.get("weight", 0.0))
            queue_items[(u_s, v_s)] = {
                "record_id_l": u_s,
                "record_id_r": v_s,
                "match_weight": w,
                "is_cut_edge": True,
                "cut_action": str(row.get("action", "")),
                "cut_reason": str(row.get("reason", "")),
                "is_same_cluster": (rec_cluster_map.get(u_s) == rec_cluster_map.get(v_s)),
            }

    # 2. Add candidates from predictions near threshold
    if not predictions_df.empty:
        for _, row in predictions_df.iterrows():
            u = str(row["record_id_l"])
            v = str(row["record_id_r"])
            if u == v:
                continue
            u_s, v_s = min(u, v), max(u, v)
            w = float(row.get("match_weight", 0.0))

            c_u = rec_cluster_map.get(u_s)
            c_v = rec_cluster_map.get(v_s)
            is_same_cluster = c_u is not None and c_v is not None and c_u == c_v

            # Inclusion condition:
            # - Cross-cluster: within [t_link - 6, t_link + 6]
            # - Intra-cluster: w < t_link + 6
            include = False
            if not is_same_cluster and (t_link - window_delta <= w <= t_link + window_delta):
                include = True
            elif is_same_cluster and (w < t_link + window_delta):
                include = True

            if include:
                if (u_s, v_s) not in queue_items:
                    queue_items[(u_s, v_s)] = {
                        "record_id_l": u_s,
                        "record_id_r": v_s,
                        "match_weight": w,
                        "is_cut_edge": False,
                        "cut_action": "",
                        "cut_reason": "",
                        "is_same_cluster": is_same_cluster,
                    }

    queue_rows = list(queue_items.values())
    queue_df = pd.DataFrame(queue_rows)

    if queue_df.empty:
        queue_df = pd.DataFrame(
            columns=[
                "record_id_l",
                "record_id_r",
                "match_weight",
                "uncertainty",
                "is_cut_edge",
                "cut_action",
                "cut_reason",
                "is_same_cluster",
            ]
        )
    else:
        queue_df["uncertainty"] = (queue_df["match_weight"] - t_link).abs()
        # Sort: is_cut_edge descending (True first), then uncertainty ascending, then IDs
        queue_df = queue_df.sort_values(
            by=["is_cut_edge", "uncertainty", "record_id_l", "record_id_r"],
            ascending=[False, True, True, True],
        ).reset_index(drop=True)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        queue_df.to_parquet(output_path, index=False)

    return queue_df
