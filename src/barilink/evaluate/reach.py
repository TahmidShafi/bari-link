"""Deduplicated reach vs true beneficiary reach and naive record counts."""

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class ReachSummary:
    """Summary of overall and per-module beneficiary reach."""

    overall_dedup_reach: int
    overall_true_unique: int
    overall_naive_records: int
    overall_reach_error_pct: float
    by_module: dict[str, dict[str, Any]]


def compute_reach(
    clusters_df: pd.DataFrame,
    record_truth_df: pd.DataFrame,
) -> ReachSummary:
    """Compute deduplicated beneficiary reach overall and per module.

    Args:
        clusters_df: DataFrame with record_id, cluster_id.
        record_truth_df: DataFrame with record_id, person_id, source_module.

    Returns:
        ReachSummary with overall and per-module reach figures and error percentages.
    """
    merged = clusters_df.merge(
        record_truth_df[["record_id", "person_id", "source_module"]],
        on="record_id",
        how="inner",
    )

    overall_dedup = int(merged["cluster_id"].nunique())
    overall_true = int(merged["person_id"].nunique())
    overall_naive = len(merged)

    overall_error_pct = (
        ((overall_dedup - overall_true) / overall_true) * 100.0 if overall_true > 0 else 0.0
    )

    by_module: dict[str, dict[str, Any]] = {}
    for mod, mod_df in merged.groupby("source_module"):
        mod_dedup = int(mod_df["cluster_id"].nunique())
        mod_true = int(mod_df["person_id"].nunique())
        mod_naive = len(mod_df)
        mod_err = ((mod_dedup - mod_true) / mod_true) * 100.0 if mod_true > 0 else 0.0

        by_module[str(mod)] = {
            "dedup_reach": mod_dedup,
            "true_unique_persons": mod_true,
            "naive_record_count": mod_naive,
            "reach_error_pct": mod_err,
        }

    return ReachSummary(
        overall_dedup_reach=overall_dedup,
        overall_true_unique=overall_true,
        overall_naive_records=overall_naive,
        overall_reach_error_pct=overall_error_pct,
        by_module=by_module,
    )
