"""Kinship-aware golden record generation with attribute survivorship and provenance lineage.

Strict segregation: This module reads only model-visible data (clusters.parquet,
records.parquet, features.parquet, resolution_log.parquet).
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd


def _pick_mode_with_date_tiebreaker(
    items: list[tuple[Any, str, str]],
) -> tuple[Any, str]:
    """Pick mode value, breaking ties by most recent enrolment_date.

    Args:
        items: list of (value, enrolment_date, record_id).

    Returns:
        (winning_value, winning_record_id)
    """
    valid = [it for it in items if it[0] is not None and pd.notna(it[0]) and str(it[0]).strip()]
    if not valid:
        return None, ""

    counts = Counter(it[0] for it in valid)
    max_count = max(counts.values())
    top_candidates = [val for val, cnt in counts.items() if cnt == max_count]

    if len(top_candidates) == 1:
        win_val = top_candidates[0]
        win_rec = next(it[2] for it in valid if it[0] == win_val)
        return win_val, win_rec

    # Tiebreak by most recent enrolment_date
    tied_items = [it for it in valid if it[0] in top_candidates]
    tied_items.sort(key=lambda it: str(it[1]), reverse=True)
    return tied_items[0][0], tied_items[0][2]


def build_golden_records(
    clusters_df: pd.DataFrame,
    records_df: pd.DataFrame,
    features_df: Optional[pd.DataFrame] = None,
    resolution_log_df: Optional[pd.DataFrame] = None,
    predictions_df: Optional[pd.DataFrame] = None,
    output_path: Optional[Path] = None,
) -> pd.DataFrame:
    """Generate one canonical golden record per cluster following survivorship and kinship rules."""
    # Ensure merged view
    df = records_df.copy()
    if features_df is not None and not features_df.empty:
        extra_cols = [c for c in features_df.columns if c not in df.columns and c != "record_id"]
        if extra_cols:
            df = df.merge(features_df[["record_id"] + extra_cols], on="record_id", how="left")

    df = df.merge(clusters_df[["record_id", "cluster_id"]], on="record_id", how="inner")

    # Was split lookup
    split_records = set()
    if resolution_log_df is not None and not resolution_log_df.empty:
        split_records.update(resolution_log_df["record_id_l"].astype(str))
        split_records.update(resolution_log_df["record_id_r"].astype(str))

    # Min internal edge weight lookup per cluster
    internal_min_weight: dict[str, float] = {}
    if predictions_df is not None and not predictions_df.empty:
        # Map record_id to cluster_id
        rec_cluster_map = dict(
            zip(clusters_df["record_id"].astype(str), clusters_df["cluster_id"].astype(str))
        )
        for _, row in predictions_df.iterrows():
            u = str(row["record_id_l"])
            v = str(row["record_id_r"])
            c_u = rec_cluster_map.get(u)
            c_v = rec_cluster_map.get(v)
            if c_u and c_v and c_u == c_v:
                w = float(row.get("match_weight", 0.0))
                if c_u not in internal_min_weight or w < internal_min_weight[c_u]:
                    internal_min_weight[c_u] = w

    golden_rows = []

    # Group by cluster_id
    for cid, c_df in df.groupby("cluster_id"):
        c_records = c_df.to_dict(orient="records")
        n_recs = len(c_records)
        record_ids = sorted([str(r["record_id"]) for r in c_records])
        modules = sorted(
            list(
                set(str(r["source_module"]) for r in c_records if pd.notna(r.get("source_module")))
            )
        )
        dates = [str(r["enrolment_date"]) for r in c_records if pd.notna(r.get("enrolment_date"))]
        dates.sort()
        first_date = dates[0] if dates else ""
        last_date = dates[-1] if dates else ""

        lineage: dict[str, dict[str, str]] = {}

        # 1. display_name: mode name_canon -> tie token count -> tie date. Output raw form.
        # Group by name_canon
        canon_groups: dict[str, list[dict]] = {}
        for r in c_records:
            nc = str(r.get("name_canon", "")).strip()
            if not nc:
                nc = str(r.get("full_name_raw", "")).strip().lower()
            canon_groups.setdefault(nc, []).append(r)

        # Mode count of name_canon
        max_canon_count = max(len(grp) for grp in canon_groups.values())
        top_canons = [nc for nc, grp in canon_groups.items() if len(grp) == max_canon_count]

        candidate_records = []
        for nc in top_canons:
            candidate_records.extend(canon_groups[nc])

        # Tiebreak 1: token count
        # Tiebreak 2: enrolment date
        candidate_records.sort(
            key=lambda r: (
                len(str(r.get("full_name_raw", "")).split()),
                str(r.get("enrolment_date", "")),
            ),
            reverse=True,
        )
        win_rec = candidate_records[0]
        display_name = str(win_rec.get("full_name_raw", "")).strip()
        lineage["display_name"] = {
            "source_record_id": str(win_rec["record_id"]),
            "rule": "mode_name_canon_tie_tokens_date",
        }

        # 2. father_name and husband_name: SEPARATE fields
        # Father
        father_recs = [
            (r.get("guardian_name_raw"), str(r.get("enrolment_date", "")), str(r["record_id"]))
            for r in c_records
            if str(r.get("guardian_type_raw", "")).strip().lower() == "father"
        ]
        father_name, f_rid = _pick_mode_with_date_tiebreaker(father_recs)
        if father_name:
            lineage["father_name"] = {
                "source_record_id": f_rid,
                "rule": "mode_guardian_father_tie_date",
            }

        # Husband
        husband_recs = [
            (r.get("guardian_name_raw"), str(r.get("enrolment_date", "")), str(r["record_id"]))
            for r in c_records
            if str(r.get("guardian_type_raw", "")).strip().lower() == "husband"
        ]
        husband_name, h_rid = _pick_mode_with_date_tiebreaker(husband_recs)
        if husband_name:
            lineage["husband_name"] = {
                "source_record_id": h_rid,
                "rule": "mode_guardian_husband_tie_date",
            }

        # 3. birth_year: median of birth_year_est (robust to heaping) + birth_year_spread
        by_list = []
        for r in c_records:
            by_val = r.get("birth_year_est")
            if by_val is not None and pd.notna(by_val):
                try:
                    by_list.append(int(float(by_val)))
                except (ValueError, TypeError):
                    pass

        if by_list:
            median_by = int(round(float(np.median(by_list))))
            by_spread = int(max(by_list) - min(by_list))
            # Pick record with value closest to median as source
            closest_r = min(
                c_records,
                key=lambda r: (
                    abs(float(r.get("birth_year_est", median_by)) - median_by)
                    if pd.notna(r.get("birth_year_est"))
                    else 999
                ),
            )
            lineage["birth_year"] = {
                "source_record_id": str(closest_r["record_id"]),
                "rule": "median_birth_year_est",
            }
        else:
            median_by = None
            by_spread = 0

        # 4. phone: most recent valid phone_norm. phones_all = sorted distinct list.
        phone_items = []
        for r in c_records:
            p = r.get("phone_norm")
            if p is not None and pd.notna(p) and str(p).strip():
                phone_items.append(
                    (str(p).strip(), str(r.get("enrolment_date", "")), str(r["record_id"]))
                )

        if phone_items:
            phone_items.sort(key=lambda it: it[1], reverse=True)
            phone = phone_items[0][0]
            lineage["phone"] = {
                "source_record_id": phone_items[0][2],
                "rule": "most_recent_valid_phone",
            }
            phones_all = sorted(list(set(it[0] for it in phone_items)))
        else:
            phone = None
            phones_all = []

        # 5. sex, village, union, upazila, district: mode, tie -> most recent date
        for attr, field in [
            ("sex", "sex_raw"),
            ("village", "village_raw"),
            ("union", "union_raw"),
            ("upazila", "upazila_raw"),
            ("district", "district_raw"),
        ]:
            items = [
                (r.get(field), str(r.get("enrolment_date", "")), str(r["record_id"]))
                for r in c_records
                if r.get(field) is not None and pd.notna(r.get(field))
            ]
            val, rid = _pick_mode_with_date_tiebreaker(items)
            lineage[attr] = {"source_record_id": rid, "rule": f"mode_{attr}_tie_date"}
            if attr == "sex":
                sex = val
            elif attr == "village":
                village = val
            elif attr == "union":
                union = val
            elif attr == "upazila":
                upazila = val
            elif attr == "district":
                district = val

        # 6. Quality & Confidence
        was_split = any(rid in split_records for rid in record_ids)
        min_weight = internal_min_weight.get(cid)

        golden_rows.append(
            {
                "cluster_id": cid,
                "display_name": display_name,
                "father_name": father_name,
                "husband_name": husband_name,
                "birth_year": median_by,
                "birth_year_spread": by_spread,
                "phone": phone,
                "phones_all": phones_all,
                "sex": sex,
                "village": village,
                "union": union,
                "upazila": upazila,
                "district": district,
                "modules": modules,
                "record_ids": record_ids,
                "first_enrolment": first_date,
                "last_enrolment": last_date,
                "n_records": n_recs,
                "confidence_min_internal_weight": min_weight,
                "confidence_was_split": was_split,
                "field_lineage": json.dumps(lineage, sort_keys=True),
            }
        )

    golden_df = pd.DataFrame(golden_rows)
    golden_df = golden_df.sort_values("cluster_id").reset_index(drop=True)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        golden_df.to_parquet(output_path, index=False)

    return golden_df
