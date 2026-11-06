"""Asymmetric cost calculation, clerical review load, and operational threshold selection."""

from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass
class CostThresholdSelection:
    """Selected operational thresholds and evaluation parameters."""

    cost_false_merge: float
    cost_missed_duplicate: float
    t_cost: float
    t_p99: Optional[float]
    min_cost: float
    t_p99_explanation: Optional[str] = None


def compute_expected_cost(
    fp: int,
    fn: int,
    cost_false_merge: float = 5.0,
    cost_missed_duplicate: float = 1.0,
) -> float:
    """Compute asymmetric expected cost = c_fm * FP + c_md * FN."""
    return (cost_false_merge * fp) + (cost_missed_duplicate * fn)


def select_thresholds(
    sweep_df: pd.DataFrame,
    cost_false_merge: float = 5.0,
    cost_missed_duplicate: float = 1.0,
) -> CostThresholdSelection:
    """Select t_cost (argmin expected_cost) and t_p99 (monotonic precision >= 0.99 suffix).

    Args:
        sweep_df: DataFrame containing at least ['threshold', 'precision', 'expected_cost'].
        cost_false_merge: Penalty per false-merge cluster pair.
        cost_missed_duplicate: Penalty per missed duplicate pair.

    Returns:
        CostThresholdSelection with t_cost and t_p99.
    """
    sorted_df = sweep_df.sort_values("threshold", ascending=True).reset_index(drop=True)

    # 1. t_cost = argmin expected_cost (break ties by higher threshold)
    min_cost = sorted_df["expected_cost"].min()
    cost_matches = sorted_df[sorted_df["expected_cost"] == min_cost]
    t_cost = float(cost_matches.iloc[-1]["threshold"])

    # 2. t_p99: lowest threshold t such that cluster precision >= 0.99
    # at t AND every threshold above t.
    # Check descending from highest threshold
    desc_df = sorted_df.sort_values("threshold", ascending=False).reset_index(drop=True)
    t_p99: Optional[float] = None
    explanation: Optional[str] = None

    valid_t: list[float] = []
    for _, row in desc_df.iterrows():
        t = float(row["threshold"])
        p = float(row["precision"])
        if p >= 0.99:
            valid_t.append(t)
        else:
            # Monotonicity broken below this threshold
            break

    if valid_t:
        t_p99 = min(valid_t)
    else:
        max_p = sorted_df["precision"].max()
        explanation = (
            f"No threshold achieves cluster-level precision >= 0.99 (maximum observed: {max_p:.4f})"
        )

    return CostThresholdSelection(
        cost_false_merge=cost_false_merge,
        cost_missed_duplicate=cost_missed_duplicate,
        t_cost=t_cost,
        t_p99=t_p99,
        min_cost=float(min_cost),
        t_p99_explanation=explanation,
    )


def compute_clerical_review_load(
    predictions_df: pd.DataFrame,
    total_records: int,
    t_low: float = 0.5,
    t_high: Optional[float] = None,
) -> float:
    """Compute clerical review load (pairs with t_low <= p < t_high per 10,000 records).

    Args:
        predictions_df: DataFrame with match_probability.
        total_records: Total record universe N in the registry.
        t_low: Lower bound of review window.
        t_high: Upper bound of review window (defaults to 1.0 if None).

    Returns:
        Review pairs per 10,000 records.
    """
    if total_records == 0 or predictions_df.empty:
        return 0.0

    upper = 1.0 if t_high is None else t_high
    probs = predictions_df["match_probability"]
    count = int(((probs >= t_low) & (probs < upper)).sum())

    return (count / total_records) * 10_000.0
