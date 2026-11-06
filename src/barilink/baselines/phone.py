"""Phone-based and hybrid (exact_or_phone) baseline linkage methods."""

from typing import Any

import pandas as pd

from barilink.baselines.exact import generate_baseline_candidates
from barilink.evaluate.contracts import PairwisePredictions


def run_phone_baseline(records_df: pd.DataFrame) -> PairwisePredictions:
    """Run phone baseline matching (p=1.0) on identical non-null normalised 11-digit phone."""
    candidates, cleaned_records = generate_baseline_candidates(records_df)

    matched_rows: list[dict[str, Any]] = []
    for u, v in candidates:
        ph_u = cleaned_records[u]["normalised_phone"]
        ph_v = cleaned_records[v]["normalised_phone"]

        if ph_u is not None and ph_u == ph_v:
            matched_rows.append(
                {
                    "record_id_l": u,
                    "record_id_r": v,
                    "match_probability": 1.0,
                }
            )

    preds_df = pd.DataFrame(matched_rows)
    if preds_df.empty:
        preds_df = pd.DataFrame(columns=["record_id_l", "record_id_r", "match_probability"])

    return PairwisePredictions(
        predictions_df=preds_df,
        candidate_pair_count=len(candidates),
        metadata={"method": "phone"},
    )


def run_exact_or_phone_baseline(records_df: pd.DataFrame) -> PairwisePredictions:
    """Run union baseline matching (p=1.0) if either exact match or phone match holds."""
    candidates, cleaned_records = generate_baseline_candidates(records_df)

    matched_rows: list[dict[str, Any]] = []
    for u, v in candidates:
        rec_u = cleaned_records[u]
        rec_v = cleaned_records[v]

        name_match = bool(rec_u["clean_name"] and (rec_u["clean_name"] == rec_v["clean_name"]))
        guardian_match = bool(
            rec_u["clean_guardian"] and (rec_u["clean_guardian"] == rec_v["clean_guardian"])
        )
        village_match = bool(
            rec_u["clean_village"] and (rec_u["clean_village"] == rec_v["clean_village"])
        )
        exact_match = name_match and guardian_match and village_match

        ph_u = rec_u["normalised_phone"]
        ph_v = rec_v["normalised_phone"]
        phone_match = bool(ph_u is not None and ph_u == ph_v)

        if exact_match or phone_match:
            matched_rows.append(
                {
                    "record_id_l": u,
                    "record_id_r": v,
                    "match_probability": 1.0,
                }
            )

    preds_df = pd.DataFrame(matched_rows)
    if preds_df.empty:
        preds_df = pd.DataFrame(columns=["record_id_l", "record_id_r", "match_probability"])

    return PairwisePredictions(
        predictions_df=preds_df,
        candidate_pair_count=len(candidates),
        metadata={"method": "exact_or_phone"},
    )
