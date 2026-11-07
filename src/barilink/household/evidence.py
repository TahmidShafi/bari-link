"""Evidence extraction and scoring for household inference.

Strict segregation: This module processes only model-visible inputs.
Zero references to ground-truth files or directories are permitted.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

from barilink.link.normalise import (
    canonicalise_name,
    clean_text_basic,
    compute_skeleton,
)

# Prefix & title tokens for model-visible sex inference
FEMALE_PREFIXES: frozenset[str] = frozenset({"mst", "most", "mosammat"})
FEMALE_TITLES: frozenset[str] = frozenset(
    {"khatun", "khatoon", "begum", "akter", "bibi", "rani", "bala"}
)
MALE_PREFIXES: frozenset[str] = frozenset({"md", "mohammad", "mohd"})

DEFAULT_HOUSEHOLD_WEIGHTS: dict[str, float] = {
    "E1": 4.0,  # assumed, not fitted: listed_member
    "E2": 4.0,  # assumed, not fitted: husband_link
    "E3": 2.0,  # assumed, not fitted: father_link
    "E4": 3.0,  # assumed, not fitted: roster_overlap
    "E5": 1.0,  # assumed, not fitted: shared_phone
}


@dataclass
class UnitProfile:
    """Consolidated profile for an entity cluster (unit) for household inference."""

    cluster_id: str
    record_ids: list[str]
    village_canon: Optional[str]
    village_raw: str
    union_raw: str
    display_name: str
    display_name_skeleton: Optional[str]
    name_skels: set[str]
    husband_name: Optional[str]
    husband_skeleton: Optional[str]
    has_husband: bool
    father_name: Optional[str]
    father_skeleton: Optional[str]
    birth_year: Optional[int]
    age: Optional[int]
    inferred_sex: Optional[str]  # "F", "M", "conflict", or None
    roster_skels: set[str]
    roster_sources: dict[str, list[str]] = field(default_factory=dict)
    phones: set[str] = field(default_factory=set)
    phone_sources: dict[str, list[str]] = field(default_factory=dict)
    modules: list[str] = field(default_factory=list)
    first_enrolment: str = ""
    last_enrolment: str = ""


def _pick_mode_with_date_tiebreaker(
    items: list[tuple[Any, str, str]],
) -> tuple[Any, str]:
    """Pick mode value, breaking ties by most recent enrolment_date."""
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

    tied_items = [it for it in valid if it[0] in top_candidates]
    tied_items.sort(key=lambda it: str(it[1]), reverse=True)
    return tied_items[0][0], tied_items[0][2]


def _infer_unit_sex(records: list[dict[str, Any]]) -> Optional[str]:
    """Infer sex from model-visible raw name prefixes and title tokens.

    F if any record has a female prefix (mst/most/mosammat) or title (khatun/begum/etc).
    M if any record has a male prefix (md/mohammad/mohd).
    'conflict' if both; else None.
    """
    has_f = False
    has_m = False

    for r in records:
        raw_name = str(r.get("full_name_raw", "")).lower()
        cleaned = re.sub(r"[^\w\s]", " ", raw_name)
        tokens = set(cleaned.split())

        title_tok = str(r.get("title_token", "")).strip().lower()
        if title_tok and title_tok != "none" and title_tok != "nan":
            tokens.add(title_tok)

        if (tokens & FEMALE_PREFIXES) or (tokens & FEMALE_TITLES):
            has_f = True
        if tokens & MALE_PREFIXES:
            has_m = True

    if has_f and has_m:
        return "conflict"
    if has_f:
        return "F"
    if has_m:
        return "M"
    return None


def build_unit_profiles(
    clusters_df: pd.DataFrame,
    records_df: pd.DataFrame,
    features_df: Optional[pd.DataFrame] = None,
    reference_year: int = 2026,
) -> dict[str, UnitProfile]:
    """Aggregate entity records into unit profiles for household evidence evaluation."""
    df = records_df.copy()
    if features_df is not None and not features_df.empty:
        extra_cols = [c for c in features_df.columns if c not in df.columns and c != "record_id"]
        if extra_cols:
            df = df.merge(features_df[["record_id"] + extra_cols], on="record_id", how="left")

    df = df.merge(clusters_df[["record_id", "cluster_id"]], on="record_id", how="inner")

    profiles: dict[str, UnitProfile] = {}

    for cid, c_df in df.groupby("cluster_id"):
        cid_str = str(cid)
        c_records = c_df.to_dict(orient="records")
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

        # Display name
        canon_groups: dict[str, list[dict]] = {}
        for r in c_records:
            nc = str(r.get("name_canon", "")).strip()
            if not nc or nc == "none" or nc == "nan":
                nc = canonicalise_name(clean_text_basic(r.get("full_name_raw", "")))
            canon_groups.setdefault(nc, []).append(r)

        max_canon_count = max(len(grp) for grp in canon_groups.values())
        top_canons = [nc for nc, grp in canon_groups.items() if len(grp) == max_canon_count]
        candidate_records = []
        for nc in top_canons:
            candidate_records.extend(canon_groups[nc])

        candidate_records.sort(
            key=lambda r: (
                len(str(r.get("full_name_raw", "")).split()),
                str(r.get("enrolment_date", "")),
            ),
            reverse=True,
        )
        win_rec = candidate_records[0]
        display_name = str(win_rec.get("full_name_raw", "")).strip()
        disp_skel = compute_skeleton(canonicalise_name(clean_text_basic(display_name)))

        # Name skeletons set across member records + display name
        name_skels = set()
        if disp_skel:
            name_skels.add(disp_skel)
        for r in c_records:
            sk = r.get("name_skeleton")
            if sk is not None and pd.notna(sk) and str(sk).strip():
                name_skels.add(str(sk).strip())
            raw_sk = compute_skeleton(
                canonicalise_name(clean_text_basic(r.get("full_name_raw", "")))
            )
            if raw_sk:
                name_skels.add(raw_sk)

        # Husband link info
        husband_items = [
            (r.get("guardian_name_raw"), str(r.get("enrolment_date", "")), str(r["record_id"]))
            for r in c_records
            if str(r.get("guardian_type_raw", "")).strip().lower() == "husband"
            or str(r.get("guardian_type", "")).strip().lower() == "husband"
        ]
        husband_name, _ = _pick_mode_with_date_tiebreaker(husband_items)
        husband_skeleton = None
        has_husband = False
        if husband_name and str(husband_name).strip():
            has_husband = True
            husband_skeleton = compute_skeleton(canonicalise_name(clean_text_basic(husband_name)))

        # Father link info
        father_items = [
            (r.get("guardian_name_raw"), str(r.get("enrolment_date", "")), str(r["record_id"]))
            for r in c_records
            if str(r.get("guardian_type_raw", "")).strip().lower() == "father"
            or str(r.get("guardian_type", "")).strip().lower() == "father"
        ]
        father_name, _ = _pick_mode_with_date_tiebreaker(father_items)
        father_skeleton = None
        if father_name and str(father_name).strip():
            father_skeleton = compute_skeleton(canonicalise_name(clean_text_basic(father_name)))

        # Birth year: median birth_year_est
        by_list = []
        for r in c_records:
            by_val = r.get("birth_year_est")
            if by_val is not None and pd.notna(by_val):
                try:
                    by_list.append(int(float(by_val)))
                except (ValueError, TypeError):
                    pass
            elif r.get("age_raw") is not None and pd.notna(r.get("age_raw")):
                try:
                    age_val = float(r["age_raw"])
                    by_list.append(int(round(reference_year - age_val)))
                except (ValueError, TypeError):
                    pass

        if by_list:
            median_by = int(round(float(np.median(by_list))))
            age = max(0, reference_year - median_by)
        else:
            median_by = None
            age = None

        # Inferred sex
        inferred_sex = _infer_unit_sex(c_records)

        # Village canon (mode)
        v_can_items = [
            (r.get("village_canon"), str(r.get("enrolment_date", "")), str(r["record_id"]))
            for r in c_records
            if r.get("village_canon") is not None and pd.notna(r.get("village_canon"))
        ]
        village_canon, _ = _pick_mode_with_date_tiebreaker(v_can_items)

        # Raw village & union (mode)
        v_raw_items = [
            (r.get("village_raw"), str(r.get("enrolment_date", "")), str(r["record_id"]))
            for r in c_records
            if r.get("village_raw") is not None and pd.notna(r.get("village_raw"))
        ]
        village_raw, _ = _pick_mode_with_date_tiebreaker(v_raw_items)
        u_raw_items = [
            (r.get("union_raw"), str(r.get("enrolment_date", "")), str(r["record_id"]))
            for r in c_records
            if r.get("union_raw") is not None and pd.notna(r.get("union_raw"))
        ]
        union_raw, _ = _pick_mode_with_date_tiebreaker(u_raw_items)

        # Rosters attached: collect roster_skels_v3 (already self-filtered)
        roster_skels: set[str] = set()
        roster_sources: dict[str, list[str]] = {}
        for r in c_records:
            r_skels = r.get("roster_skels_v3")
            if r_skels is None or not hasattr(r_skels, "__iter__"):
                r_skels = r.get("roster_skels")
            if r_skels is not None and hasattr(r_skels, "__iter__"):
                rid_s = str(r["record_id"])
                for item in r_skels:
                    if item is not None and pd.notna(item) and str(item).strip():
                        s_str = str(item).strip()
                        # Self-filter guard
                        if s_str not in name_skels:
                            roster_skels.add(s_str)
                            roster_sources.setdefault(s_str, []).append(rid_s)

        # Phones attached
        phones: set[str] = set()
        phone_sources: dict[str, list[str]] = {}
        for r in c_records:
            p = r.get("phone_norm")
            if p is not None and pd.notna(p) and str(p).strip() and str(p).strip().lower() != "nan":
                p_str = str(p).strip()
                phones.add(p_str)
                phone_sources.setdefault(p_str, []).append(str(r["record_id"]))

        profiles[cid_str] = UnitProfile(
            cluster_id=cid_str,
            record_ids=record_ids,
            village_canon=village_canon,
            village_raw=str(village_raw) if village_raw is not None else "",
            union_raw=str(union_raw) if union_raw is not None else "",
            display_name=display_name,
            display_name_skeleton=disp_skel,
            name_skels=name_skels,
            husband_name=husband_name,
            husband_skeleton=husband_skeleton,
            has_husband=has_husband,
            father_name=father_name,
            father_skeleton=father_skeleton,
            birth_year=median_by,
            age=age,
            inferred_sex=inferred_sex,
            roster_skels=roster_skels,
            roster_sources=roster_sources,
            phones=phones,
            phone_sources=phone_sources,
            modules=modules,
            first_enrolment=first_date,
            last_enrolment=last_date,
        )

    return profiles


def compute_sex_inference_coverage(profiles: dict[str, UnitProfile]) -> float:
    """Compute the coverage of model-visible inferred_sex across units."""
    if not profiles:
        return 0.0
    valid_count = sum(1 for u in profiles.values() if u.inferred_sex is not None)
    return float(valid_count / len(profiles))


def build_household_evidence(
    profiles: dict[str, UnitProfile],
    weights: Optional[dict[str, float]] = None,
    output_path: Optional[Path] = None,
) -> pd.DataFrame:
    """Evaluate candidate pairs within village_canon blocks for household evidence E1..E5.

    Candidate unit pairs share the same non-null village_canon.
    Pairs are indexed via feature channels to evaluate only pairs with non-zero potential.
    """
    if weights is None:
        weights = DEFAULT_HOUSEHOLD_WEIGHTS

    w1 = float(weights.get("E1", 4.0))
    w2 = float(weights.get("E2", 4.0))
    w3 = float(weights.get("E3", 2.0))
    w4 = float(weights.get("E4", 3.0))
    w5 = float(weights.get("E5", 1.0))

    # Group units by village_canon
    village_units: dict[str, list[UnitProfile]] = {}
    for u in profiles.values():
        if u.village_canon and str(u.village_canon).strip():
            village_units.setdefault(str(u.village_canon).strip(), []).append(u)

    edge_rows: list[dict[str, Any]] = []

    for _, v_list in village_units.items():
        if len(v_list) < 2:
            continue

        # Inverted indices within village block for O(K) candidate generation
        name_skel_idx: dict[str, list[UnitProfile]] = {}
        roster_skel_idx: dict[str, list[UnitProfile]] = {}
        husband_skel_idx: dict[str, list[UnitProfile]] = {}
        father_skel_idx: dict[str, list[UnitProfile]] = {}
        phone_idx: dict[str, list[UnitProfile]] = {}

        for u in v_list:
            for sk in u.name_skels:
                name_skel_idx.setdefault(sk, []).append(u)
            for rsk in u.roster_skels:
                roster_skel_idx.setdefault(rsk, []).append(u)
            if u.has_husband and u.husband_skeleton:
                husband_skel_idx.setdefault(u.husband_skeleton, []).append(u)
            if u.father_skeleton:
                father_skel_idx.setdefault(u.father_skeleton, []).append(u)
            for ph in u.phones:
                phone_idx.setdefault(ph, []).append(u)

        candidate_pairs: set[tuple[str, str]] = set()

        # Channel 1: E1 candidates (name in roster)
        for sk, u_names in name_skel_idx.items():
            if sk in roster_skel_idx:
                for un in u_names:
                    for ur in roster_skel_idx[sk]:
                        if un.cluster_id != ur.cluster_id:
                            pair = (
                                min(un.cluster_id, ur.cluster_id),
                                max(un.cluster_id, ur.cluster_id),
                            )
                            candidate_pairs.add(pair)

        # Channel 2: E2 candidates (husband_skel matches any name_skel)
        for h_sk, u_husbands in husband_skel_idx.items():
            if h_sk in name_skel_idx:
                for uh in u_husbands:
                    for un in name_skel_idx[h_sk]:
                        if uh.cluster_id != un.cluster_id:
                            pair = (
                                min(uh.cluster_id, un.cluster_id),
                                max(uh.cluster_id, un.cluster_id),
                            )
                            candidate_pairs.add(pair)

        # Channel 3: E3 candidates (father_skel matches any name_skel)
        for f_sk, u_fathers in father_skel_idx.items():
            if f_sk in name_skel_idx:
                for uf in u_fathers:
                    for un in name_skel_idx[f_sk]:
                        if uf.cluster_id != un.cluster_id:
                            pair = (
                                min(uf.cluster_id, un.cluster_id),
                                max(uf.cluster_id, un.cluster_id),
                            )
                            candidate_pairs.add(pair)

        # Channel 4: E4 candidates (shared roster skels)
        for _, u_rosters in roster_skel_idx.items():
            if len(u_rosters) >= 2:
                for i in range(len(u_rosters)):
                    for j in range(i + 1, len(u_rosters)):
                        u1 = u_rosters[i]
                        u2 = u_rosters[j]
                        if u1.cluster_id != u2.cluster_id:
                            pair = (
                                min(u1.cluster_id, u2.cluster_id),
                                max(u1.cluster_id, u2.cluster_id),
                            )
                            candidate_pairs.add(pair)

        # Channel 5: E5 candidates (shared phones)
        for _, u_phones in phone_idx.items():
            if len(u_phones) >= 2:
                for i in range(len(u_phones)):
                    for j in range(i + 1, len(u_phones)):
                        u1 = u_phones[i]
                        u2 = u_phones[j]
                        if u1.cluster_id != u2.cluster_id:
                            pair = (
                                min(u1.cluster_id, u2.cluster_id),
                                max(u1.cluster_id, u2.cluster_id),
                            )
                            candidate_pairs.add(pair)

        # Evaluate candidate pairs
        for cid_a, cid_b in candidate_pairs:
            u_a = profiles[cid_a]
            u_b = profiles[cid_b]

            lineage: dict[str, Any] = {}

            # E1: listed_member
            e1_ab = list(u_a.name_skels & u_b.roster_skels)
            e1_ba = list(u_b.name_skels & u_a.roster_skels)
            e1_active = bool(e1_ab or e1_ba)
            if e1_active:
                lineage["E1"] = {
                    "matched_skels_a_in_b_roster": e1_ab,
                    "matched_skels_b_in_a_roster": e1_ba,
                }

            # E2: husband_link (Amendment 4: match against ANY name skeleton)
            e2_a_is_wife = bool(
                u_a.has_husband
                and u_a.husband_skeleton
                and (u_a.husband_skeleton in u_b.name_skels)
            )
            e2_b_is_wife = bool(
                u_b.has_husband
                and u_b.husband_skeleton
                and (u_b.husband_skeleton in u_a.name_skels)
            )
            e2_active = e2_a_is_wife or e2_b_is_wife
            if e2_active:
                lineage["E2"] = {
                    "a_is_wife": e2_a_is_wife,
                    "b_is_wife": e2_b_is_wife,
                    "wife_unit": cid_a if e2_a_is_wife else cid_b,
                    "husband_unit": cid_b if e2_a_is_wife else cid_a,
                    "husband_skeleton": (
                        u_a.husband_skeleton if e2_a_is_wife else u_b.husband_skeleton
                    ),
                }

            # E3: father_link (child is NOT adult female and has NO husband_name)
            # A is child, B is father
            e3_a_child = (
                not (u_a.inferred_sex == "F" and u_a.age is not None and u_a.age >= 18)
                and not u_a.has_husband
                and bool(u_a.father_skeleton and (u_a.father_skeleton in u_b.name_skels))
                and (u_a.birth_year is not None and u_b.birth_year is not None)
                and (u_a.birth_year >= u_b.birth_year + 15)
            )
            # B is child, A is father
            e3_b_child = (
                not (u_b.inferred_sex == "F" and u_b.age is not None and u_b.age >= 18)
                and not u_b.has_husband
                and bool(u_b.father_skeleton and (u_b.father_skeleton in u_a.name_skels))
                and (u_b.birth_year is not None and u_a.birth_year is not None)
                and (u_b.birth_year >= u_a.birth_year + 15)
            )
            e3_active = e3_a_child or e3_b_child
            if e3_active:
                lineage["E3"] = {
                    "child_unit": cid_a if e3_a_child else cid_b,
                    "father_unit": cid_b if e3_a_child else cid_a,
                    "birth_year_gap": (
                        (u_a.birth_year - u_b.birth_year)
                        if e3_a_child and u_a.birth_year and u_b.birth_year
                        else (
                            (u_b.birth_year - u_a.birth_year)
                            if u_a.birth_year and u_b.birth_year
                            else None
                        )
                    ),
                }

            # E4: roster_overlap (share >= 2 member skeletons)
            shared_roster = list(u_a.roster_skels & u_b.roster_skels)
            e4_active = bool(len(shared_roster) >= 2)
            if e4_active:
                lineage["E4"] = {
                    "count": len(shared_roster),
                    "shared_skeletons": shared_roster,
                }

            # E5: shared_phone (share >= 1 normalized phone)
            shared_ph = list(u_a.phones & u_b.phones)
            e5_active = bool(len(shared_ph) >= 1)
            if e5_active:
                lineage["E5"] = {
                    "shared_phones": shared_ph,
                }

            # Weighted sum score
            score = (
                w1 * float(e1_active)
                + w2 * float(e2_active)
                + w3 * float(e3_active)
                + w4 * float(e4_active)
                + w5 * float(e5_active)
            )

            if score >= 1.0:
                edge_rows.append(
                    {
                        "unit_id_l": cid_a,
                        "unit_id_r": cid_b,
                        "score": score,
                        "e1": e1_active,
                        "e2": e2_active,
                        "e3": e3_active,
                        "e4": e4_active,
                        "e5": e5_active,
                        "evidence_lineage": json.dumps(lineage, sort_keys=True),
                    }
                )

    edges_df = pd.DataFrame(edge_rows)
    if edges_df.empty:
        edges_df = pd.DataFrame(
            columns=[
                "unit_id_l",
                "unit_id_r",
                "score",
                "e1",
                "e2",
                "e3",
                "e4",
                "e5",
                "evidence_lineage",
            ]
        )
    else:
        edges_df = edges_df.sort_values(["unit_id_l", "unit_id_r"]).reset_index(drop=True)

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        edges_df.to_parquet(output_path, index=False)

    return edges_df
