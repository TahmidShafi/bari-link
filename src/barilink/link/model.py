"""Splink 4 probabilistic record linkage model specification, training, and prediction.

Uses DuckDB backend and Splink 4 API only.
Reads only model-visible inputs from registry/ and features.parquet.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional, Sequence

import pandas as pd
import splink.blocking_analysis as ba
import splink.comparison_level_library as cll
import splink.comparison_library as cl
from splink import DuckDBAPI, Linker, SettingsCreator, block_on


def create_splink_settings(config: dict[str, Any]) -> SettingsCreator:
    """Create Splink 4 SettingsCreator object with 9 comparisons and 5 blocking rules."""
    link_cfg = config.get("linkage", {})
    use_tf: bool = link_cfg.get("use_term_frequency", True)
    use_kinship: bool = link_cfg.get("use_kinship", True)
    jw_thresholds: Sequence[float] = link_cfg.get("jw_thresholds", [0.92, 0.85])
    jw_village: float = link_cfg.get("jw_village_threshold", 0.88)

    # 1. Given Name
    c_given = cl.CustomComparison(
        comparison_levels=[
            cll.NullLevel("name_canon"),
            cll.ExactMatchLevel("name_canon", term_frequency_adjustments=use_tf),
            cll.ExactMatchLevel("name_skeleton"),
            cll.ExactMatchLevel("name_tokens_sorted"),
            cll.JaroWinklerLevel("name_canon", distance_threshold=jw_thresholds[0]),
            cll.JaroWinklerLevel("name_canon", distance_threshold=jw_thresholds[1]),
            cll.ElseLevel(),
        ],
        output_column_name="given_name",
    )

    # 2. Guardian Name
    c_guardian = cl.CustomComparison(
        comparison_levels=[
            cll.NullLevel("guardian_canon"),
            cll.ExactMatchLevel("guardian_canon", term_frequency_adjustments=use_tf),
            cll.ExactMatchLevel("guardian_skeleton"),
            cll.JaroWinklerLevel("guardian_canon", distance_threshold=jw_thresholds[0]),
            cll.JaroWinklerLevel("guardian_canon", distance_threshold=jw_thresholds[1]),
            cll.ElseLevel(),
        ],
        output_column_name="guardian_name",
    )

    # 3. Kinship (Amendment 1)
    # (a) both rosters null
    # (b) roster intersect >= 2
    # (c) cross-household evidence
    # (d) roster intersect >= 1
    # (e) else
    kin_null_level = cll.CustomLevel(
        "roster_skels_l IS NULL AND roster_skels_r IS NULL",
        label_for_charts="Both rosters null",
    )
    kin_null_level.is_null_level = True

    c_kinship = cl.CustomComparison(
        comparison_levels=[
            kin_null_level,
            cll.CustomLevel(
                "coalesce(len(list_intersect(roster_skels_l, roster_skels_r)), 0) >= 2",
                label_for_charts="Roster intersect >= 2",
            ),
            cll.CustomLevel(
                "coalesce(list_contains(roster_skels_l, guardian_skeleton_r), false) "
                "OR coalesce(list_contains(roster_skels_r, guardian_skeleton_l), false)",
                label_for_charts="Cross-household guardian match",
            ),
            cll.CustomLevel(
                "coalesce(len(list_intersect(roster_skels_l, roster_skels_r)), 0) >= 1",
                label_for_charts="Roster intersect >= 1",
            ),
            cll.ElseLevel(),
        ],
        output_column_name="kinship",
    )

    # 4. Phone
    c_phone = cl.CustomComparison(
        comparison_levels=[
            cll.NullLevel("phone_norm"),
            cll.ExactMatchLevel("phone_norm"),
            cll.ExactMatchLevel("phone_last8"),
            cll.ElseLevel(),
        ],
        output_column_name="phone",
    )

    # 5. Birth Year
    c_year = cl.CustomComparison(
        comparison_levels=[
            cll.NullLevel("birth_year_est"),
            cll.ExactMatchLevel("birth_year_est"),
            cll.AbsoluteDifferenceLevel("birth_year_est", difference_threshold=2),
            cll.AbsoluteDifferenceLevel("birth_year_est", difference_threshold=5),
            cll.ElseLevel(),
        ],
        output_column_name="birth_year",
    )

    # 6. Village
    c_village = cl.CustomComparison(
        comparison_levels=[
            cll.NullLevel("village_canon"),
            cll.ExactMatchLevel("village_canon"),
            cll.JaroWinklerLevel("village_canon", distance_threshold=jw_village),
            cll.ElseLevel(),
        ],
        output_column_name="village",
    )

    # 7. Union
    c_union = cl.ExactMatch("union_raw")

    # 8. Sex
    c_sex = cl.ExactMatch("sex_raw")

    # 9. Title Token
    c_title = cl.ExactMatch("title_token")

    comparisons = [c_given, c_guardian]
    if use_kinship:
        comparisons.append(c_kinship)
    comparisons.extend([c_phone, c_year, c_village, c_union, c_sex, c_title])

    # 5 Prediction Blocking Rules
    blocking_rules = [
        block_on("given_first_skel", "village_canon"),
        block_on("phone_norm"),
        block_on("guardian_skeleton", "village_canon"),
        block_on("name_skeleton", "union_raw"),
        block_on("given_first_skel", "birth_year_est"),
    ]

    return SettingsCreator(
        link_type="dedupe_only",
        unique_id_column_name="record_id",
        comparisons=comparisons,
        blocking_rules_to_generate_predictions=blocking_rules,
        retain_intermediate_calculation_columns=True,
    )


def train_splink_model(
    features_df: pd.DataFrame,
    config: dict[str, Any],
    output_model_path: str | Path,
    threads: Optional[int] = None,
) -> Linker:
    """Train Splink model on dev features and export model JSON."""
    db_api = DuckDBAPI()
    if threads is not None:
        db_api._con.execute(f"SET threads = {threads}")

    settings = create_splink_settings(config)
    linker = Linker(features_df, settings, db_api)

    link_cfg = config.get("linkage", {})
    prob_recall = link_cfg.get("prob_random_match_recall", 0.60)
    u_max_pairs = int(link_cfg.get("u_max_pairs", 2000000))
    seed = int(config.get("seed", 42))

    # Step 1: Prior probability
    linker.training.estimate_probability_two_random_records_match(
        ["l.phone_norm = r.phone_norm AND l.name_skeleton = r.name_skeleton"],
        recall=prob_recall,
    )

    # Step 2: Estimate u
    linker.training.estimate_u_using_random_sampling(max_pairs=u_max_pairs, seed=seed)

    # Step 3: Expectation Maximisation sessions
    linker.training.estimate_parameters_using_expectation_maximisation(
        block_on("phone_norm"),
        fix_u_probabilities=True,
    )
    linker.training.estimate_parameters_using_expectation_maximisation(
        block_on("name_skeleton", "village_canon"),
        fix_u_probabilities=True,
    )

    # Save trained model to JSON
    out_p = Path(output_model_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    linker.misc.save_model_to_json(str(out_p), overwrite=True)

    return linker


def predict_splink_model(
    features_df: pd.DataFrame,
    model_settings_or_path: Any,
    run_name: str,
    base_results_dir: str = "results",
    threads: Optional[int] = None,
) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    """Score candidate pairs using trained Splink model and persist prediction parquets."""
    db_api = DuckDBAPI()
    if threads is not None:
        db_api._con.execute(f"SET threads = {threads}")

    if isinstance(model_settings_or_path, (str, Path)):
        linker = Linker(features_df, str(model_settings_or_path), db_api)
    else:
        linker = Linker(features_df, model_settings_or_path, db_api)

    # Candidate pair count across prediction blocking rules
    rules = linker._settings_obj._blocking_rules_to_generate_predictions
    rules_sql = [getattr(r, "blocking_rule_sql", str(r)) for r in rules]
    cum_df = ba.cumulative_comparisons_to_be_scored_from_blocking_rules_data(
        table_or_tables=[features_df],
        blocking_rules=rules_sql,
        link_type="dedupe_only",
        db_api=db_api,
        unique_id_column_name="record_id",
    )
    candidate_pair_count = int(cum_df["cumulative_rows"].iloc[-1]) if not cum_df.empty else 0

    # Inference predict
    splink_df = linker.inference.predict()
    pair_detail_df = splink_df.as_pandas_dataframe()

    # Format predictions conforming to Phase 3 contract
    # Ensure record_id_l < record_id_r
    preds_records = []
    for _, row in pair_detail_df.iterrows():
        id_l = str(row["record_id_l"])
        id_r = str(row["record_id_r"])
        p = float(row["match_probability"])
        w = float(row.get("match_weight", 0.0))
        if id_l > id_r:
            id_l, id_r = id_r, id_l
        preds_records.append({
            "record_id_l": id_l,
            "record_id_r": id_r,
            "match_probability": p,
            "match_weight": w,
        })

    predictions_df = pd.DataFrame(preds_records)
    if not predictions_df.empty:
        predictions_df = (
            predictions_df.sort_values(
                by=["match_probability", "record_id_l"], ascending=[False, True]
            )
            .drop_duplicates(subset=["record_id_l", "record_id_r"])
            .reset_index(drop=True)
        )
    else:
        predictions_df = pd.DataFrame(
            columns=["record_id_l", "record_id_r", "match_probability", "match_weight"]
        )

    # Persist outputs
    out_dir = Path(base_results_dir) / run_name / "splink_v1"
    out_dir.mkdir(parents=True, exist_ok=True)
    preds_path = out_dir / "predictions.parquet"
    detail_path = out_dir / "pair_detail.parquet"
    meta_path = out_dir / "metadata.json"

    predictions_df.to_parquet(preds_path, engine="pyarrow", index=False)
    pair_detail_df.to_parquet(detail_path, engine="pyarrow", index=False)

    meta = {
        "method": "splink_v1",
        "run_name": run_name,
        "candidate_pair_count": candidate_pair_count,
        "scored_pairs": len(predictions_df),
        "blocking_rules_summary": cum_df.to_dict(orient="records"),
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    return predictions_df, pair_detail_df, candidate_pair_count
