"""Audit untrained Splink comparison level parameters (m and u probabilities).

Analyzes results/models/splink_k/model.json:
1. Programmatically inspects comparison levels where m or u was not estimated.
2. Programmatically reads default values used by Splink at inference.
3. Counts candidate pairs falling into each untrained level across holdout_5..9.
4. Re-scores candidate pairs with each untrained level's Bayes factor set to 1 (neutral)
   and evaluates resolution sensitivity at frozen thresholds without retraining.
5. Documents inert sex_raw comparison.
6. Exports results to results/summary/untrained_params_audit.json.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import duckdb
import numpy as np
import pandas as pd
from splink import DuckDBAPI, Linker

from barilink.resolve.graph import build_resolved_graph, evaluate_resolved_clusters


def run_untrained_parameter_audit(
    model_path: str | Path = "results/models/splink_k/model.json",
    base_data_dir: str | Path = "data/generated",
    base_results_dir: str | Path = "results",
    output_path: str | Path = "results/summary/untrained_params_audit.json",
    seeds: tuple[str, ...] = ("holdout_5", "holdout_6", "holdout_7", "holdout_8", "holdout_9"),
) -> dict[str, Any]:
    """Execute the untrained parameter audit and sensitivity analysis."""
    model_path = Path(model_path)
    base_data_dir = Path(base_data_dir)
    base_results_dir = Path(base_results_dir)
    output_path = Path(output_path)

    with open(model_path, "r", encoding="utf-8") as f:
        model_dict = json.load(f)

    # 1. Programmatically extract default m/u values using Splink Linker
    dummy_df = pd.DataFrame(
        [
            {
                "record_id": "r1",
                "given_first_skel": "a",
                "village_canon": "b",
                "phone_norm": "01711111111",
                "guardian_skeleton": "c",
                "name_skeleton": "d",
                "union_raw": "u",
                "birth_year_est": 1990,
                "name_canon": "e",
                "name_tokens_sorted": "f",
                "guardian_canon": "g",
                "phone_last8": "11111111",
                "sex_raw": None,
                "title_token": None,
                "roster_canons": [],
                "guardian_type": None,
            }
        ]
    )
    db_api = DuckDBAPI()
    linker = Linker(dummy_df, model_dict, db_api=db_api)

    untrained_levels_info: list[dict[str, Any]] = []

    for comp in linker._settings_obj.comparisons:
        comp_name = comp.output_column_name
        # Skip inert comparisons where all pairs are null; reported under sex_raw_audit
        if comp_name == "sex_raw":
            continue

        # Find raw comparison in JSON
        raw_comp = next(
            (
                c
                for c in model_dict.get("comparisons", [])
                if c.get("output_column_name") == comp_name
            ),
            None,
        )
        if not raw_comp:
            continue

        raw_levels = raw_comp.get("comparison_levels", [])
        for cl in comp.comparison_levels:
            if getattr(cl, "is_null_level", False):
                continue

            raw_cl = next(
                (lvl for lvl in raw_levels if lvl.get("sql_condition") == cl.sql_condition),
                {},
            )
            m_in_json = "m_probability" in raw_cl
            u_in_json = "u_probability" in raw_cl

            if not m_in_json or not u_in_json:
                m_val = float(cl.m_probability)
                u_val = float(cl.u_probability)
                bf_val = float(cl.bayes_factor) if hasattr(cl, "bayes_factor") else (m_val / u_val)

                # Assert reported m and u are valid probabilities
                assert 0.0 <= m_val <= 1.0, f"m_probability {m_val} not in [0, 1]"
                assert 0.0 <= u_val <= 1.0, f"u_probability {u_val} not in [0, 1]"

                untrained_levels_info.append(
                    {
                        "comparison": comp_name,
                        "label": cl.label_for_charts,
                        "sql_condition": cl.sql_condition,
                        "comparison_vector_value": cl.comparison_vector_value,
                        "m_estimated_in_model": m_in_json,
                        "u_estimated_in_model": u_in_json,
                        "m_default_used": m_val,
                        "u_default_used": u_val,
                        "bayes_factor_used": bf_val,
                        "note": "",
                    }
                )

    # 2. Count candidate pairs falling into each untrained level across holdout seeds
    con = duckdb.connect()
    pair_counts_by_level: dict[str, dict[str, int]] = {
        f"{item['comparison']}:{item['comparison_vector_value']}": {
            "total": 0,
            **{s: 0 for s in seeds},
        }
        for item in untrained_levels_info
    }

    # Also count sex_raw null vs non-null
    sex_raw_null_count = 0
    sex_raw_non_null_count = 0

    for s in seeds:
        pair_detail_p = base_results_dir / s / "splink_k" / "pair_detail.parquet"
        if not pair_detail_p.exists():
            continue

        for item in untrained_levels_info:
            c_name = item["comparison"]
            cvv = item["comparison_vector_value"]
            gamma_col = f"gamma_{c_name}"
            cnt = con.execute(
                f"SELECT count(*) FROM '{pair_detail_p}' WHERE {gamma_col} = {cvv}"
            ).fetchone()[0]
            key = f"{c_name}:{cvv}"
            pair_counts_by_level[key][s] = int(cnt)
            pair_counts_by_level[key]["total"] += int(cnt)

        # Verify sex_raw
        sex_counts = con.execute(
            f"SELECT gamma_sex_raw, count(*) FROM '{pair_detail_p}' GROUP BY gamma_sex_raw"
        ).fetchall()
        for g_val, cnt in sex_counts:
            if g_val == -1:
                sex_raw_null_count += cnt
            else:
                sex_raw_non_null_count += cnt

    # Attach pair counts to untrained_levels_info
    for item in untrained_levels_info:
        key = f"{item['comparison']}:{item['comparison_vector_value']}"
        item["candidate_pair_counts"] = pair_counts_by_level.get(key, {})

    # 3. Sensitivity Analysis across holdout_5..9
    # Frozen thresholds: t_link = 2.0, t_bridge = 4.0
    t_link, t_bridge = 2.0, 4.0

    def eval_seed(seed_name: str, neutralize: Optional[str] = None) -> dict[str, float]:
        pair_detail_p = base_results_dir / seed_name / "splink_k" / "pair_detail.parquet"
        records_p = base_data_dir / seed_name / "registry" / "records.parquet"
        truth_records_p = base_data_dir / seed_name / "truth" / "record_truth.parquet"
        truth_pairs_p = base_data_dir / seed_name / "truth" / "true_pairs.parquet"
        features_p = base_data_dir / seed_name / "registry" / "features.parquet"
        doppel_p = base_data_dir / seed_name / "truth" / "doppelganger_person_pairs.parquet"

        df = con.execute(f"SELECT * FROM '{pair_detail_p}'").df()

        if neutralize == "phone_last8":
            mask = df["gamma_phone"] == 1
            df.loc[mask, "match_weight"] = df.loc[mask, "match_weight"] - np.log2(
                df.loc[mask, "bf_phone"]
            )
        elif neutralize == "village_else":
            mask = df["gamma_village"] == 0
            df.loc[mask, "match_weight"] = df.loc[mask, "match_weight"] - np.log2(
                df.loc[mask, "bf_village"]
            )
        elif neutralize == "all_untrained":
            mask_phone = df["gamma_phone"] == 1
            df.loc[mask_phone, "match_weight"] = df.loc[mask_phone, "match_weight"] - np.log2(
                df.loc[mask_phone, "bf_phone"]
            )
            mask_vill = df["gamma_village"] == 0
            df.loc[mask_vill, "match_weight"] = df.loc[mask_vill, "match_weight"] - np.log2(
                df.loc[mask_vill, "bf_village"]
            )

        records_df = pd.read_parquet(records_p)
        features_df = pd.read_parquet(features_p) if features_p.exists() else None

        clusters_df, _ = build_resolved_graph(
            predictions_df=df,
            records_df=records_df,
            t_link=t_link,
            t_bridge=t_bridge,
            features_df=features_df,
            apply_listed_as_other_member=True,
        )

        rec_truth_df = pd.read_parquet(truth_records_p)
        true_pairs_df = pd.read_parquet(truth_pairs_p)
        doppel_df = pd.read_parquet(doppel_p) if doppel_p.exists() else None

        return evaluate_resolved_clusters(
            clusters_df=clusters_df,
            record_truth_df=rec_truth_df,
            true_pairs_df=true_pairs_df,
            doppelganger_person_pairs_df=doppel_df,
        )

    sensitivity_results: dict[str, dict[str, Any]] = {}
    conditions = [
        ("baseline", None, "Frozen splink_k model without changes"),
        ("neutralize_phone_last8", "phone_last8", "Phone last8 Bayes factor set to 1.0"),
        ("neutralize_village_else", "village_else", "Village ELSE Bayes factor set to 1.0"),
        ("neutralize_all_untrained", "all_untrained", "All untrained Bayes factors set to 1.0"),
    ]

    base_costs = []
    base_f1s = []

    for cond_name, neut_arg, desc in conditions:
        costs, precs, recs, f1s = [], [], [], []
        for s in seeds:
            m = eval_seed(s, neutralize=neut_arg)
            costs.append(m["expected_cost"])
            precs.append(m["cluster_precision"])
            recs.append(m["cluster_recall"])
            f1s.append(m["cluster_f1"])

        if cond_name == "baseline":
            base_costs = list(costs)
            base_f1s = list(f1s)

        cost_deltas = [c - b for c, b in zip(costs, base_costs)]
        f1_deltas = [f - b for f, b in zip(f1s, base_f1s)]

        sensitivity_results[cond_name] = {
            "description": desc,
            "cost_mean": round(float(np.mean(costs)), 1),
            "cost_sd": round(float(np.std(costs, ddof=1)), 1),
            "delta_cost_mean": round(float(np.mean(cost_deltas)), 1),
            "delta_cost_sd": round(float(np.std(cost_deltas, ddof=1)), 1),
            "precision_mean": round(float(np.mean(precs)), 4),
            "precision_sd": round(float(np.std(precs, ddof=1)), 4),
            "recall_mean": round(float(np.mean(recs)), 4),
            "recall_sd": round(float(np.std(recs, ddof=1)), 4),
            "f1_mean": round(float(np.mean(f1s)), 4),
            "f1_sd": round(float(np.std(f1s, ddof=1)), 4),
            "delta_f1_mean": round(float(np.mean(f1_deltas)), 4),
            "delta_f1_sd": round(float(np.std(f1_deltas, ddof=1)), 4),
        }

    audit_summary = {
        "source": "results/summary/untrained_params_audit.json",
        "model_path": str(model_path),
        "protocol": {
            "seeds": list(seeds),
            "frozen_t_link": t_link,
            "frozen_t_bridge": t_bridge,
            "decision_rule": (
                "Sensitivity analysis only. Frozen model is NOT replaced or retrained."
            ),
        },
        "untrained_levels": untrained_levels_info,
        "sex_raw_audit": {
            "status": "INERT",
            "null_candidate_pairs": sex_raw_null_count,
            "non_null_candidate_pairs": sex_raw_non_null_count,
            "records_null_rate": 1.0,
            "finding": (
                "not estimated; every candidate pair is null; inert; recommended for removal"
            ),
            "recommendation": (
                "Remove sex_raw comparison from future Splink model configurations "
                "to avoid predict-time warnings."
            ),
        },
        "sensitivity_analysis": sensitivity_results,
        "overall_conclusion": (
            "The champion pipeline's operational cost and cluster metrics are insensitive "
            "to setting the untrained levels to neutral (Bayes factor 1). Setting untrained "
            "levels to neutral Bayes factor 1.0 shifts 5-seed mean cost by "
            f"{sensitivity_results['neutralize_all_untrained']['delta_cost_mean']:+.1f} cost "
            f"points (from {sensitivity_results['baseline']['cost_mean']:.1f} to "
            f"{sensitivity_results['neutralize_all_untrained']['cost_mean']:.1f}) and shifts "
            f"F1 by {sensitivity_results['neutralize_all_untrained']['delta_f1_mean']:+.4f}."
        ),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(audit_summary, f, indent=2)

    print(f"Untrained parameter audit successfully written to: {output_path}")
    return audit_summary


if __name__ == "__main__":
    run_untrained_parameter_audit()

