"""Household golden record synthesis with direct and indirect reach estimation.

Strict segregation: This module processes only model-visible inputs.
Zero references to ground-truth files or directories are permitted.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from barilink.household.evidence import UnitProfile


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


def build_household_golden_records(
    household_clusters_df: pd.DataFrame,
    profiles: dict[str, UnitProfile],
    records_df: Optional[pd.DataFrame] = None,
    output_path: Optional[Path] = None,
) -> pd.DataFrame:
    """Generate canonical household golden records following attribute survivorship and reach rules.

    Args:
        household_clusters_df: DataFrame with cluster_id, household_id.
        profiles: Dictionary mapping cluster_id to UnitProfile.
        records_df: Optional DataFrame of raw records to retrieve field dates/records.
        output_path: Optional path to save household_golden.parquet.

    Returns:
        DataFrame of canonical household golden records.
    """
    # Group cluster_ids by household_id
    hh_groups: dict[str, list[str]] = {}
    for _, row in household_clusters_df.iterrows():
        hh_id = str(row["household_id"])
        c_id = str(row["cluster_id"])
        hh_groups.setdefault(hh_id, []).append(c_id)

    golden_rows: list[dict[str, Any]] = []

    for hh_id, member_cids in hh_groups.items():
        member_profiles = [profiles[cid] for cid in member_cids if cid in profiles]
        lineage: dict[str, Any] = {}

        # 1. Geographic mode (village, union) with date tiebreaker
        village_items: list[tuple[Any, str, str]] = []
        union_items: list[tuple[Any, str, str]] = []
        for u in member_profiles:
            if u.village_raw:
                village_items.append((u.village_raw, u.last_enrolment, u.cluster_id))
            if u.union_raw:
                union_items.append((u.union_raw, u.last_enrolment, u.cluster_id))

        village_val, v_source = _pick_mode_with_date_tiebreaker(village_items)
        union_val, u_source = _pick_mode_with_date_tiebreaker(union_items)
        lineage["village"] = {
            "value": village_val,
            "source_unit": v_source,
            "rule": "mode_village_tie_date",
        }
        lineage["union"] = {
            "value": union_val,
            "source_unit": u_source,
            "rule": "mode_union_tie_date",
        }

        # 2. Enrolled members info
        enrolled_members = []
        enrolled_name_skels: set[str] = set()
        modules_set: set[str] = set()
        phones_set: set[str] = set()
        all_roster_skels: list[str] = []
        has_any_roster = False

        for u in member_profiles:
            enrolled_members.append(
                {
                    "cluster_id": u.cluster_id,
                    "display_name": u.display_name,
                    "birth_year": u.birth_year,
                    "inferred_sex": u.inferred_sex,
                }
            )
            enrolled_name_skels.update(u.name_skels)
            modules_set.update(u.modules)
            phones_set.update(u.phones)
            if u.roster_skels:
                has_any_roster = True
                all_roster_skels.extend(u.roster_skels)

        # 3. Roster names unenrolled
        # Skeletons attached to any member that match NO enrolled member's name skeleton
        unenrolled_skels = sorted(
            list(set(rsk for rsk in all_roster_skels if rsk not in enrolled_name_skels))
        )

        direct_reach = len(member_profiles)
        indirect_reach = len(unenrolled_skels)
        est_household_size = direct_reach + indirect_reach

        lineage["direct_reach"] = {
            "count": direct_reach,
            "unit_ids": [u.cluster_id for u in member_profiles],
        }
        lineage["indirect_reach"] = {
            "count": indirect_reach,
            "unenrolled_skeletons": unenrolled_skels,
            "has_roster": has_any_roster,
        }
        lineage["est_household_size"] = {
            "formula": "direct_reach + indirect_reach",
            "value": est_household_size,
        }

        golden_rows.append(
            {
                "household_id": hh_id,
                "village": village_val,
                "union": union_val,
                "enrolled_members": json.dumps(enrolled_members, sort_keys=True),
                "member_cluster_ids": sorted(member_cids),
                "modules": sorted(list(modules_set)),
                "phones_all": sorted(list(phones_set)),
                "roster_names_unenrolled": unenrolled_skels,
                "has_roster": has_any_roster,
                "direct_reach": direct_reach,
                "indirect_reach": indirect_reach,
                "est_household_size": est_household_size,
                "field_lineage": json.dumps(lineage, sort_keys=True),
            }
        )

    golden_df = pd.DataFrame(golden_rows)
    if golden_df.empty:
        golden_df = pd.DataFrame(
            columns=[
                "household_id",
                "village",
                "union",
                "enrolled_members",
                "member_cluster_ids",
                "modules",
                "phones_all",
                "roster_names_unenrolled",
                "has_roster",
                "direct_reach",
                "indirect_reach",
                "est_household_size",
                "field_lineage",
            ]
        )
    else:
        golden_df = golden_df.sort_values("household_id").reset_index(drop=True)

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        golden_df.to_parquet(output_path, index=False)

    return golden_df
