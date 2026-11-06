"""Asymmetric cost calculation, clerical review load, and operational threshold selection."""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


def weight_to_prob(w: float) -> float:
    """Convert match weight (base-2 log-odds) to match probability."""
    if np.isposinf(w) or w >= 50.0:
        return 1.0
    if np.isneginf(w) or w <= -50.0:
        return 0.0
    return float(1.0 / (1.0 + 2.0 ** (-float(w))))


def prob_to_weight(p: float) -> float:
    """Convert match probability to match weight (base-2 log-odds)."""
    if p >= 1.0:
        return float("inf")
    if p <= 0.0:
        return float("-inf")
    p_clamped = min(max(float(p), 1e-15), 1.0 - 1e-15)
    return float(np.log2(p_clamped / (1.0 - p_clamped)))


@dataclass
class CostThresholdSelection:
    """Selected operational thresholds and evaluation parameters."""

    cost_false_merge: float
    cost_missed_duplicate: float
    t_cost: float
    t_p99: Optional[float]
    min_cost: float
    grid: str = "weight"
    t_cost_weight: float = 0.0
    t_cost_prob: float = 0.0
    t_p99_weight: Optional[float] = None
    t_p99_prob: Optional[float] = None
    t_cost_on_boundary: bool = False
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
    grid: str = "weight",
) -> CostThresholdSelection:
    """Select t_cost (argmin expected_cost) and t_p99 (monotonic precision >= 0.99 suffix).

    Args:
        sweep_df: DataFrame containing at least ['threshold', 'precision', 'expected_cost'].
        cost_false_merge: Penalty per false-merge cluster pair.
        cost_missed_duplicate: Penalty per missed duplicate pair.
        grid: 'weight' (match-weight grid) or 'probability' (probability grid).

    Returns:
        CostThresholdSelection with t_cost and t_p99 in both spaces.
    """
    col = (
        "threshold_weight"
        if (grid == "weight" and "threshold_weight" in sweep_df.columns)
        else "threshold"
    )
    sorted_df = sweep_df.sort_values(col, ascending=True).reset_index(drop=True)

    # 1. t_cost = argmin expected_cost (break ties by higher threshold)
    min_cost = sorted_df["expected_cost"].min()
    cost_matches = sorted_df[sorted_df["expected_cost"] == min_cost]
    best_row = cost_matches.iloc[-1]
    t_cost = float(best_row[col])

    if grid == "weight":
        t_cost_weight = t_cost
        t_cost_prob = float(best_row.get("threshold_probability", weight_to_prob(t_cost_weight)))
        t_cost_on_boundary = bool(
            np.isclose(t_cost_weight, -5.0, atol=1e-4) or np.isclose(t_cost_weight, 25.0, atol=1e-4)
        )
    else:
        t_cost_prob = t_cost
        t_cost_weight = float(best_row.get("threshold_weight", prob_to_weight(t_cost_prob)))
        t_cost_on_boundary = bool(
            np.isclose(t_cost_prob, 0.01, atol=1e-4) or np.isclose(t_cost_prob, 0.99, atol=1e-4)
        )

    if t_cost_on_boundary:
        warnings.warn(
            f"Selected t_cost ({t_cost}) lies on the grid boundary! "
            f"The true optimum may lie outside the current grid range.",
            UserWarning,
            stacklevel=2,
        )

    # 2. t_p99: lowest threshold t such that cluster precision >= 0.99 at t and all above
    desc_df = sorted_df.sort_values(col, ascending=False).reset_index(drop=True)
    t_p99: Optional[float] = None
    explanation: Optional[str] = None

    valid_t: list[float] = []
    for _, row in desc_df.iterrows():
        t = float(row[col])
        p = float(row["precision"])
        if p >= 0.99:
            valid_t.append(t)
        else:
            break

    t_p99_weight: Optional[float] = None
    t_p99_prob: Optional[float] = None

    if valid_t:
        t_p99 = min(valid_t)
        if grid == "weight":
            t_p99_weight = t_p99
            t_p99_prob = weight_to_prob(t_p99_weight)
        else:
            t_p99_prob = t_p99
            t_p99_weight = prob_to_weight(t_p99_prob)
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
        grid=grid,
        t_cost_weight=t_cost_weight,
        t_cost_prob=t_cost_prob,
        t_p99_weight=t_p99_weight,
        t_p99_prob=t_p99_prob,
        t_cost_on_boundary=t_cost_on_boundary,
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
