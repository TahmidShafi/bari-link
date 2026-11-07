"""Error diagnosis on DEV run at frozen operational threshold.

Identifies:
1. Missed true candidate pairs (false negatives among candidate pairs), broken down by:
   - guardian_type_raw combination (father/father, husband/husband,
     father/husband, null/known, both null)
   - true guardian switch vs same guardian
   - module pair
   - count of null fields across the pair
   - damaging Bayes factor
2. False merges at t_cost (false positives), broken down by:
   - true relationship (different household vs same household kinship roles)
   - positive Bayes factor drivers
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from splink import DuckDBAPI, Linker


def classify_guardian_type_combo(t1: Optional[str], t2: Optional[str]) -> str:
    """Classify pair of raw guardian types symmetrically."""
    v1 = str(t1).strip().lower() if pd.notna(t1) and str(t1).strip() != "" else None
    v2 = str(t2).strip().lower() if pd.notna(t2) and str(t2).strip() != "" else None

    if v1 is None and v2 is None:
        return "both null"
    if v1 is None or v2 is None:
        return "null/known"

    pair = tuple(sorted([v1, v2]))
    if pair == ("father", "father"):
        return "father/father"
    if pair == ("husband", "husband"):
        return "husband/husband"
    if pair == ("father", "husband"):
        return "father/husband"
    return f"{pair[0]}/{pair[1]}"


def classify_relationship(
    p1: str,
    p2: str,
    h1: str,
    h2: str,
    persons_map: dict[str, dict],
) -> str:
    """Classify ground-truth relationship between two persons."""
    if h1 != h2:
        return "Different household"

    info1 = persons_map.get(p1, {})
    info2 = persons_map.get(p2, {})

    # Spouse check
    if info1.get("spouse_id") == p2 or info2.get("spouse_id") == p1:
        return "Same household (Spouse)"

    # Parent-child check
    if (
        info1.get("father_id") == p2
        or info1.get("mother_id") == p2
        or info2.get("father_id") == p1
        or info2.get("mother_id") == p1
    ):
        return "Same household (Parent-Child)"

    # Sibling check
    f1, m1 = info1.get("father_id"), info1.get("mother_id")
    f2, m2 = info2.get("father_id"), info2.get("mother_id")
    if (f1 and f1 == f2) or (m1 and m1 == m2):
        return "Same household (Sibling)"

    return "Same household (Other)"


def run_dev_diagnosis(
    run_name: str = "demo",
    method: str = "splink_v1",
    base_data_dir: str = "data/generated",
    base_results_dir: str = "results",
) -> dict:
    """Run error diagnosis on DEV run at frozen t_cost."""
    run_dir = Path(base_data_dir) / run_name
    res_dir = Path(base_results_dir) / run_name / method
    model_path = Path(base_results_dir) / "models" / method / "model.json"
    sel_path = Path(base_results_dir) / method / "selected_thresholds.json"

    if not sel_path.exists():
        raise FileNotFoundError(f"Selected thresholds file not found at {sel_path}")
    with open(sel_path, "r", encoding="utf-8") as f:
        sel = json.load(f)
    t_cost = float(sel["t_cost_weight"])

    print(f"\nRunning DEV diagnosis for '{method}' on '{run_name}' at t_cost = {t_cost:.2f}...")

    # Load data
    feat_df = pd.read_parquet(run_dir / "registry" / "features.parquet")
    rec_df = pd.read_parquet(run_dir / "registry" / "records.parquet")
    rt_df = pd.read_parquet(run_dir / "truth" / "record_truth.parquet")
    p_df = pd.read_parquet(run_dir / "persons.parquet")
    clog_df = pd.read_parquet(run_dir / "truth" / "corruption_log.parquet")

    # Splink prediction with full comparison columns
    db_api = DuckDBAPI()
    linker = Linker(feat_df, str(model_path), db_api)
    pred_df = linker.inference.predict().as_duckdbpyrelation().df()

    # Merge truth onto left and right records
    rt_cols = ["record_id", "person_id", "household_id", "source_module"]
    rt_l = rt_df[rt_cols].rename(columns=lambda c: c + "_tl")
    rt_r = rt_df[rt_cols].rename(columns=lambda c: c + "_tr")

    rec_cols = [
        "record_id",
        "guardian_type_raw",
        "full_name_raw",
        "guardian_name_raw",
        "age_raw",
        "sex_raw",
        "phone_raw",
        "village_raw",
        "union_raw",
        "upazila_raw",
        "district_raw",
    ]
    rec_l = rec_df[rec_cols].rename(columns=lambda c: c + "_rl")
    rec_r = rec_df[rec_cols].rename(columns=lambda c: c + "_rr")

    df = pred_df.merge(rt_l, left_on="record_id_l", right_on="record_id_tl").merge(
        rt_r, left_on="record_id_r", right_on="record_id_tr"
    )
    df = df.merge(rec_l, left_on="record_id_l", right_on="record_id_rl").merge(
        rec_r, left_on="record_id_r", right_on="record_id_rr"
    )

    is_true = df["person_id_tl"] == df["person_id_tr"]
    scored_candidates = len(df)
    candidate_true_pairs = int(is_true.sum())

    # 1. Missed true candidate pairs (w < t_cost)
    missed_df = df[is_true & (df["match_weight"] < t_cost)].copy()
    num_missed = len(missed_df)

    # 2. False merges at t_cost (w >= t_cost)
    fm_df = df[(~is_true) & (df["match_weight"] >= t_cost)].copy()
    num_fm = len(fm_df)

    # A. Breakdown 1: guardian_type_raw combination
    missed_df["guardian_combo"] = [
        classify_guardian_type_combo(r["guardian_type_raw_rl"], r["guardian_type_raw_rr"])
        for _, r in missed_df.iterrows()
    ]
    guardian_combo_counts = missed_df["guardian_combo"].value_counts()

    # B. Breakdown 2: true guardian switch vs same guardian
    switched_records = set(clog_df[clog_df["corruption_type"] == "guardian_switch"]["record_id"])
    missed_df["switched_l"] = missed_df["record_id_l"].isin(switched_records)
    missed_df["switched_r"] = missed_df["record_id_r"].isin(switched_records)
    missed_df["is_switch"] = missed_df["switched_l"] ^ missed_df["switched_r"]
    switch_map = {True: "True guardian switch", False: "Same guardian"}
    switch_counts = missed_df["is_switch"].map(switch_map).value_counts()

    # C. Breakdown 3: module pair
    missed_df["mod_pair"] = [
        " vs ".join(sorted([str(r["source_module_tl"]), str(r["source_module_tr"])]))
        for _, r in missed_df.iterrows()
    ]
    module_pair_counts = missed_df["mod_pair"].value_counts()

    # D. Breakdown 4: count of null fields across the pair
    raw_eval_cols = [
        "full_name_raw",
        "guardian_name_raw",
        "guardian_type_raw",
        "age_raw",
        "sex_raw",
        "phone_raw",
        "village_raw",
        "union_raw",
        "upazila_raw",
        "district_raw",
    ]
    rec_null_map = rec_df.set_index("record_id")[raw_eval_cols].isna().sum(axis=1).to_dict()
    missed_df["null_count"] = missed_df["record_id_l"].map(rec_null_map) + missed_df[
        "record_id_r"
    ].map(rec_null_map)
    null_count_counts = missed_df["null_count"].value_counts().sort_index()

    # E. Breakdown 5: damaging Bayes factor
    bf_cols = [c for c in df.columns if c.startswith("bf_") and not c.startswith("bf_tf_adj_")]
    bf_log2_df = pd.DataFrame(
        {
            col: np.log2(np.clip(missed_df[col].fillna(1.0).astype(float), 1e-12, 1e12))
            for col in bf_cols
        },
        index=missed_df.index,
    )
    missed_df["damaging_bf"] = bf_log2_df.idxmin(axis=1).str.replace("^bf_", "", regex=True)
    damaging_bf_counts = missed_df["damaging_bf"].value_counts()

    # False merge analysis
    persons_map = p_df.set_index("person_id").to_dict(orient="index")
    fm_df["rel"] = [
        classify_relationship(
            r["person_id_tl"],
            r["person_id_tr"],
            r["household_id_tl"],
            r["household_id_tr"],
            persons_map,
        )
        for _, r in fm_df.iterrows()
    ]
    fm_rel_counts = fm_df["rel"].value_counts()

    # Positive BF drivers for false merges
    fm_pos_bf: dict[str, int] = {}
    for col in bf_cols:
        col_clean = col.replace("bf_", "")
        log_val = np.log2(np.clip(fm_df[col].fillna(1.0).astype(float), 1e-12, 1e12))
        fm_pos_bf[col_clean] = int((log_val > 0).sum())
    fm_pos_bf_series = pd.Series(fm_pos_bf).sort_values(ascending=False)

    # Console display of top 3 cells
    print("\n" + "=" * 70)
    print("DEV ERROR DIAGNOSIS SUMMARY (Top 3 Cells per Breakdown)")
    print("=" * 70)
    missed_pct = num_missed / candidate_true_pairs * 100
    print(f"Total scored candidate pairs: {scored_candidates:,}")
    print(f"Total candidate true pairs:   {candidate_true_pairs:,}")
    print(f"Missed true candidate pairs:  {num_missed:,} ({missed_pct:.1f}%)")
    print(f"False merges at t_cost:       {num_fm:,}")
    print("-" * 70)

    print("1. Guardian Type Combo (Missed True Pairs):")
    for k, v in guardian_combo_counts.head(3).items():
        print(f"   - {k:<25} {v:>4} ({v / num_missed * 100:.1f}%)")

    print("\n2. True Guardian Switch vs Same Guardian:")
    for k, v in switch_counts.head(3).items():
        print(f"   - {k:<25} {v:>4} ({v / num_missed * 100:.1f}%)")

    print("\n3. Module Pair (Missed True Pairs):")
    for k, v in module_pair_counts.head(3).items():
        print(f"   - {k:<40} {v:>4} ({v / num_missed * 100:.1f}%)")

    print("\n4. Null Field Count across Pair (Missed True Pairs):")
    for k, v in null_count_counts.sort_values(ascending=False).head(3).items():
        print(f"   - {k} null fields:                {v:>4} ({v / num_missed * 100:.1f}%)")

    print("\n5. Damaging Bayes Factor (Missed True Pairs):")
    for k, v in damaging_bf_counts.head(3).items():
        print(f"   - {k:<25} {v:>4} ({v / num_missed * 100:.1f}%)")

    print("\n6. False Merge True Relationship:")
    for k, v in fm_rel_counts.head(3).items():
        pct = (v / num_fm * 100) if num_fm > 0 else 0.0
        print(f"   - {k:<30} {v:>4} ({pct:.1f}%)")

    print("\n7. False Merge Positive Bayes Factor Drivers:")
    for k, v in fm_pos_bf_series.head(3).items():
        pct = (v / num_fm * 100) if num_fm > 0 else 0.0
        print(f"   - {k:<25} {v:>4} pairs ({pct:.1f}%)")
    print("=" * 70)

    # Write diagnosis.md
    res_dir.mkdir(parents=True, exist_ok=True)
    out_md = res_dir / "diagnosis.md"

    md_lines = [
        f"# Linkage Error Diagnosis: `{method}` on `{run_name}`",
        "",
        (
            f"This report evaluates linking errors on the DEV dataset (`{run_name}`) at the "
            f"frozen operational threshold $t_{{\\text{{cost}}}} = {t_cost:.2f}$."
        ),
        "",
        "## Summary Metrics",
        "",
        f"- **Total Scored Candidate Pairs**: {scored_candidates:,}",
        f"- **Total Candidate True Pairs**: {candidate_true_pairs:,}",
        (
            f"- **Missed True Candidate Pairs (False Negatives)**: "
            f"{num_missed:,} ({num_missed / candidate_true_pairs * 100:.2f}%)"
        ),
        f"- **False Merges at $t_{{\\text{{cost}}}}$ (False Positives)**: {num_fm:,}",
        "",
        "---",
        "",
        "## 1. Missed True Candidate Pairs Analysis",
        "",
        "### A. Guardian Type Raw Combination",
        "",
        "| Guardian Type Combination | Count | Percentage |",
        "| :--- | :--- | :--- |",
    ]
    for k, v in guardian_combo_counts.items():
        md_lines.append(f"| `{k}` | {v:,} | {v / num_missed * 100:.2f}% |")

    md_lines.extend(
        [
            "",
            "### B. True Guardian Switch vs Same Guardian",
            "",
            "| Relationship Status | Count | Percentage |",
            "| :--- | :--- | :--- |",
        ]
    )
    for k, v in switch_counts.items():
        md_lines.append(f"| `{k}` | {v:,} | {v / num_missed * 100:.2f}% |")

    md_lines.extend(
        [
            "",
            "### C. Cross-Module Pair Distribution",
            "",
            "| Module Pair | Count | Percentage |",
            "| :--- | :--- | :--- |",
        ]
    )
    for k, v in module_pair_counts.items():
        md_lines.append(f"| `{k}` | {v:,} | {v / num_missed * 100:.2f}% |")

    md_lines.extend(
        [
            "",
            "### D. Null Field Count Across Pair (out of 20 raw fields)",
            "",
            "| Null Count | Count | Percentage |",
            "| :--- | :--- | :--- |",
        ]
    )
    for k, v in null_count_counts.items():
        md_lines.append(f"| {k} | {v:,} | {v / num_missed * 100:.2f}% |")

    md_lines.extend(
        [
            "",
            "### E. Most Damaging Bayes Factor",
            "",
            (
                "Comparison whose log2 Bayes factor was most negative, "
                "pulling match weight below $t_{\\text{cost}}$:"
            ),
            "",
            "| Damaging Comparison | Count | Percentage |",
            "| :--- | :--- | :--- |",
        ]
    )
    for k, v in damaging_bf_counts.items():
        md_lines.append(f"| `{k}` | {v:,} | {v / num_missed * 100:.2f}% |")

    md_lines.extend(
        [
            "",
            "---",
            "",
            "## 2. False Merges Analysis",
            "",
            "### A. Ground-Truth Relationship of Erroneously Merged Pairs",
            "",
            "| Ground-Truth Relationship | Count | Percentage |",
            "| :--- | :--- | :--- |",
        ]
    )
    for k, v in fm_rel_counts.items():
        pct = (v / num_fm * 100) if num_fm > 0 else 0.0
        md_lines.append(f"| `{k}` | {v:,} | {pct:.2f}% |")

    md_lines.extend(
        [
            "",
            "### B. Comparison Features Driving False Merges (Positive Bayes Factors)",
            "",
            (
                "Number of false-merge pairs where the comparison contributed "
                "$\\text{BF} > 1.0$ (positive log-odds):"
            ),
            "",
            "| Comparison Feature | Pairs with Positive BF | Fraction of False Merges |",
            "| :--- | :--- | :--- |",
        ]
    )
    for k, v in fm_pos_bf_series.items():
        pct = (v / num_fm * 100) if num_fm > 0 else 0.0
        md_lines.append(f"| `{k}` | {v:,} | {pct:.2f}% |")

    out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"\nFull diagnosis written to: {out_md.resolve()}")

    return {
        "scored_candidates": scored_candidates,
        "candidate_true_pairs": candidate_true_pairs,
        "missed_true_candidates": num_missed,
        "false_merges": num_fm,
        "guardian_combo_counts": guardian_combo_counts.to_dict(),
        "switch_counts": switch_counts.to_dict(),
        "module_pair_counts": module_pair_counts.to_dict(),
        "damaging_bf_counts": damaging_bf_counts.to_dict(),
        "fm_rel_counts": fm_rel_counts.to_dict(),
        "fm_pos_bf": fm_pos_bf,
    }
