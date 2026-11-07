"""Pairwise evaluation metrics: cluster-level (headline), edge-level (diagnostic), and blocking."""

from dataclasses import dataclass

import pandas as pd


@dataclass
class PairwiseMetrics:
    """Pairwise metrics at a specific decision threshold."""

    # Cluster-level headline metrics
    tp: int
    fp: int
    fn: int
    precision: float
    recall: float
    f1: float

    # Edge-level diagnostic metrics
    edge_tp: int
    edge_fp: int
    edge_fn: int
    edge_precision: float
    edge_recall: float
    edge_f1: float


@dataclass
class BlockingMetrics:
    """Evaluation metrics for the candidate generation / blocking stage."""

    candidate_pairs: int
    total_possible_pairs: int
    reduction_ratio: float
    pair_completeness: float
    pair_quality: float


def evaluate_blocking(
    candidate_pairs: int,
    total_records: int,
    candidate_true_pairs: int,
    total_true_pairs: int,
) -> BlockingMetrics:
    """Compute reduction ratio, pair completeness, and pair quality.

    Args:
        candidate_pairs: Number of pairs retained after blocking.
        total_records: Total number of records N in the registry.
        candidate_true_pairs: Number of true match pairs present in the candidate set.
        total_true_pairs: Total ground-truth pairs in the dataset.
    """
    total_possible = (total_records * (total_records - 1)) // 2
    if total_possible > 0:
        reduction_ratio = 1.0 - (candidate_pairs / total_possible)
    else:
        reduction_ratio = 1.0

    pair_completeness = (candidate_true_pairs / total_true_pairs) if total_true_pairs > 0 else 1.0
    pair_quality = (candidate_true_pairs / candidate_pairs) if candidate_pairs > 0 else 0.0

    return BlockingMetrics(
        candidate_pairs=candidate_pairs,
        total_possible_pairs=total_possible,
        reduction_ratio=reduction_ratio,
        pair_completeness=pair_completeness,
        pair_quality=pair_quality,
    )


def compute_pairwise_metrics_from_counts(
    tp: int,
    fp: int,
    total_true_pairs: int,
    edge_tp: int,
    edge_fp: int,
) -> PairwiseMetrics:
    """Compute cluster-level and edge-level metrics from raw counts."""
    fn = max(0, total_true_pairs - tp)
    precision = (tp / (tp + fp)) if (tp + fp) > 0 else 1.0
    recall = (tp / total_true_pairs) if total_true_pairs > 0 else 1.0
    f1 = (2.0 * precision * recall) / (precision + recall) if (precision + recall) > 0.0 else 0.0

    edge_fn = max(0, total_true_pairs - edge_tp)
    edge_precision = (edge_tp / (edge_tp + edge_fp)) if (edge_tp + edge_fp) > 0 else 1.0
    edge_recall = (edge_tp / total_true_pairs) if total_true_pairs > 0 else 1.0
    edge_f1 = (
        (2.0 * edge_precision * edge_recall) / (edge_precision + edge_recall)
        if (edge_precision + edge_recall) > 0.0
        else 0.0
    )

    return PairwiseMetrics(
        tp=tp,
        fp=fp,
        fn=fn,
        precision=precision,
        recall=recall,
        f1=f1,
        edge_tp=edge_tp,
        edge_fp=edge_fp,
        edge_fn=edge_fn,
        edge_precision=edge_precision,
        edge_recall=edge_recall,
        edge_f1=edge_f1,
    )


def evaluate_pairwise(
    predictions_df: pd.DataFrame,
    true_pairs_set: set[tuple[str, str]],
    clusters_df: pd.DataFrame,
    record_person_map: dict[str, str],
    threshold: float = 0.5,
) -> PairwiseMetrics:
    """Evaluate pairwise metrics at threshold t for both cluster and edge levels.

    Args:
        predictions_df: Scored pairs with record_id_l, record_id_r, match_probability.
        true_pairs_set: Set of (record_id_1, record_id_2) with record_id_1 < record_id_2.
        clusters_df: DataFrame of record_id, cluster_id at threshold t.
        record_person_map: Map of record_id -> person_id.
        threshold: Decision threshold t.
    """
    total_true_pairs = len(true_pairs_set)

    # 1. Edge-level (diagnostic): scored pairs >= threshold
    above = predictions_df[predictions_df["match_probability"] >= threshold]
    edge_tp = 0
    edge_fp = 0
    for _, row in above.iterrows():
        pair = (
            min(str(row["record_id_l"]), str(row["record_id_r"])),
            max(str(row["record_id_l"]), str(row["record_id_r"])),
        )
        if pair in true_pairs_set:
            edge_tp += 1
        else:
            edge_fp += 1

    # 2. Cluster-level (headline): all pairs in same cluster
    cluster_records = clusters_df.groupby("cluster_id")["record_id"].apply(list)
    cluster_tp = 0
    cluster_fp = 0

    for _, rids in cluster_records.items():
        if len(rids) <= 1:
            continue
        p_counts: dict[str, int] = {}
        for rid in rids:
            p = record_person_map.get(str(rid))
            if p is not None:
                p_counts[p] = p_counts.get(p, 0) + 1

        c_size = len(rids)
        c_pairs = (c_size * (c_size - 1)) // 2
        c_true = sum((cnt * (cnt - 1)) // 2 for cnt in p_counts.values())
        c_false = c_pairs - c_true

        cluster_tp += c_true
        cluster_fp += c_false

    return compute_pairwise_metrics_from_counts(
        tp=cluster_tp,
        fp=cluster_fp,
        total_true_pairs=total_true_pairs,
        edge_tp=edge_tp,
        edge_fp=edge_fp,
    )
