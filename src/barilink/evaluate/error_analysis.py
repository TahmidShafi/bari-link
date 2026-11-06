"""Linkage error analysis and blocking failure diagnostic reporting.

Authorized to read ground-truth records from truth/ directory to evaluate
model false merges, false negatives, and unblocked true pairs at t_cost.
"""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path
from typing import Any, Optional

import pandas as pd


def _format_cell(val: Any) -> str:
    """Format table cell to avoid markdown layout breakage."""
    if val is None or pd.isna(val):
        return "—"
    s = str(val).strip().replace("|", "/")
    return s if s else "—"


def generate_error_analysis(
    run_name: str,
    method: str = "splink_v1",
    base_data_dir: str = "data/generated",
    base_results_dir: str = "results",
    t_cost: Optional[float] = None,
) -> str:
    """Analyze false merges, false negatives, and unblocked true pairs at t_cost."""
    run_dir = Path(base_data_dir) / run_name
    truth_path = run_dir / "truth" / "record_truth.parquet"
    records_path = run_dir / "registry" / "records.parquet"
    features_path = run_dir / "registry" / "features.parquet"

    results_dir = Path(base_results_dir) / run_name / method
    preds_path = results_dir / "predictions.parquet"
    out_md_path = results_dir / "error_analysis.md"

    if not truth_path.exists():
        raise FileNotFoundError(f"Truth file not found: {truth_path}")
    if not preds_path.exists():
        raise FileNotFoundError(f"Predictions not found: {preds_path}")

    # Determine t_cost
    if t_cost is None:
        sel_path = Path(base_results_dir) / method / "selected_thresholds.json"
        metrics_path = results_dir / "metrics.json"
        if sel_path.exists():
            with open(sel_path, "r", encoding="utf-8") as f:
                sel = json.load(f)
                t_cost = float(sel.get("t_cost", 0.5))
        elif metrics_path.exists():
            with open(metrics_path, "r", encoding="utf-8") as f:
                m = json.load(f)
                t_cost = float(m.get("operational_thresholds", {}).get("t_cost", 0.5))
        else:
            t_cost = 0.5

    # Load data
    truth_df = pd.read_parquet(truth_path)
    records_df = pd.read_parquet(records_path) if records_path.exists() else pd.DataFrame()
    features_df = pd.read_parquet(features_path) if features_path.exists() else pd.DataFrame()
    preds_df = pd.read_parquet(preds_path)

    # Build lookups
    truth_map = dict(zip(truth_df["record_id"], truth_df["person_id"]))

    rec_info: dict[str, dict[str, Any]] = {}
    if not records_df.empty:
        for row in records_df.to_dict(orient="records"):
            rec_info[str(row["record_id"])] = row

    features_dict: dict[str, dict[str, Any]] = {}
    if not features_df.empty:
        for row in features_df.to_dict(orient="records"):
            features_dict[str(row["record_id"])] = row

    # Ground-truth true pairs
    grouped_persons = truth_df.groupby("person_id")["record_id"].apply(list)
    true_pairs_set: set[tuple[str, str]] = set()
    for rec_list in grouped_persons:
        if len(rec_list) >= 2:
            for r1, r2 in combinations(sorted(rec_list), 2):
                true_pairs_set.add((r1, r2))

    total_true_pairs = len(true_pairs_set)

    # Scored pairs analysis
    scored_pairs_set: set[tuple[str, str]] = set()
    false_merges = []
    candidate_false_negatives = []

    for row in preds_df.to_dict(orient="records"):
        r_l = str(row["record_id_l"])
        r_r = str(row["record_id_r"])
        if r_l > r_r:
            r_l, r_r = r_r, r_l
        p = float(row["match_probability"])
        pair = (r_l, r_r)
        scored_pairs_set.add(pair)

        p_l = truth_map.get(r_l)
        p_r = truth_map.get(r_r)
        is_same_person = (p_l == p_r) and (p_l is not None)

        if p >= t_cost and not is_same_person:
            false_merges.append((r_l, r_r, p, p_l, p_r))
        elif p < t_cost and is_same_person:
            candidate_false_negatives.append((r_l, r_r, p, p_l, p_r))

    # Sort
    false_merges.sort(key=lambda x: x[2], reverse=True)
    candidate_false_negatives.sort(key=lambda x: x[2])

    top_false_merges = false_merges[:15]
    top_fn = candidate_false_negatives[:15]

    # Unblocked true pairs
    unblocked_true_pairs = sorted(true_pairs_set - scored_pairs_set)
    unblocked_count = len(unblocked_true_pairs)
    unblocked_share = (
        (unblocked_count / total_true_pairs * 100.0) if total_true_pairs > 0 else 0.0
    )

    # Build Markdown Report
    lines = [
        f"# Linkage Error Analysis: {method} ({run_name})",
        "",
        f"**Decision Threshold ($t_{{cost}}$):** `{t_cost:.4f}`  ",
        f"**Total Ground-Truth True Pairs:** `{total_true_pairs:,}`  ",
        f"**Total Scored Candidate Pairs:** `{len(scored_pairs_set):,}`  ",
        f"**Scored True Pairs:** `{len(true_pairs_set & scored_pairs_set):,}`  ",
        f"**Unblocked True Pairs (Missed by all rules):** `{unblocked_count:,}` "
        f"({unblocked_share:.2f}%)  ",
        f"**Total False Merges ($p \\ge t_{{cost}}$):** `{len(false_merges):,}`  ",
        f"**Total Candidate False Negatives ($p < t_{{cost}}$):** "
        f"`{len(candidate_false_negatives):,}`  ",
        "",
        "---",
        "",
        "## 1. Top 15 False Merges (Highest Probability Non-Matches)",
        "",
        "Pairs of records representing different individuals that the model scored above the "
        "decision threshold:",
        "",
    ]

    if top_false_merges:
        lines.append(
            "| Rank | Record L | Record R | Prob | Name L | Name R | Guardian L | Guardian R | "
            "Village L | Village R | Phone L | Phone R | Mod L | Mod R |"
        )
        lines.append(
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | "
            ":--- | :--- | :--- | :--- | :--- | :--- |"
        )
        for rank, (r_l, r_r, p, _, _) in enumerate(top_false_merges, start=1):
            i_l = rec_info.get(r_l, {})
            i_r = rec_info.get(r_r, {})
            lines.append(
                f"| {rank} | `{r_l}` | `{r_r}` | {p:.4f} | "
                f"{_format_cell(i_l.get('full_name_raw'))} | "
                f"{_format_cell(i_r.get('full_name_raw'))} | "
                f"{_format_cell(i_l.get('guardian_name_raw'))} | "
                f"{_format_cell(i_r.get('guardian_name_raw'))} | "
                f"{_format_cell(i_l.get('village_raw'))} | "
                f"{_format_cell(i_r.get('village_raw'))} | "
                f"{_format_cell(i_l.get('phone_raw'))} | "
                f"{_format_cell(i_r.get('phone_raw'))} | "
                f"{_format_cell(i_l.get('source_module'))} | "
                f"{_format_cell(i_r.get('source_module'))} |"
            )
    else:
        lines.append("_No false merges observed at this threshold._")

    lines.extend([
        "",
        "---",
        "",
        "## 2. Top 15 Candidate False Negatives (Lowest Probability True Matches)",
        "",
        "Pairs of records representing the same individual that were captured by blocking "
        "rules but received low match probabilities:",
        "",
    ])

    if top_fn:
        lines.append(
            "| Rank | Record L | Record R | Prob | Name L | Name R | Guardian L | Guardian R | "
            "Village L | Village R | Phone L | Phone R | Mod L | Mod R |"
        )
        lines.append(
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | "
            ":--- | :--- | :--- | :--- | :--- | :--- |"
        )
        for rank, (r_l, r_r, p, _, _) in enumerate(top_fn, start=1):
            i_l = rec_info.get(r_l, {})
            i_r = rec_info.get(r_r, {})
            lines.append(
                f"| {rank} | `{r_l}` | `{r_r}` | {p:.4f} | "
                f"{_format_cell(i_l.get('full_name_raw'))} | "
                f"{_format_cell(i_r.get('full_name_raw'))} | "
                f"{_format_cell(i_l.get('guardian_name_raw'))} | "
                f"{_format_cell(i_r.get('guardian_name_raw'))} | "
                f"{_format_cell(i_l.get('village_raw'))} | "
                f"{_format_cell(i_r.get('village_raw'))} | "
                f"{_format_cell(i_l.get('phone_raw'))} | "
                f"{_format_cell(i_r.get('phone_raw'))} | "
                f"{_format_cell(i_l.get('source_module'))} | "
                f"{_format_cell(i_r.get('source_module'))} |"
            )
    else:
        lines.append("_No candidate false negatives observed._")

    lines.extend([
        "",
        "---",
        "",
        "## 3. Unblocked True Pairs Analysis",
        "",
        f"A total of **{unblocked_count:,}** true pairs ({unblocked_share:.2f}%) "
        "were never generated as candidate pairs because they failed all 5 blocking rules.",
        "",
        "### Sample of Unblocked True Pairs and Rule Failure Attribution",
        "",
    ])

    sample_unblocked = unblocked_true_pairs[:10]
    for idx, (r_l, r_r) in enumerate(sample_unblocked, start=1):
        i_l = rec_info.get(r_l, {})
        i_r = rec_info.get(r_r, {})
        f_l = features_dict.get(r_l, {})
        f_r = features_dict.get(r_r, {})

        lines.append(f"#### Case {idx}: `{r_l}` and `{r_r}` (Person: `{truth_map.get(r_l)}`)")
        lines.append(
            f"- **Record L:** {_format_cell(i_l.get('full_name_raw'))} | "
            f"Guardian: {_format_cell(i_l.get('guardian_name_raw'))} | "
            f"Village: {_format_cell(i_l.get('village_raw'))} | "
            f"Phone: {_format_cell(i_l.get('phone_raw'))} | "
            f"Age: {_format_cell(i_l.get('age_raw'))}"
        )
        lines.append(
            f"- **Record R:** {_format_cell(i_r.get('full_name_raw'))} | "
            f"Guardian: {_format_cell(i_r.get('guardian_name_raw'))} | "
            f"Village: {_format_cell(i_r.get('village_raw'))} | "
            f"Phone: {_format_cell(i_r.get('phone_raw'))} | "
            f"Age: {_format_cell(i_r.get('age_raw'))}"
        )
        lines.append("- **Blocking Rule Failure Reasons:**")

        # Rule 1
        g1_l, g1_r = f_l.get("given_first_skel"), f_r.get("given_first_skel")
        v_l, v_r = f_l.get("village_canon"), f_r.get("village_canon")
        r1_reasons = []
        if g1_l != g1_r:
            r1_reasons.append(f"different first token skeleton ('{g1_l}' vs '{g1_r}')")
        if v_l != v_r:
            r1_reasons.append(f"different village ('{v_l}' vs '{v_r}')")
        lines.append(
            f"  1. `given_first_skel + village_canon`: "
            f"{', '.join(r1_reasons) if r1_reasons else 'failed'}"
        )

        # Rule 2
        p_l, p_r = f_l.get("phone_norm"), f_r.get("phone_norm")
        if p_l is None or p_r is None:
            r2_reason = "missing phone on one or both records"
        elif p_l != p_r:
            r2_reason = f"different phone number ('{p_l}' vs '{p_r}')"
        else:
            r2_reason = "failed"
        lines.append(f"  2. `phone_norm`: {r2_reason}")

        # Rule 3
        gs_l, gs_r = f_l.get("guardian_skeleton"), f_r.get("guardian_skeleton")
        r3_reasons = []
        if gs_l != gs_r:
            r3_reasons.append(f"different guardian skeleton ('{gs_l}' vs '{gs_r}')")
        if v_l != v_r:
            r3_reasons.append(f"different village ('{v_l}' vs '{v_r}')")
        lines.append(
            f"  3. `guardian_skeleton + village_canon`: "
            f"{', '.join(r3_reasons) if r3_reasons else 'failed'}"
        )

        # Rule 4
        ns_l, ns_r = f_l.get("name_skeleton"), f_r.get("name_skeleton")
        u_l, u_r = f_l.get("union_raw"), f_r.get("union_raw")
        r4_reasons = []
        if ns_l != ns_r:
            r4_reasons.append(f"different name skeleton ('{ns_l}' vs '{ns_r}')")
        if u_l != u_r:
            r4_reasons.append(f"different union ('{u_l}' vs '{u_r}')")
        lines.append(
            f"  4. `name_skeleton + union_raw`: "
            f"{', '.join(r4_reasons) if r4_reasons else 'failed'}"
        )

        # Rule 5
        by_l, by_r = f_l.get("birth_year_est"), f_r.get("birth_year_est")
        r5_reasons = []
        if g1_l != g1_r:
            r5_reasons.append(f"different first token skeleton ('{g1_l}' vs '{g1_r}')")
        if by_l != by_r:
            r5_reasons.append(f"different birth year estimate ({by_l} vs {by_r})")
        lines.append(
            f"  5. `given_first_skel + birth_year_est`: "
            f"{', '.join(r5_reasons) if r5_reasons else 'failed'}"
        )
        lines.append("")

    content = "\n".join(lines) + "\n"
    with open(out_md_path, "w", encoding="utf-8") as f:
        f.write(content)

    return content
