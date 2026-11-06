"""Exact match baseline with deterministic text normalisation and blocking."""

import re
import string
from collections import defaultdict
from typing import Any, Optional

import pandas as pd

from barilink.evaluate.contracts import PairwisePredictions

PREFIXES = {"md", "mohammad", "mohd", "mst", "most", "mosammat"}
PUNCT_TRANSLATOR = str.maketrans(string.punctuation, " " * len(string.punctuation))
PHONE_REGEX = re.compile(r"^01[3-9]\d{8}$")


def clean_name(val: Any) -> str:
    """Clean name by lowercasing, stripping punctuation, honorifics, and spaces."""
    if val is None or pd.isna(val):
        return ""
    text = str(val).lower().translate(PUNCT_TRANSLATOR)
    tokens = text.split()
    while tokens and tokens[0] in PREFIXES:
        tokens.pop(0)
    return " ".join(tokens)


def clean_village(val: Any) -> str:
    """Clean village by lowercasing, stripping punctuation, and collapsing whitespace."""
    if val is None or pd.isna(val):
        return ""
    text = str(val).lower().translate(PUNCT_TRANSLATOR)
    return " ".join(text.split())


def normalise_phone(val: Any) -> Optional[str]:
    """Normalise phone to Bangladeshi 11-digit format 01[3-9]XXXXXXXX."""
    if val is None or pd.isna(val):
        return None
    digits = re.sub(r"\D", "", str(val))
    if len(digits) == 13 and digits.startswith("8801"):
        digits = digits[2:]
    if len(digits) == 11 and PHONE_REGEX.match(digits):
        return digits
    return None


def generate_baseline_candidates(
    records_df: pd.DataFrame,
) -> tuple[set[tuple[str, str]], dict[str, dict[str, Any]]]:
    """Generate candidate pairs within same cleaned village OR same normalised phone.

    Returns:
        Tuple of (candidate_pairs_set, cleaned_records_dict).
    """
    cleaned_records: dict[str, dict[str, Any]] = {}
    village_groups: dict[str, list[str]] = defaultdict(list)
    phone_groups: dict[str, list[str]] = defaultdict(list)

    for _, row in records_df.iterrows():
        rid = str(row["record_id"])
        c_name = clean_name(row.get("full_name_raw"))
        c_guardian = clean_name(row.get("guardian_name_raw"))
        c_vil = clean_village(row.get("village_raw"))
        n_ph = normalise_phone(row.get("phone_raw"))

        cleaned_records[rid] = {
            "record_id": rid,
            "clean_name": c_name,
            "clean_guardian": c_guardian,
            "clean_village": c_vil,
            "normalised_phone": n_ph,
        }

        if c_vil:
            village_groups[c_vil].append(rid)
        if n_ph:
            phone_groups[n_ph].append(rid)

    candidates: set[tuple[str, str]] = set()

    for rids in village_groups.values():
        if len(rids) > 1:
            for i in range(len(rids)):
                for j in range(i + 1, len(rids)):
                    u, v = rids[i], rids[j]
                    candidates.add((min(u, v), max(u, v)))

    for rids in phone_groups.values():
        if len(rids) > 1:
            for i in range(len(rids)):
                for j in range(i + 1, len(rids)):
                    u, v = rids[i], rids[j]
                    candidates.add((min(u, v), max(u, v)))

    return candidates, cleaned_records


def run_exact_baseline(records_df: pd.DataFrame) -> PairwisePredictions:
    """Run exact string-matching baseline over blocked candidates.

    Matches (p=1.0) when clean_name AND clean_guardian AND clean_village are equal and non-empty.
    """
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

        if name_match and guardian_match and village_match:
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
        metadata={"method": "exact"},
    )
