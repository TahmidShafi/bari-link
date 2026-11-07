"""Connected components, graph clustering, and cluster-level entity resolution metrics."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Optional, Sequence

import pandas as pd


@dataclass
class ClusterMetrics:
    """Metrics evaluated at the cluster entity resolution level."""

    bcubed_precision: float
    bcubed_recall: float
    bcubed_f1: float
    false_merge_clusters: int
    false_merged_records: int
    split_persons: int
    doppelganger_false_merge_rate: float
    dedup_reach: int


class UnionFind:
    """Disjoint Set Union (DSU) with path compression and incremental cluster accounting."""

    def __init__(
        self,
        record_ids: Sequence[str],
        record_person_map: Optional[dict[str, str]] = None,
        person_total_counts: Optional[dict[str, int]] = None,
    ) -> None:
        self.parent: dict[str, str] = {rid: rid for rid in record_ids}
        self.rank: dict[str, int] = {rid: 0 for rid in record_ids}
        self.size: dict[str, int] = {rid: 1 for rid in record_ids}

        # person_id -> count in component
        self.record_person_map = record_person_map or {}
        self.person_total_counts = person_total_counts or {}

        # Component person distributions: root -> Counter(person_id -> count)
        self.person_counts: dict[str, Counter[str]] = {}
        for rid in record_ids:
            p = self.record_person_map.get(rid)
            cnt = Counter()
            if p is not None:
                cnt[p] = 1
            self.person_counts[rid] = cnt

        # Incremental cluster-level pair counts
        self.cluster_tp: int = 0
        self.cluster_fp: int = 0

        # Roots set
        self.roots: set[str] = set(record_ids)

    def find(self, x: str) -> str:
        """Find root with path compression."""
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        curr = x
        while curr != root:
            nxt = self.parent[curr]
            self.parent[curr] = root
            curr = nxt
        return root

    def union(self, x: str, y: str) -> bool:
        """Merge components containing x and y.

        Returns:
            True if components were merged, False if already in same component.
        """
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x == root_y:
            return False

        # Ensure root_x has >= root_y rank for union-by-rank
        if self.rank[root_x] < self.rank[root_y]:
            root_x, root_y = root_y, root_x

        # Increment cluster-level pair counts
        size_x = self.size[root_x]
        size_y = self.size[root_y]
        new_pairs = size_x * size_y

        counts_x = self.person_counts[root_x]
        counts_y = self.person_counts[root_y]

        # Calculate new true pairs across components
        new_true = 0
        # Iterate over smaller Counter
        if len(counts_x) < len(counts_y):
            for p, c_x in counts_x.items():
                if p in counts_y:
                    new_true += c_x * counts_y[p]
        else:
            for p, c_y in counts_y.items():
                if p in counts_x:
                    new_true += c_y * counts_x[p]

        new_false = new_pairs - new_true
        self.cluster_tp += new_true
        self.cluster_fp += new_false

        # Merge trees
        self.parent[root_y] = root_x
        self.size[root_x] += size_y
        if self.rank[root_x] == self.rank[root_y]:
            self.rank[root_x] += 1

        # Small-to-large merge of Counters
        if len(counts_x) < len(counts_y):
            counts_y.update(counts_x)
            self.person_counts[root_x] = counts_y
        else:
            counts_x.update(counts_y)
            self.person_counts[root_x] = counts_x

        del self.person_counts[root_y]
        self.roots.remove(root_y)
        return True

    def get_components(self) -> dict[str, list[str]]:
        """Return mapping from root record_id to list of member record_ids."""
        comps: dict[str, list[str]] = defaultdict(list)
        for rid in self.parent:
            comps[self.find(rid)].append(rid)
        return comps

    def compute_metrics(
        self,
        total_records: int,
        doppelganger_person_pairs: Optional[Sequence[tuple[str, str]]] = None,
    ) -> ClusterMetrics:
        """Compute B-cubed, false merge, split persons, and doppelganger metrics."""
        if total_records == 0:
            return ClusterMetrics(
                bcubed_precision=1.0,
                bcubed_recall=1.0,
                bcubed_f1=1.0,
                false_merge_clusters=0,
                false_merged_records=0,
                split_persons=0,
                doppelganger_false_merge_rate=0.0,
                dedup_reach=0,
            )

        prec_sum = 0.0
        rec_sum = 0.0
        false_merge_clusters = 0
        false_merged_records = 0

        # Person -> set of cluster roots
        person_roots: dict[str, set[str]] = defaultdict(set)

        for root in self.roots:
            c_size = self.size[root]
            c_counts = self.person_counts[root]

            sum_sq = 0
            max_p_count = 0
            distinct_p_count = 0

            for p, count in c_counts.items():
                sum_sq += count * count
                if count > max_p_count:
                    max_p_count = count
                distinct_p_count += 1
                person_roots[p].add(root)

                total_p = self.person_total_counts.get(p, count)
                if total_p > 0:
                    rec_sum += (count * count) / total_p

            prec_sum += sum_sq / c_size

            if distinct_p_count > 1:
                false_merge_clusters += 1
                false_merged_records += c_size - max_p_count

        bcubed_p = prec_sum / total_records
        bcubed_r = rec_sum / total_records
        bcubed_f1 = (
            (2.0 * bcubed_p * bcubed_r) / (bcubed_p + bcubed_r)
            if (bcubed_p + bcubed_r) > 0.0
            else 0.0
        )

        split_persons = sum(1 for p, roots in person_roots.items() if len(roots) > 1)

        # Doppelganger false merge rate
        doppel_rate = 0.0
        if doppelganger_person_pairs and len(doppelganger_person_pairs) > 0:
            merged_doppels = 0
            for p1, p2 in doppelganger_person_pairs:
                roots_1 = person_roots.get(p1, set())
                roots_2 = person_roots.get(p2, set())
                if roots_1 and roots_2 and bool(roots_1.intersection(roots_2)):
                    merged_doppels += 1
            doppel_rate = merged_doppels / len(doppelganger_person_pairs)

        return ClusterMetrics(
            bcubed_precision=bcubed_p,
            bcubed_recall=bcubed_r,
            bcubed_f1=bcubed_f1,
            false_merge_clusters=false_merge_clusters,
            false_merged_records=false_merged_records,
            split_persons=split_persons,
            doppelganger_false_merge_rate=doppel_rate,
            dedup_reach=len(self.roots),
        )


def build_clusters_from_pairs(
    predictions_df: pd.DataFrame,
    record_ids: Sequence[str],
    threshold: float = 0.5,
) -> pd.DataFrame:
    """Build cluster assignments by finding connected components of pairs with p >= threshold.

    Args:
        predictions_df: DataFrame with record_id_l, record_id_r, match_probability.
        record_ids: Full universe of record IDs in the registry.
        threshold: Probability cutoff for establishing an edge.

    Returns:
        DataFrame with record_id, cluster_id.
    """
    uf = UnionFind(record_ids)
    if not predictions_df.empty:
        above = predictions_df[predictions_df["match_probability"] >= threshold]
        for _, row in above.iterrows():
            uf.union(str(row["record_id_l"]), str(row["record_id_r"]))

    rows = []
    for rid in record_ids:
        rows.append({"record_id": rid, "cluster_id": uf.find(rid)})
    return pd.DataFrame(rows)


def evaluate_clusters(
    clusters_df: pd.DataFrame,
    record_truth_df: pd.DataFrame,
    doppelganger_person_pairs_df: Optional[pd.DataFrame] = None,
) -> ClusterMetrics:
    """Evaluate cluster assignments against ground truth."""
    # Build maps
    record_person_map = dict(
        zip(
            record_truth_df["record_id"].astype(str),
            record_truth_df["person_id"].astype(str),
        )
    )
    person_counts = Counter(record_person_map.values())
    total_records = len(clusters_df)

    # Group records by cluster_id
    cluster_records: dict[str, list[str]] = defaultdict(list)
    for _, row in clusters_df.iterrows():
        cluster_records[str(row["cluster_id"])].append(str(row["record_id"]))

    prec_sum = 0.0
    rec_sum = 0.0
    false_merge_clusters = 0
    false_merged_records = 0
    person_clusters: dict[str, set[str]] = defaultdict(set)

    for cid, rids in cluster_records.items():
        c_size = len(rids)
        c_person_counts = Counter(
            record_person_map[rid] for rid in rids if rid in record_person_map
        )

        sum_sq = 0
        max_p_count = 0
        for p, count in c_person_counts.items():
            sum_sq += count * count
            if count > max_p_count:
                max_p_count = count
            person_clusters[p].add(cid)
            tot_p = person_counts.get(p, count)
            if tot_p > 0:
                rec_sum += (count * count) / tot_p

        prec_sum += sum_sq / c_size

        if len(c_person_counts) > 1:
            false_merge_clusters += 1
            false_merged_records += c_size - max_p_count

    bcubed_p = prec_sum / total_records if total_records > 0 else 1.0
    bcubed_r = rec_sum / total_records if total_records > 0 else 1.0
    bcubed_f1 = (
        (2.0 * bcubed_p * bcubed_r) / (bcubed_p + bcubed_r) if (bcubed_p + bcubed_r) > 0.0 else 0.0
    )

    split_persons = sum(1 for p, cids in person_clusters.items() if len(cids) > 1)

    # Doppelgangers
    doppel_rate = 0.0
    if doppelganger_person_pairs_df is not None and not doppelganger_person_pairs_df.empty:
        total_doppel_pairs = len(doppelganger_person_pairs_df)
        merged_doppels = 0
        for _, row in doppelganger_person_pairs_df.iterrows():
            p1 = str(row["person_id_1"])
            p2 = str(row["person_id_2"])
            cids_1 = person_clusters.get(p1, set())
            cids_2 = person_clusters.get(p2, set())
            if cids_1 and cids_2 and bool(cids_1.intersection(cids_2)):
                merged_doppels += 1
        doppel_rate = merged_doppels / total_doppel_pairs if total_doppel_pairs > 0 else 0.0

    return ClusterMetrics(
        bcubed_precision=bcubed_p,
        bcubed_recall=bcubed_r,
        bcubed_f1=bcubed_f1,
        false_merge_clusters=false_merge_clusters,
        false_merged_records=false_merged_records,
        split_persons=split_persons,
        doppelganger_false_merge_rate=doppel_rate,
        dedup_reach=len(cluster_records),
    )
