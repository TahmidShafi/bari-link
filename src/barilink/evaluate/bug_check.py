"""Diagnostic bug check on DEV data for self-entry roster collisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from barilink.link.normalise import canonicalise_name, clean_text_basic, compute_skeleton


def run_kinship_bug_check(
    run_name: str = "demo",
    method: str = "splink_v3",
    resolved_method: str = "splink_v3_resolved",
    base_data_dir: str | Path = "data/generated",
    base_results_dir: str | Path = "results",
) -> dict[str, Any]:
    """Check for true candidate pairs erroneously severed by listed_as_other_member constraint."""
    run_dir = Path(base_data_dir) / run_name
    truth_dir = run_dir / "truth"
    reg_dir = run_dir / "registry"

    rec_truth = pd.read_parquet(truth_dir / "record_truth.parquet")
    rec_to_person = rec_truth.set_index("record_id")["person_id"].to_dict()

    records_df = pd.read_parquet(reg_dir / "records.parquet").set_index("record_id")
    rosters_df = pd.read_parquet(reg_dir / "rosters.parquet")
    features_df = pd.read_parquet(reg_dir / "features.parquet").set_index("record_id")

    preds_p = Path(base_results_dir) / run_name / method / "predictions.parquet"
    if not preds_p.exists():
        raise FileNotFoundError(f"Predictions parquet not found at {preds_p}")
    preds = pd.read_parquet(preds_p)

    preds["person_l"] = preds["record_id_l"].map(rec_to_person)
    preds["person_r"] = preds["record_id_r"].map(rec_to_person)
    true_preds = preds[preds["person_l"] == preds["person_r"]]

    # 1. Count true pairs where listed_as_other_member fired
    fired_pairs = []
    examples = []
    for _, row in true_preds.iterrows():
        rl = row["record_id_l"]
        rr = row["record_id_r"]
        skel_l = features_df.loc[rl, "name_skeleton"]
        skel_r = features_df.loc[rr, "name_skeleton"]
        r_skels_l = features_df.loc[rl, "roster_skels_v3"]
        r_skels_r = features_df.loc[rr, "roster_skels_v3"]

        fired_l = bool(r_skels_r is not None and len(r_skels_r) > 0 and skel_l in r_skels_r)
        fired_r = bool(r_skels_l is not None and len(r_skels_l) > 0 and skel_r in r_skels_l)

        if fired_l or fired_r:
            fired_pairs.append((rl, rr, fired_l, fired_r))

            if fired_l:
                rost_r = rosters_df[rosters_df["record_id"] == rr]
                for _, ro in rost_r.iterrows():
                    m_name = clean_text_basic(ro["member_name_raw"])
                    m_skel = compute_skeleton(canonicalise_name(m_name))
                    if m_skel == skel_l:
                        examples.append(
                            {
                                "record_id": rl,
                                "roster_record_id": rr,
                                "person_id": row["person_l"],
                                "participant_raw_name": records_df.loc[rl, "full_name_raw"],
                                "roster_member_raw_name": ro["member_name_raw"],
                                "relation_raw": ro["relation_raw"],
                                "participant_skeleton": skel_l,
                                "member_skeleton": m_skel,
                            }
                        )

            if fired_r:
                rost_l = rosters_df[rosters_df["record_id"] == rl]
                for _, ro in rost_l.iterrows():
                    m_name = clean_text_basic(ro["member_name_raw"])
                    m_skel = compute_skeleton(canonicalise_name(m_name))
                    if m_skel == skel_r:
                        examples.append(
                            {
                                "record_id": rr,
                                "roster_record_id": rl,
                                "person_id": row["person_l"],
                                "participant_raw_name": records_df.loc[rr, "full_name_raw"],
                                "roster_member_raw_name": ro["member_name_raw"],
                                "relation_raw": ro["relation_raw"],
                                "participant_skeleton": skel_r,
                                "member_skeleton": m_skel,
                            }
                        )

    # 2. Count resolution cannot-link cuts that separated records of the same person
    res_log_p = Path(base_results_dir) / run_name / resolved_method / "resolution_log.parquet"
    same_person_cuts = []
    total_listed_cuts = 0

    if res_log_p.exists():
        res_log = pd.read_parquet(res_log_p)
        listed_cuts = res_log[res_log["reason"] == "listed_as_other_member"]
        total_listed_cuts = len(listed_cuts)

        for _, row in listed_cuts.iterrows():
            u = row["record_id_l"]
            v = row["record_id_r"]
            pu = rec_to_person.get(u)
            pv = rec_to_person.get(v)
            if pu == pv and pu is not None:
                same_person_cuts.append(
                    {
                        "component_id": str(row.get("component_id", "")),
                        "record_id_l": u,
                        "record_id_r": v,
                        "person_id": pu,
                        "weight": float(row["weight"]),
                        "name_l": records_df.loc[u, "full_name_raw"],
                        "name_r": records_df.loc[v, "full_name_raw"],
                        "guardian_l": records_df.loc[u, "guardian_name_raw"],
                        "guardian_r": records_df.loc[v, "guardian_name_raw"],
                    }
                )

    return {
        "method": method,
        "resolved_method": resolved_method,
        "true_candidate_pairs": len(true_preds),
        "true_pairs_listed_fired_count": len(fired_pairs),
        "total_listed_cuts": total_listed_cuts,
        "same_person_cuts_count": len(same_person_cuts),
        "same_person_cuts": same_person_cuts,
        "examples": examples,
    }
