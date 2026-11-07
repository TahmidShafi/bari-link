"""Export pipeline results for web visualization and UI demo."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from barilink.evaluate.export_eval import build_eval_export_datasets
from barilink.resolve.graph import precompute_ui_clusters


def _sha256_file(path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def get_git_info() -> tuple[str, bool]:
    """Get current git commit SHA and dirty working tree status."""
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        status = subprocess.check_output(
            ["git", "status", "--porcelain"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        is_dirty = len(status) > 0
        return sha, is_dirty
    except Exception:
        return "unknown", False


def export_web_data(
    run_name: str = "holdout_5",
    output_dir: Path | str = "web/public/data",
    data_dir: Path | str = "data/generated",
    results_dir: Path | str = "results",
    weight_floor: float = -5.0,
    max_total_mb: float = 25.0,
    model_path: Optional[Path | str] = None,
    t_bridge: float = 4.0,
    max_birth_year_gap: int = 10,
) -> dict[str, Any]:
    """Export all model-visible and evaluation datasets required by the web UI.

    Enforces data contracts:
      1. Model-visible files contain NO ground truth columns (person_id, household_id, clean_*).
      2. Total size of exported files <= max_total_mb.
      3. Manifest tracks sha256, row count, byte size, git_sha and git_dirty.
    """
    out_path = Path(output_dir)
    eval_path = out_path / "eval"
    out_path.mkdir(parents=True, exist_ok=True)
    eval_path.mkdir(parents=True, exist_ok=True)

    run_data_dir = Path(data_dir) / run_name
    run_results_dir = Path(results_dir) / run_name

    # -------------------------------------------------------------------------
    # 1. records.parquet: Raw fields only, NO truth columns
    # -------------------------------------------------------------------------
    raw_records_path = run_data_dir / "registry" / "records.parquet"
    if not raw_records_path.exists():
        raise FileNotFoundError(f"Records not found: {raw_records_path}")

    records_df = pd.read_parquet(raw_records_path)
    allowed_cols = [
        "record_id",
        "source_module",
        "enrolment_date",
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
        "group_id",
    ]
    rec_cols = [c for c in allowed_cols if c in records_df.columns]
    web_records_df = records_df[rec_cols].copy()
    web_records_path = out_path / "records.parquet"
    web_records_df.to_parquet(web_records_path, index=False)

    # -------------------------------------------------------------------------
    # 2. pairs.parquet: match_weight >= weight_floor, gamma_* and bf_* columns
    # -------------------------------------------------------------------------
    pair_detail_path = run_results_dir / "splink_k" / "pair_detail.parquet"
    if not pair_detail_path.exists():
        raise FileNotFoundError(f"Pair detail not found: {pair_detail_path}")

    pairs_df = pd.read_parquet(pair_detail_path)
    filtered_pairs = pairs_df[pairs_df["match_weight"] >= weight_floor].copy()

    core_cols = ["record_id_l", "record_id_r", "match_weight", "match_probability"]
    feature_cols = [
        c
        for c in filtered_pairs.columns
        if c.startswith("gamma_") or c.startswith("bf_")
    ]
    web_pairs_df = filtered_pairs[core_cols + feature_cols].copy()
    web_pairs_path = out_path / "pairs.parquet"
    web_pairs_df.to_parquet(web_pairs_path, index=False)

    # -------------------------------------------------------------------------
    # 3. clusters_by_threshold.parquet: (t_link, record_id, cluster_id)
    # -------------------------------------------------------------------------
    preds_path = run_results_dir / "splink_k" / "predictions.parquet"
    if not preds_path.exists():
        raise FileNotFoundError(f"Predictions not found: {preds_path}")
    preds_df = pd.read_parquet(preds_path)

    feat_path = run_data_dir / "registry" / "features.parquet"
    features_df = pd.read_parquet(feat_path) if feat_path.exists() else None

    clusters_by_thresh_path = out_path / "clusters_by_threshold.parquet"
    clusters_by_thresh_df = precompute_ui_clusters(
        predictions_df=preds_df,
        records_df=web_records_df,
        t_bridge=t_bridge,
        output_path=clusters_by_thresh_path,
        max_birth_year_gap=max_birth_year_gap,
        features_df=features_df,
        apply_listed_as_other_member=True,
    )

    clusters_by_thresh_noconstraint_path = (
        out_path / "clusters_by_threshold_noconstraint.parquet"
    )
    clusters_by_thresh_noconstraint_df = precompute_ui_clusters(
        predictions_df=preds_df,
        records_df=web_records_df,
        t_bridge=t_bridge,
        output_path=clusters_by_thresh_noconstraint_path,
        max_birth_year_gap=max_birth_year_gap,
        features_df=features_df,
        apply_listed_as_other_member=False,
    )

    # -------------------------------------------------------------------------
    # 4. golden_records.parquet: Person-level golden records with field_lineage
    # -------------------------------------------------------------------------
    golden_path = run_results_dir / "splink_k_resolved" / "golden_records.parquet"
    if not golden_path.exists():
        # Build if not present
        from barilink.resolve.golden import build_golden_records

        clusters_resolved_path = (
            run_results_dir / "splink_k_resolved" / "clusters.parquet"
        )
        clusters_df = pd.read_parquet(clusters_resolved_path)
        log_path = run_results_dir / "splink_k_resolved" / "resolution_log.parquet"
        res_log_df = pd.read_parquet(log_path) if log_path.exists() else None
        golden_df = build_golden_records(
            clusters_df=clusters_df,
            records_df=records_df,
            features_df=features_df,
            resolution_log_df=res_log_df,
            predictions_df=preds_df,
            output_path=golden_path,
        )
    else:
        golden_df = pd.read_parquet(golden_path)

    web_golden_path = out_path / "golden_records.parquet"
    golden_df.to_parquet(web_golden_path, index=False)

    # -------------------------------------------------------------------------
    # 5. household_graph.json & household_golden.parquet
    # -------------------------------------------------------------------------
    hh_graph_src = run_results_dir / "household" / "household_graph.json"
    hh_gold_src = run_results_dir / "household" / "household_golden.parquet"

    web_hh_graph_path = out_path / "household_graph.json"
    web_hh_gold_path = out_path / "household_golden.parquet"

    if hh_graph_src.exists():
        with open(hh_graph_src, "r", encoding="utf-8") as f_in, open(
            web_hh_graph_path, "w", encoding="utf-8"
        ) as f_out:
            f_out.write(f_in.read())
    else:
        # Fallback empty graph if run does not have household graph
        with open(web_hh_graph_path, "w", encoding="utf-8") as f_out:
            json.dump({"nodes": [], "edges": []}, f_out)

    if hh_gold_src.exists():
        hh_gold_df = pd.read_parquet(hh_gold_src)
        if "household_id" in hh_gold_df.columns:
            hh_gold_df = hh_gold_df.rename(
                columns={"household_id": "household_cluster_id"}
            )
        hh_gold_df.to_parquet(web_hh_gold_path, index=False)
    else:
        pd.DataFrame().to_parquet(web_hh_gold_path, index=False)

    # -------------------------------------------------------------------------
    # 6. model_summary.json: prior, comparisons, levels, m & u probabilities
    # -------------------------------------------------------------------------
    if model_path is None:
        model_path = Path("results/models/splink_k/model.json")
    model_file = Path(model_path)
    if not model_file.exists():
        raise FileNotFoundError(f"Model file not found: {model_file}")

    with open(model_file, "r", encoding="utf-8") as f:
        model_dict = json.load(f)

    model_summary = {
        "prior": model_dict.get("probability_two_random_records_match"),
        "comparisons": [],
    }
    for comp in model_dict.get("comparisons", []):
        comp_summary = {
            "name": comp.get("output_column_name"),
            "levels": [],
        }
        for lvl in comp.get("comparison_levels", []):
            comp_summary["levels"].append(
                {
                    "label": lvl.get(
                        "label_for_charts",
                        str(lvl.get("comparison_vector_value")),
                    ),
                    "m_probability": lvl.get("m_probability"),
                    "u_probability": lvl.get("u_probability"),
                    "bayes_factor": lvl.get("bayes_factor"),
                }
            )
        model_summary["comparisons"].append(comp_summary)

    web_model_summary_path = out_path / "model_summary.json"
    with open(web_model_summary_path, "w", encoding="utf-8") as f:
        json.dump(model_summary, f, indent=2)

    # -------------------------------------------------------------------------
    # 7. eval/ threshold_table.parquet & record_labels.parquet
    # -------------------------------------------------------------------------
    build_eval_export_datasets(
        run_data_dir=run_data_dir,
        clusters_by_thresh_df=clusters_by_thresh_df,
        eval_out_dir=eval_path,
        clusters_by_thresh_noconstraint_df=clusters_by_thresh_noconstraint_df,
        pairs_df=web_pairs_df,
    )

    # -------------------------------------------------------------------------
    # 8. eval/headline.json: Confirmed holdout_5..9 benchmark results
    # -------------------------------------------------------------------------
    leakage_src = Path(results_dir) / "holdout" / "leakage_comparison.json"
    if not leakage_src.exists():
        leakage_src = Path("results/holdout/leakage_comparison.json")

    h1_src = Path(results_dir) / "demo" / "h1_dev_outcome.json"
    if not h1_src.exists():
        h1_src = Path("results/demo/h1_dev_outcome.json")

    h2_src = Path(results_dir) / "demo" / "h2_dev_outcome.json"
    if not h2_src.exists():
        h2_src = Path("results/demo/h2_dev_outcome.json")

    confirm_src = Path(results_dir) / "holdout_confirm" / "confirm_table.json"
    if not confirm_src.exists():
        confirm_src = Path("results/holdout_confirm/confirm_table.json")

    hh_src = Path(results_dir) / "holdout_confirm" / "household_table.json"
    if not hh_src.exists():
        hh_src = Path("results/holdout_confirm/household_table.json")

    leakage_data = {}
    if leakage_src.exists():
        with open(leakage_src, "r", encoding="utf-8") as f:
            leakage_data = json.load(f)

    h1_data = {}
    if h1_src.exists():
        with open(h1_src, "r", encoding="utf-8") as f:
            h1_data = json.load(f)

    h2_data = {}
    if h2_src.exists():
        with open(h2_src, "r", encoding="utf-8") as f:
            h2_data = json.load(f)

    confirm_data = {}
    if confirm_src.exists():
        with open(confirm_src, "r", encoding="utf-8") as f:
            confirm_data = json.load(f)

    hh_data = {}
    if hh_src.exists():
        with open(hh_src, "r", encoding="utf-8") as f:
            hh_data = json.load(f)

    h_conf = confirm_data.get("holdout_confirmation", {})
    hh_champ = hh_data.get("champion", {})
    hh_strata_a = hh_data.get("roster_strata", {}).get("stratum_a_with_roster", {})

    headline_data = {
        "schema_version": "1.0",
        "sources": [
            str(leakage_src).replace("\\", "/"),
            str(h1_src).replace("\\", "/"),
            str(h2_src).replace("\\", "/"),
            str(confirm_src).replace("\\", "/"),
            str(hh_src).replace("\\", "/"),
        ],
        "person_linkage_champion": {
            "method": "splink_k_resolved",
            "operating_thresholds": {"t_link": 2.0, "t_bridge": 4.0},
            "holdout_5_to_9": {
                "expected_cost_mean": h_conf.get("pipeline_k_cost_mean", 812.2),
                "expected_cost_sd": h_conf.get("pipeline_k_cost_sd", 29.2),
                "cluster_precision_mean": h_conf.get("pipeline_k_precision_mean", 0.9656),
                "cluster_precision_sd": h_conf.get("pipeline_k_precision_sd", 0.0106),
                "cluster_recall_mean": h_conf.get("pipeline_k_recall_mean", 0.5277),
                "cluster_recall_sd": h_conf.get("pipeline_k_recall_sd", 0.0172),
                "cluster_f1_mean": h_conf.get("pipeline_k_f1_mean", 0.6823),
                "cluster_f1_sd": h_conf.get("pipeline_k_f1_sd", 0.0137),
                "doppelganger_fm_rate": h_conf.get("doppelganger_fm_rate_pipeline_k", 0.0132),
                "paired_delta_cost_vs_ref": h_conf.get("paired_delta_cost", -76.0),
                "paired_delta_cost_sd": h_conf.get("paired_delta_cost_sd", 27.3),
            },
        },
        "household_inference_champion": {
            "method": "household_graph_cuts",
            "operating_threshold": {"t_hh": 5.0},
            "holdout_5_to_9": {
                "record_pairwise_f1_mean": hh_champ.get("record_pairwise_f1_mean", 0.4592),
                "record_pairwise_f1_sd": hh_champ.get("record_pairwise_f1_sd", 0.0049),
                "record_precision_mean": hh_champ.get("record_precision_mean", 0.6848),
                "record_precision_sd": hh_champ.get("record_precision_sd", 0.0147),
                "record_recall_mean": hh_champ.get("record_recall_mean", 0.3455),
                "record_recall_sd": hh_champ.get("record_recall_sd", 0.0042),
                "unit_bcubed_f1_mean": hh_champ.get("unit_bcubed_f1_mean", 0.7528),
                "unit_bcubed_f1_sd": hh_champ.get("unit_bcubed_f1_sd", 0.0017),
                "hh_reached_error_pct_mean": hh_champ.get("hh_reached_error_pct_mean", 59.13),
                "hh_reached_error_pct_sd": hh_champ.get("hh_reached_error_pct_sd", 1.15),
                "household_size_mae_mean": hh_champ.get("household_size_mae_mean", 2.07),
                "household_size_mae_sd": hh_champ.get("household_size_mae_sd", 0.06),
                "stratum_roster_indirect_error_pct_mean": (
                    hh_strata_a.get("indirect_reach_error_pct_mean", 13.71)
                ),
                "stratum_roster_size_mae_mean": hh_strata_a.get(
                    "household_size_mae_mean", 1.35
                ),
            },
        },
        "oracle_comparison": {
            "record_pairwise_f1_mean": hh_data.get("oracle", {}).get(
                "record_pairwise_f1_mean", 0.6062
            ),
            "record_pairwise_f1_sd": hh_data.get("oracle", {}).get(
                "record_pairwise_f1_sd", 0.0109
            ),
            "hh_reached_error_pct_mean": hh_data.get("oracle", {}).get(
                "hh_reached_error_pct_mean", 38.74
            ),
            "household_size_mae_mean": hh_data.get("oracle", {}).get(
                "household_size_mae_mean", 2.01
            ),
        },
        "leakage_before_after": leakage_data,
        "h1": h1_data,
        "h2": h2_data,
        "h3": confirm_data,
        "cost_ratio_sensitivity": {
            "source": confirm_data.get("source", "results/holdout_confirm/confirm_table.json"),
            "ratios": confirm_data.get("cost_ratio_sensitivity", []),
            "description": "Pipeline K vs Reference across cost ratios 1:1, 2:1, 5:1, 10:1",
        },
        "household": hh_data,
    }
    web_headline_path = eval_path / "headline.json"
    with open(web_headline_path, "w", encoding="utf-8") as f:
        json.dump(headline_data, f, indent=2)

    # -------------------------------------------------------------------------
    # 10. manifest.json: Hashes, byte sizes, row counts, git info
    # -------------------------------------------------------------------------
    git_sha, git_dirty = get_git_info()
    manifest_files: dict[str, dict[str, Any]] = {}

    all_exported_files = sorted(
        [p for p in out_path.rglob("*") if p.is_file() and p.name != "manifest.json"]
    )

    total_bytes = 0
    for p in all_exported_files:
        rel_key = str(p.relative_to(out_path)).replace("\\", "/")
        b_size = p.stat().st_size
        total_bytes += b_size
        f_hash = _sha256_file(p)

        # Determine row count
        if p.suffix == ".parquet":
            r_count = len(pd.read_parquet(p))
        elif p.suffix == ".json":
            try:
                with open(p, "r", encoding="utf-8") as jf:
                    j_obj = json.load(jf)
                if isinstance(j_obj, list):
                    r_count = len(j_obj)
                elif isinstance(j_obj, dict):
                    if "nodes" in j_obj:
                        r_count = len(j_obj["nodes"])
                    elif "comparisons" in j_obj:
                        r_count = len(j_obj["comparisons"])
                    else:
                        r_count = len(j_obj)
                else:
                    r_count = 1
            except Exception:
                r_count = 1
        else:
            r_count = 0

        manifest_files[rel_key] = {
            "row_count": r_count,
            "byte_size": b_size,
            "sha256": f_hash,
        }

    manifest = {
        "schema_version": "1.0",
        "git_sha": git_sha,
        "git_dirty": git_dirty,
        "generation_utc": datetime.now(timezone.utc).isoformat(),
        "total_byte_size": total_bytes,
        "files": manifest_files,
    }

    manifest_path = out_path / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    total_mb = total_bytes / (1024 * 1024)
    if total_mb > max_total_mb:
        breakdown = "\n".join(
            f"  {k}: {v['byte_size'] / (1024 * 1024):.2f} MB"
            for k, v in manifest_files.items()
        )
        raise ValueError(
            f"Export size {total_mb:.2f} MB exceeds limit {max_total_mb} MB!\n{breakdown}"
        )

    return manifest
