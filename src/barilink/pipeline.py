"""Reproducible pipeline runner and determinism verification for bari-link."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import yaml

from barilink.corrupt.registry import export_registries
from barilink.evaluate.household_eval import (
    export_household_graph_json,
    run_household_evaluation_on_run,
)
from barilink.evaluate.report import generate_resolved_evaluation_report
from barilink.export.web import export_web_data
from barilink.generate.population import generate_population
from barilink.link.model import predict_splink_model
from barilink.link.normalise import export_features
from barilink.resolve.golden import build_golden_records
from barilink.resolve.graph import build_resolved_graph


def _validate_publish_spec(spec_path: Path) -> dict[str, Any]:
    """Validate that the frozen publish specification exists and matches committed artifacts."""
    if not spec_path.exists():
        raise FileNotFoundError(
            f"Frozen publish spec missing: {spec_path}. Never falling back to defaults."
        )

    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    # 1. Validate model artifact
    model_path = Path(spec["model_path"])
    if not model_path.exists():
        raise FileNotFoundError(
            f"Frozen model artifact missing: {model_path}. Never falling back to defaults."
        )
    with open(model_path, "r", encoding="utf-8") as mf:
        model_json = json.load(mf)

    # Assert no kinship comparison present in model JSON
    comp_names = [c.get("output_column_name") for c in model_json.get("comparisons", [])]
    if "kinship" in comp_names:
        raise ValueError(
            "Assertion failed: model JSON contains a 'kinship' comparison, "
            "violating frozen Pipeline K specification."
        )

    # 2. Validate resolution threshold artifact
    res_thresh_path = Path(spec["resolve_thresholds_path"])
    if not res_thresh_path.exists():
        raise FileNotFoundError(
            f"Frozen resolve thresholds missing: {res_thresh_path}. "
            f"Never falling back to defaults."
        )
    with open(res_thresh_path, "r", encoding="utf-8") as rtf:
        res_thresh = json.load(rtf)
    if "t_link" not in res_thresh or "t_bridge" not in res_thresh:
        raise ValueError(f"Invalid resolve thresholds in {res_thresh_path}")

    # 3. Validate household threshold artifact
    hh_thresh_path = Path(spec["household_thresholds_path"])
    if not hh_thresh_path.exists():
        raise FileNotFoundError(
            f"Frozen household thresholds missing: {hh_thresh_path}. "
            f"Never falling back to defaults."
        )
    with open(hh_thresh_path, "r", encoding="utf-8") as htf:
        hh_thresh = json.load(htf)
    if "t_hh" not in hh_thresh:
        raise ValueError(f"Invalid household thresholds in {hh_thresh_path}")

    return spec


def run_pipeline(
    profile: str = "publish",
    run_name: Optional[str] = None,
    config_path: Optional[str] = None,
    base_data_dir: str = "data/generated",
    base_results_dir: str = "results",
    web_dir: str = "web/public/data",
) -> dict[str, Any]:
    """Execute the complete reproducible end-to-end pipeline.

    Profiles:
      - publish: Full run on holdout_5 using strictly frozen published artifacts.
      - ci: Fast smoke-test on configs/ci.yaml (500 households, seed offset 9000).
    """
    if profile not in ("publish", "ci"):
        raise ValueError(f"Unknown profile '{profile}'. Choices: 'publish', 'ci'.")

    spec_path = Path("results/publish/publish_spec.json")
    spec = _validate_publish_spec(spec_path)

    if profile == "publish":
        selected_run_name = run_name or "holdout_5"
        selected_config = config_path or "configs/default.yaml"
        seed_offset = 1005
        role = "holdout"
    else:  # profile == "ci"
        selected_run_name = run_name or "ci"
        selected_config = config_path or "configs/ci.yaml"
        seed_offset = 9000
        role = "holdout"

    print("\n" + "=" * 70)
    print(f"RUNNING REPRODUCIBLE PIPELINE (Profile: {profile.upper()})")
    print("=" * 70)
    print(f"Run Name:     {selected_run_name}")
    print(f"Config:       {selected_config}")
    print(f"Seed Offset:  {seed_offset}")
    print(f"Role:         {role}")
    print(f"Model Path:   {spec['model_path']}")

    # -------------------------------------------------------------------------
    # 1. Build: Generate synthetic population & corrupt registries
    # -------------------------------------------------------------------------
    out_dir = Path(base_data_dir) / selected_run_name
    print(f"\n[Step 1/8] Generating population and corrupted registries -> {out_dir}")
    generate_population(
        config_path=selected_config,
        output_dir=out_dir,
        seed_offset=seed_offset,
        role=role,
    )
    with open(selected_config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    export_registries(
        config_path=selected_config,
        run_name=selected_run_name,
        base_data_dir=base_data_dir,
        seed_offset=seed_offset,
        role=role,
    )

    # -------------------------------------------------------------------------
    # 2. Features: Normalisation and skeleton features
    # -------------------------------------------------------------------------
    print(f"\n[Step 2/8] Normalising records and computing features -> {out_dir / 'registry'}")
    export_features(run_name=selected_run_name, base_data_dir=base_data_dir)

    # -------------------------------------------------------------------------
    # 3. Predict: Splink K model prediction
    # -------------------------------------------------------------------------
    print(f"\n[Step 3/8] Running Splink K inference using frozen model -> {spec['model_path']}")
    feat_path = out_dir / "registry" / "features.parquet"
    features_df = pd.read_parquet(feat_path)
    predict_splink_model(
        features_df=features_df,
        model_settings_or_path=spec["model_path"],
        run_name=selected_run_name,
        base_results_dir=base_results_dir,
        method="splink_k",
    )

    # -------------------------------------------------------------------------
    # 4. Resolve: Min-cut resolution at frozen thresholds
    # -------------------------------------------------------------------------
    res_thresh_path = Path(spec["resolve_thresholds_path"])
    with open(res_thresh_path, "r", encoding="utf-8") as rtf:
        res_thresh = json.load(rtf)
    t_link = float(res_thresh["t_link"])
    t_bridge = float(res_thresh["t_bridge"])
    max_gap = int(spec["max_birth_year_gap"])

    print(
        f"\n[Step 4/8] Resolving entity clusters at frozen t_link={t_link}, "
        f"t_bridge={t_bridge}"
    )
    preds_p = (
        Path(base_results_dir) / selected_run_name / "splink_k" / "predictions.parquet"
    )
    preds_df = pd.read_parquet(preds_p)
    recs_p = out_dir / "registry" / "records.parquet"
    records_df = pd.read_parquet(recs_p)
    feat_p = out_dir / "registry" / "features.parquet"
    features_df = pd.read_parquet(feat_p) if feat_p.exists() else None

    resolved_clusters_df, resolution_log_df = build_resolved_graph(
        predictions_df=preds_df,
        records_df=records_df,
        t_link=t_link,
        t_bridge=t_bridge,
        max_birth_year_gap=max_gap,
        features_df=features_df,
        apply_listed_as_other_member=True,
    )
    res_dir = Path(base_results_dir) / selected_run_name / "splink_k_resolved"
    res_dir.mkdir(parents=True, exist_ok=True)
    resolved_clusters_df.to_parquet(res_dir / "clusters.parquet", index=False)
    resolution_log_df.to_parquet(res_dir / "resolution_log.parquet", index=False)

    # -------------------------------------------------------------------------
    # 5. Golden Records: Attribute survivorship and provenance lineage
    # -------------------------------------------------------------------------
    print(f"\n[Step 5/8] Generating golden records -> {res_dir / 'golden_records.parquet'}")
    build_golden_records(
        clusters_df=resolved_clusters_df,
        records_df=records_df,
        features_df=features_df,
        resolution_log_df=resolution_log_df,
        predictions_df=preds_df,
        output_path=res_dir / "golden_records.parquet",
    )

    # -------------------------------------------------------------------------
    # 6. Household Inference: Graph cuts at frozen t_hh
    # -------------------------------------------------------------------------
    hh_thresh_path = Path(spec["household_thresholds_path"])
    with open(hh_thresh_path, "r", encoding="utf-8") as htf:
        hh_thresh = json.load(htf)
    t_hh = float(hh_thresh["t_hh"])
    hh_weights = spec["household_weights"]

    hh_res_dir = Path(base_results_dir) / selected_run_name / "household"
    hh_res_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n[Step 6/8] Inferring households at frozen t_hh={t_hh} -> {hh_res_dir}")

    hh_metrics, hh_clusters, hh_golden, _, profiles = run_household_evaluation_on_run(
        run_name=selected_run_name,
        method="splink_k_resolved",
        t_hh=t_hh,
        weights=hh_weights,
        output_dir=hh_res_dir,
        base_data_dir=base_data_dir,
        base_results_dir=base_results_dir,
    )

    # Export graph json for UI visualization
    from barilink.household.evidence import build_household_evidence

    edges_df = build_household_evidence(
        profiles, output_path=hh_res_dir / "household_edges.parquet"
    )
    export_household_graph_json(
        profiles, hh_clusters, edges_df, hh_res_dir / "household_graph.json"
    )

    # -------------------------------------------------------------------------
    # 7. Evaluate: Evaluate linkage metrics in report mode
    # -------------------------------------------------------------------------
    print(f"\n[Step 7/8] Evaluating person linkage metrics -> {res_dir / 'metrics.json'}")
    link_metrics = generate_resolved_evaluation_report(
        run_name=selected_run_name,
        method="splink_k_resolved",
        base_data_dir=base_data_dir,
        base_results_dir=base_results_dir,
        config=cfg,
    )

    # -------------------------------------------------------------------------
    # 8. Web Export: Bundle all model-visible and evaluation assets
    # -------------------------------------------------------------------------
    print(f"\n[Step 8/8] Exporting web assets -> {web_dir}")
    manifest = export_web_data(
        run_name=selected_run_name,
        output_dir=web_dir,
        data_dir=base_data_dir,
        results_dir=base_results_dir,
        model_path=spec["model_path"],
        t_bridge=t_bridge,
        max_birth_year_gap=max_gap,
    )

    summary = {
        "profile": profile,
        "run_name": selected_run_name,
        "person_linkage": link_metrics.get("headline_metrics_at_t_cost", {}),
        "household_inference": {
            "record_pairwise_f1": hh_metrics.record_pairwise_f1,
            "record_pairwise_precision": hh_metrics.record_pairwise_precision,
            "record_pairwise_recall": hh_metrics.record_pairwise_recall,
            "unit_bcubed_f1": hh_metrics.unit_bcubed_f1,
            "households_reached_error_pct": hh_metrics.households_reached_error_pct,
            "household_size_mae": hh_metrics.household_size_mae,
            "n_inferred_households": hh_metrics.n_inferred_households,
        },
        "manifest": manifest,
    }

    # -------------------------------------------------------------------------
    # Cross-Check & Baseline Generation (Amendment 2)
    # -------------------------------------------------------------------------
    if profile == "publish" and selected_run_name == "holdout_5":
        print("\n--- Verifying cross-check against confirmed holdout_5 metrics ---")
        p_cost = summary["person_linkage"]["expected_cost"]
        if abs(p_cost - 784.0) > 0.5:
            raise ValueError(
                f"Cross-check failed: person linkage cost {p_cost} != expected 784.0"
            )
        print("  ✓ Person linkage expected cost matches confirm_table (784.0)")

        # Write results/publish/expected_headline.json from pipeline output
        expected_headline = {
            "schema_version": "1.0",
            "run_name": selected_run_name,
            "role": role,
            "seed_offset": seed_offset,
            "operating_points": {
                "person_linkage": {
                    "method": "splink_k_resolved",
                    "t_link": t_link,
                    "t_bridge": t_bridge,
                },
                "household_inference": {
                    "t_hh": t_hh,
                },
            },
            "metrics": {
                "person_linkage": {
                    "cluster_precision": summary["person_linkage"]["cluster_precision"],
                    "cluster_recall": summary["person_linkage"]["cluster_recall"],
                    "cluster_f1": summary["person_linkage"]["cluster_f1"],
                    "expected_cost": summary["person_linkage"]["expected_cost"],
                    "false_merge_clusters": summary["person_linkage"]["false_merge_clusters"],
                    "split_persons": summary["person_linkage"]["split_persons"],
                    "dedup_reach": summary["person_linkage"]["dedup_reach"],
                    "doppelganger_false_merge_rate": summary["person_linkage"][
                        "doppelganger_false_merge_rate"
                    ],
                },
                "household_inference": {
                    "record_pairwise_precision": hh_metrics.record_pairwise_precision,
                    "record_pairwise_recall": hh_metrics.record_pairwise_recall,
                    "record_pairwise_f1": hh_metrics.record_pairwise_f1,
                    "unit_bcubed_f1": hh_metrics.unit_bcubed_f1,
                    "households_reached_error_pct": hh_metrics.households_reached_error_pct,
                    "household_size_mae": hh_metrics.household_size_mae,
                    "n_inferred_households": hh_metrics.n_inferred_households,
                },
            },
            "determinism_note": (
                "File hashes are not used for cross-OS validation because DuckDB/Arrow parquet "
                "encodings, floating-point LSBs in Splink EM, and platform newlines vary between "
                "Windows and Linux. Determinism is asserted via semantic equivalence within "
                "0.005 tolerance."
            ),
        }
        exp_path = Path("results/publish/expected_headline.json")
        exp_path.parent.mkdir(parents=True, exist_ok=True)
        with open(exp_path, "w", encoding="utf-8") as f:
            json.dump(expected_headline, f, indent=2)
        print(f"Written verified expected headline to: {exp_path}")

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70 + "\n")
    return summary


def verify_pipeline(
    run_name: Optional[str] = None,
    results_dir: str = "results",
    expected_path: Optional[str] = None,
) -> bool:
    """Verify that current run metrics match committed results/publish/expected_headline.json."""
    selected_run_name = run_name or "holdout_5"
    exp_file = (
        Path(expected_path)
        if expected_path
        else Path("results/publish/expected_headline.json")
    )
    if not exp_file.exists():
        raise FileNotFoundError(
            f"Expected headline file not found: {exp_file}. Run 'pipeline --profile publish' first."
        )

    with open(exp_file, "r", encoding="utf-8") as f:
        expected = json.load(f)

    # Load actual person linkage metrics
    p_metrics_path = (
        Path(results_dir) / selected_run_name / "splink_k_resolved" / "metrics.json"
    )
    if not p_metrics_path.exists():
        raise FileNotFoundError(
            f"Actual person linkage metrics not found: {p_metrics_path}"
        )
    with open(p_metrics_path, "r", encoding="utf-8") as f:
        p_metrics_dict = json.load(f)
    actual_p = p_metrics_dict.get("headline_metrics_at_t_cost", {})

    # Load actual household inference metrics
    hh_metrics_path = (
        Path(results_dir) / selected_run_name / "household" / "household_metrics.json"
    )
    if not hh_metrics_path.exists():
        raise FileNotFoundError(
            f"Actual household metrics not found: {hh_metrics_path}"
        )
    with open(hh_metrics_path, "r", encoding="utf-8") as f:
        actual_hh = json.load(f)

    exp_p = expected["metrics"]["person_linkage"]
    exp_hh = expected["metrics"]["household_inference"]

    print("\n" + "=" * 70)
    print("PIPELINE DETERMINISM VERIFICATION")
    print("=" * 70)
    print(f"Run Name:      {selected_run_name}")
    print(f"Expected File: {exp_file}")
    print("Tolerance:     Rates/F1 <= 0.005, Counts <= 1.0%")
    print("-" * 70)
    print(f"{'Metric':<32} {'Expected':<12} {'Actual':<12} {'Diff':<10} {'Status'}")
    print("-" * 70)

    all_passed = True

    def check_float(name: str, exp_val: float, act_val: float, tol: float = 0.005):
        nonlocal all_passed
        diff = abs(exp_val - act_val)
        passed = diff <= tol
        if not passed:
            all_passed = False
        status = "PASS" if passed else "FAIL"
        print(f"{name:<32} {exp_val:<12.4f} {act_val:<12.4f} {diff:<10.4f} {status}")

    def check_count(name: str, exp_val: int, act_val: int, pct_tol: float = 0.01):
        nonlocal all_passed
        diff = abs(exp_val - act_val)
        allowed = max(1, int(exp_val * pct_tol))
        passed = diff <= allowed
        if not passed:
            all_passed = False
        status = "PASS" if passed else "FAIL"
        print(f"{name:<32} {exp_val:<12d} {act_val:<12d} {diff:<10d} {status}")

    # Person linkage checks
    check_float(
        "Person Cluster Precision",
        exp_p["cluster_precision"],
        actual_p["cluster_precision"],
    )
    check_float(
        "Person Cluster Recall",
        exp_p["cluster_recall"],
        actual_p["cluster_recall"],
    )
    check_float("Person Cluster F1", exp_p["cluster_f1"], actual_p["cluster_f1"])
    check_float(
        "Person Expected Cost",
        exp_p["expected_cost"],
        actual_p["expected_cost"],
        tol=0.5,
    )
    check_count(
        "False-Merge Clusters",
        exp_p["false_merge_clusters"],
        actual_p["false_merge_clusters"],
    )
    check_count("Split Persons", exp_p["split_persons"], actual_p["split_persons"])
    check_count("Dedup Reach (Clusters)", exp_p["dedup_reach"], actual_p["dedup_reach"])
    check_float(
        "Doppelganger FM Rate",
        exp_p["doppelganger_false_merge_rate"],
        actual_p["doppelganger_false_merge_rate"],
    )

    # Household inference checks
    check_float(
        "Household Record Precision",
        exp_hh["record_pairwise_precision"],
        actual_hh["record_pairwise_precision"],
    )
    check_float(
        "Household Record Recall",
        exp_hh["record_pairwise_recall"],
        actual_hh["record_pairwise_recall"],
    )
    check_float(
        "Household Record F1",
        exp_hh["record_pairwise_f1"],
        actual_hh["record_pairwise_f1"],
    )
    check_float(
        "Household Unit B-cubed F1",
        exp_hh["unit_bcubed_f1"],
        actual_hh["unit_bcubed_f1"],
    )
    check_float(
        "Household Size MAE",
        exp_hh["household_size_mae"],
        actual_hh["household_size_mae"],
        tol=0.05,
    )
    check_float(
        "Household Reached Error %",
        exp_hh["households_reached_error_pct"],
        actual_hh["households_reached_error_pct"],
        tol=0.5,
    )
    check_count(
        "Inferred Households",
        exp_hh["n_inferred_households"],
        actual_hh["n_inferred_households"],
    )

    print("-" * 70)
    if all_passed:
        print("ALL METRICS WITHIN TOLERANCE -> VERIFICATION PASSED ✓\n")
        return True
    else:
        print("ONE OR MORE METRICS EXCEEDED TOLERANCE -> VERIFICATION FAILED ✗\n")
        return False
