"""Stratified pairwise performance breakdowns across modules, corruptions, and names."""

from typing import Optional

import pandas as pd


def compute_strata_breakdowns(
    clusters_df: pd.DataFrame,
    record_truth_df: pd.DataFrame,
    true_pairs_df: pd.DataFrame,
    corruption_log_df: pd.DataFrame,
    predictions_df: Optional[pd.DataFrame] = None,
    threshold: float = 0.5,
) -> pd.DataFrame:
    """Compute stratified pairwise recall and precision.

    Breakdowns:
    1. Module pairs (e.g. upg_enrolment x microfinance_group)
    2. Corruption modes (guardian_switch, transliteration, phone)
    3. Name frequency bands (top-10, 11-50, rest)

    Args:
        clusters_df: DataFrame with record_id, cluster_id at operational threshold.
        record_truth_df: DataFrame with record_id, person_id, source_module, clean_given_name.
        true_pairs_df: DataFrame with record_id_1, record_id_2.
        corruption_log_df: DataFrame with record_id, corruption_type.
        predictions_df: Optional scored predictions.
        threshold: Threshold cutoff.

    Returns:
        DataFrame with stratum_type, stratum_value, tp, fp, fn, precision, recall, f1.
    """
    rec_meta = record_truth_df.set_index("record_id").to_dict(orient="index")

    # Name frequency bands from clean_given_name
    name_counts = record_truth_df["clean_given_name"].value_counts()
    top_10_names = set(name_counts.iloc[:10].index)
    top_50_names = set(name_counts.iloc[10:50].index)

    def get_name_band(name: str) -> str:
        if name in top_10_names:
            return "top-10"
        elif name in top_50_names:
            return "11-50"
        return "rest"

    # Corruption flags
    corr_types = corruption_log_df[["record_id", "corruption_type"]].drop_duplicates()
    guardian_switch_rids = set(
        corr_types[corr_types["corruption_type"].str.contains("guardian", case=False)][
            "record_id"
        ]
    )
    translit_rids = set(
        corr_types[corr_types["corruption_type"].str.contains("translit", case=False)][
            "record_id"
        ]
    )
    phone_rids = set(
        corr_types[corr_types["corruption_type"].str.contains("phone", case=False)]["record_id"]
    )

    # True pairs set
    true_pairs_set: set[tuple[str, str]] = set()
    for _, row in true_pairs_df.iterrows():
        r1, r2 = str(row["record_id_1"]), str(row["record_id_2"])
        true_pairs_set.add((min(r1, r2), max(r1, r2)))

    # Cluster-level predicted pairs
    cluster_to_records = clusters_df.groupby("cluster_id")["record_id"].apply(list)
    pred_pairs_set: set[tuple[str, str]] = set()
    for _, rids in cluster_to_records.items():
        if len(rids) > 1:
            for i in range(len(rids)):
                for j in range(i + 1, len(rids)):
                    r1, r2 = str(rids[i]), str(rids[j])
                    pred_pairs_set.add((min(r1, r2), max(r1, r2)))

    # Evaluate TP and FP
    tp_pairs = pred_pairs_set.intersection(true_pairs_set)
    fp_pairs = pred_pairs_set - true_pairs_set
    fn_pairs = true_pairs_set - pred_pairs_set

    # Helper to classify pair into strata
    def get_pair_strata(r1: str, r2: str) -> dict[str, str]:
        m1 = rec_meta.get(r1, {}).get("source_module", "unknown")
        m2 = rec_meta.get(r2, {}).get("source_module", "unknown")
        mod_pair = f"{min(m1, m2)} x {max(m1, m2)}"

        has_g = (r1 in guardian_switch_rids) or (r2 in guardian_switch_rids)
        g_sw = "guardian_switch" if has_g else "no_guardian_switch"

        has_tr = (r1 in translit_rids) or (r2 in translit_rids)
        tr = "transliteration" if has_tr else "no_transliteration"

        has_ph = (r1 in phone_rids) or (r2 in phone_rids)
        ph = "phone_corruption" if has_ph else "no_phone_corruption"

        n1 = rec_meta.get(r1, {}).get("clean_given_name", "")
        name_band = get_name_band(n1)

        return {
            "module_pair": mod_pair,
            "guardian_switch": g_sw,
            "transliteration": tr,
            "phone_corruption": ph,
            "name_band": name_band,
        }

    # Aggregate counts per stratum
    # strata_counts: (stratum_type, stratum_value) -> {'tp': 0, 'fp': 0, 'fn': 0}
    strata_counts: dict[tuple[str, str], dict[str, int]] = {}

    def record_stat(pair: tuple[str, str], metric: str) -> None:
        r1, r2 = pair
        s_dict = get_pair_strata(r1, r2)
        for s_type, s_val in s_dict.items():
            key = (s_type, s_val)
            if key not in strata_counts:
                strata_counts[key] = {"tp": 0, "fp": 0, "fn": 0}
            strata_counts[key][metric] += 1

    for pair in tp_pairs:
        record_stat(pair, "tp")
    for pair in fp_pairs:
        record_stat(pair, "fp")
    for pair in fn_pairs:
        record_stat(pair, "fn")

    rows = []
    for (s_type, s_val), counts in sorted(strata_counts.items()):
        tp = counts["tp"]
        fp = counts["fp"]
        fn = counts["fn"]
        p = (tp / (tp + fp)) if (tp + fp) > 0 else 1.0
        r = (tp / (tp + fn)) if (tp + fn) > 0 else 1.0
        f1 = (2.0 * p * r) / (p + r) if (p + r) > 0.0 else 0.0
        rows.append(
            {
                "stratum_type": s_type,
                "stratum_value": s_val,
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "precision": p,
                "recall": r,
                "f1": f1,
            }
        )

    return pd.DataFrame(rows)
