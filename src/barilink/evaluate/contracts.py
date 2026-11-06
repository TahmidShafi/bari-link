"""Input schemas and validation contracts for linkage methods."""

from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np
import pandas as pd


@dataclass
class PairwisePredictions:
    """Pairwise match predictions produced by a record linkage method."""

    predictions_df: pd.DataFrame
    candidate_pair_count: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ClusterPredictions:
    """Cluster assignments produced by a record linkage method."""

    clusters_df: pd.DataFrame
    metadata: dict[str, Any] = field(default_factory=dict)


def validate_predictions(
    predictions_df: pd.DataFrame,
    records_df: pd.DataFrame,
    candidate_pair_count: Optional[int] = None,
) -> pd.DataFrame:
    """Validate and normalise pairwise match predictions.

    Args:
        predictions_df: DataFrame with record_id_l, record_id_r, match_probability.
        records_df: DataFrame containing the universe of valid record_ids.
        candidate_pair_count: Optional number of candidate pairs evaluated.

    Returns:
        Normalised DataFrame with record_id_l < record_id_r and duplicates removed.

    Raises:
        ValueError: If required columns are missing, probabilities out of bounds,
                    self-pairs exist, unknown record_ids appear, or candidate count is negative.
    """
    required_cols = {"record_id_l", "record_id_r", "match_probability"}
    if not required_cols.issubset(predictions_df.columns):
        missing = required_cols - set(predictions_df.columns)
        err = f"Predictions missing required columns: {sorted(missing)}"
        raise ValueError(err)

    if candidate_pair_count is not None and candidate_pair_count < 0:
        err = f"candidate_pair_count must be non-negative, got {candidate_pair_count}"
        raise ValueError(err)

    if len(predictions_df) == 0:
        res = predictions_df.copy()
        if "record_id_l" in res and "record_id_r" in res:
            res["record_id_l"] = res["record_id_l"].astype(str)
            res["record_id_r"] = res["record_id_r"].astype(str)
        return res

    df = predictions_df.copy()

    # Normalise unordered pairs so record_id_l < record_id_r
    swap_mask = df["record_id_l"] > df["record_id_r"]
    if swap_mask.any():
        df.loc[swap_mask, ["record_id_l", "record_id_r"]] = (
            df.loc[swap_mask, ["record_id_r", "record_id_l"]].values
        )

    # Check for self-pairs
    self_pairs = df[df["record_id_l"] == df["record_id_r"]]
    if not self_pairs.empty:
        example = self_pairs.iloc[0]["record_id_l"]
        err = f"Self-pairs not allowed in predictions (e.g., {example} == {example})"
        raise ValueError(err)

    # Check match_probability range [0.0, 1.0]
    probs = df["match_probability"]
    if not np.issubdtype(probs.dtype, np.number):
        err = f"match_probability must be numeric, got dtype {probs.dtype}"
        raise ValueError(err)

    if probs.isna().any():
        raise ValueError("match_probability contains NaN values")

    if (probs < 0.0).any() or (probs > 1.0).any():
        invalid = df[(df["match_probability"] < 0.0) | (df["match_probability"] > 1.0)]
        val = invalid.iloc[0]["match_probability"]
        err = f"match_probability values must be in [0, 1], found invalid value: {val}"
        raise ValueError(err)

    # Validate that all record IDs exist in records_df
    valid_record_ids = set(records_df["record_id"].astype(str))
    pred_record_ids = set(df["record_id_l"].astype(str)).union(df["record_id_r"].astype(str))
    unknown_ids = pred_record_ids - valid_record_ids
    if unknown_ids:
        sample = list(unknown_ids)[:5]
        err = (
            f"Found {len(unknown_ids)} unknown record IDs in predictions "
            f"not in registry: {sample}"
        )
        raise ValueError(err)

    # Deduplicate pairs, keeping highest match_probability
    df = df.sort_values("match_probability", ascending=False).drop_duplicates(
        subset=["record_id_l", "record_id_r"], keep="first"
    )
    df = df.sort_values(["record_id_l", "record_id_r"]).reset_index(drop=True)
    return df


def validate_clusters(clusters_df: pd.DataFrame, records_df: pd.DataFrame) -> pd.DataFrame:
    """Validate cluster assignments.

    Args:
        clusters_df: DataFrame with columns record_id, cluster_id.
        records_df: DataFrame containing the universe of valid record_ids.

    Returns:
        Validated clusters DataFrame.

    Raises:
        ValueError: If columns missing, duplicate records, or record universe mismatch.
    """
    required_cols = {"record_id", "cluster_id"}
    if not required_cols.issubset(clusters_df.columns):
        missing = required_cols - set(clusters_df.columns)
        err = f"Clusters DataFrame missing required columns: {sorted(missing)}"
        raise ValueError(err)

    # Check duplicates
    if clusters_df["record_id"].duplicated().any():
        dup = clusters_df[clusters_df["record_id"].duplicated()].iloc[0]["record_id"]
        err = f"Duplicate record_id in clusters: {dup}"
        raise ValueError(err)

    # Check that all records from registry exist exactly once
    cluster_ids = set(clusters_df["record_id"].astype(str))
    registry_ids = set(records_df["record_id"].astype(str))

    missing_ids = registry_ids - cluster_ids
    if missing_ids:
        sample = list(missing_ids)[:5]
        err = f"{len(missing_ids)} records from registry missing in clusters: {sample}"
        raise ValueError(err)

    extra_ids = cluster_ids - registry_ids
    if extra_ids:
        sample = list(extra_ids)[:5]
        err = f"{len(extra_ids)} unknown record IDs in clusters not in registry: {sample}"
        raise ValueError(err)

    return clusters_df.copy()
