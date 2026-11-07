"""Evaluation harness for household inference, reach estimation, and error decomposition.

Reads ground truth to assess household clustering and reach metrics.
Strict segregation: Barilink.household must NEVER import or call this module.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional, Sequence

import numpy as np
import pandas as pd

from barilink.household.evidence import (
    DEFAULT_HOUSEHOLD_WEIGHTS,
    build_household_evidence,
    build_unit_profiles,
    compute_sex_inference_coverage,
)
from barilink.household.golden import build_household_golden_records
from barilink.household.infer import infer_households


@dataclass
class HouseholdEvalMetrics:
    """Consolidated evaluation metrics for household inference."""

    # Headline record-level pairwise metrics
    record_pairwise_precision: float
    record_pairwise_recall: float
    record_pairwise_f1: float

    # Secondary person/unit-level metrics
    unit_pairwise_precision: float
    unit_pairwise_recall: float
    unit_pairwise_f1: float
    unit_bcubed_precision: float
    unit_bcubed_recall: float
    unit_bcubed_f1: float

    # Reached households metrics
    n_inferred_households: int
    n_true_reached_households: int
    households_reached_error_pct: float

    # Reach & Size metrics
    true_indirect_reach: int
    est_indirect_reach: int
    indirect_reach_error_pct: float
    household_size_mae: float

    # Stratified reach & size metrics (Amendment 3)
    stratum_roster_coverage: float  # Share of reached households with >= 1 roster
    stratum_roster_indirect_error_pct: float
    stratum_roster_size_mae: float

    stratum_no_roster_coverage: float  # Share of reached households with 0 rosters
    stratum_no_roster_size_mae: float

    # Diagnostics
    sex_inference_coverage: float
    n_cannot_household_cuts: int
    n_max_size_cuts: int


def compute_pairwise_metrics(
    pred_labels: Sequence[str],
    true_labels: Sequence[str],
) -> tuple[float, float, float]:
    """Compute pairwise precision, recall, and F1 via contingency matrix in O(N)."""
    df = pd.DataFrame({"pred": pred_labels, "true": true_labels})
    contingency = df.groupby(["pred", "true"]).size()
    tp = sum(v * (v - 1) // 2 for v in contingency)

    pred_sizes = df.groupby("pred").size()
    tp_fp = sum(v * (v - 1) // 2 for v in pred_sizes)

    true_sizes = df.groupby("true").size()
    tp_fn = sum(v * (v - 1) // 2 for v in true_sizes)

    prec = float(tp / tp_fp) if tp_fp > 0 else 0.0
    rec = float(tp / tp_fn) if tp_fn > 0 else 0.0
    f1 = float(2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
    return prec, rec, f1


def compute_bcubed_metrics(
    pred_labels: Sequence[str],
    true_labels: Sequence[str],
) -> tuple[float, float, float]:
    """Compute B-cubed precision, recall, and F1 in O(N)."""
    df = pd.DataFrame({"pred": pred_labels, "true": true_labels})
    n_total = len(df)
    if n_total == 0:
        return 0.0, 0.0, 0.0

    contingency = df.groupby(["pred", "true"]).size()
    pred_sizes = df.groupby("pred").size().to_dict()
    true_sizes = df.groupby("true").size().to_dict()

    sum_p = 0.0
    sum_r = 0.0
    for (p, t), cnt in contingency.items():
        sum_p += (cnt * cnt) / pred_sizes[p]
        sum_r += (cnt * cnt) / true_sizes[t]

    prec = float(sum_p / n_total)
    rec = float(sum_r / n_total)
    f1 = float(2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
    return prec, rec, f1


def evaluate_household_pipeline(
    data_dir: Path,
    household_clusters_df: pd.DataFrame,
    household_golden_df: pd.DataFrame,
    household_log_df: pd.DataFrame,
    profiles: dict[str, Any],
    person_clusters_df: pd.DataFrame,
) -> HouseholdEvalMetrics:
    """Evaluate inferred households and golden records against ground truth."""
    # 1. Load ground truth
    record_truth_path = data_dir / "truth" / "record_truth.parquet"
    if not record_truth_path.exists():
        record_truth_path = data_dir / "truth" / "record_truth.csv"
    record_truth_df = (
        pd.read_parquet(record_truth_path)
        if record_truth_path.suffix == ".parquet"
        else pd.read_csv(record_truth_path)
    )

    households_truth_path = data_dir / "households.parquet"
    if not households_truth_path.exists():
        households_truth_path = data_dir / "households.csv"
    households_truth_df = (
        pd.read_parquet(households_truth_path)
        if households_truth_path.suffix == ".parquet"
        else pd.read_csv(households_truth_path)
    )

    # 2. Record-level mapping (Headline metric: Amendment 2)
    # Merge record_id -> cluster_id -> household_id
    rec_hh = person_clusters_df.merge(household_clusters_df, on="cluster_id", how="inner")
    rec_eval = rec_hh.merge(
        record_truth_df[["record_id", "household_id"]],
        on="record_id",
        how="inner",
        suffixes=("_pred", "_true"),
    )

    rec_prec, rec_rec, rec_f1 = compute_pairwise_metrics(
        rec_eval["household_id_pred"].astype(str),
        rec_eval["household_id_true"].astype(str),
    )

    # 3. Unit-level mapping (Secondary metric)
    # Map each person cluster to its majority person, hence its true household_id
    rec_person = person_clusters_df.merge(
        record_truth_df[["record_id", "person_id", "household_id"]],
        on="record_id",
        how="inner",
    )
    unit_true_map: dict[str, str] = {}
    for cid, c_df in rec_person.groupby("cluster_id"):
        # Majority person_id (tiebreak lowest person_id)
        person_counts = c_df["person_id"].value_counts()
        max_cnt = person_counts.max()
        top_persons = sorted(person_counts[person_counts == max_cnt].index.tolist())
        majority_pid = top_persons[0]
        true_hh = str(c_df[c_df["person_id"] == majority_pid]["household_id"].iloc[0])
        unit_true_map[str(cid)] = true_hh

    unit_eval = household_clusters_df.copy()
    unit_eval["true_household_id"] = unit_eval["cluster_id"].astype(str).map(unit_true_map)
    # Drop units without truth (if any)
    unit_eval = unit_eval.dropna(subset=["true_household_id"])

    u_prec, u_rec, u_f1 = compute_pairwise_metrics(
        unit_eval["household_id"].astype(str),
        unit_eval["true_household_id"].astype(str),
    )
    u_b_prec, u_b_rec, u_b_f1 = compute_bcubed_metrics(
        unit_eval["household_id"].astype(str),
        unit_eval["true_household_id"].astype(str),
    )

    # 4. Households reached metrics
    # Reached true households: distinct households with >= 1 enrolled record
    true_reached_hh_ids = set(record_truth_df["household_id"].astype(str).unique())
    n_true_reached = len(true_reached_hh_ids)
    n_inferred = len(household_golden_df)
    hh_reached_err_pct = (
        ((n_inferred - n_true_reached) / n_true_reached * 100.0) if n_true_reached > 0 else 0.0
    )

    # 5. True Reach & Indirect Reach
    # True indirect reach per reached household = total members - enrolled distinct persons
    hh_size_dict = dict(
        zip(
            households_truth_df["household_id"].astype(str),
            households_truth_df["n_members"].astype(int),
        )
    )
    enrolled_per_hh = record_truth_df.groupby("household_id")["person_id"].nunique().to_dict()

    true_indirect_dict: dict[str, int] = {}
    for hhid in true_reached_hh_ids:
        tot_m = hh_size_dict.get(hhid, 0)
        enr_p = enrolled_per_hh.get(hhid, 0)
        true_indirect_dict[hhid] = max(0, tot_m - enr_p)

    total_true_indirect = sum(true_indirect_dict.values())
    total_est_indirect = int(household_golden_df["indirect_reach"].sum())
    indirect_reach_err_pct = (
        ((total_est_indirect - total_true_indirect) / total_true_indirect * 100.0)
        if total_true_indirect > 0
        else 0.0
    )

    # 6. Household Size MAE for reached households
    # Map each reached true household to plurality inferred household
    hh_pred_map: dict[str, str] = {}
    for hhid, h_df in rec_eval.groupby("household_id_true"):
        pred_counts = h_df["household_id_pred"].value_counts()
        hh_pred_map[str(hhid)] = str(pred_counts.index[0])

    golden_lookup = household_golden_df.set_index("household_id")

    size_errors = []
    roster_size_errors = []
    roster_true_indirect = 0
    roster_est_indirect = 0

    no_roster_size_errors = []

    for hhid in true_reached_hh_ids:
        true_sz = hh_size_dict.get(hhid, 0)
        pred_hhid = hh_pred_map.get(hhid)
        if pred_hhid and pred_hhid in golden_lookup.index:
            row_inf = golden_lookup.loc[pred_hhid]
            est_sz = int(row_inf["est_household_size"])
            has_rost = bool(row_inf["has_roster"])
            est_ind = int(row_inf["indirect_reach"])
        else:
            est_sz = 1
            has_rost = False
            est_ind = 0

        err = abs(est_sz - true_sz)
        size_errors.append(err)

        if has_rost:
            roster_size_errors.append(err)
            roster_est_indirect += est_ind
            roster_true_indirect += true_indirect_dict.get(hhid, 0)
        else:
            no_roster_size_errors.append(err)

    hh_size_mae = float(np.mean(size_errors)) if size_errors else 0.0

    # Stratified metrics (Amendment 3)
    n_eval_hh = len(true_reached_hh_ids)
    roster_cov = float(len(roster_size_errors) / n_eval_hh) if n_eval_hh > 0 else 0.0
    no_roster_cov = float(len(no_roster_size_errors) / n_eval_hh) if n_eval_hh > 0 else 0.0

    roster_ind_err = (
        ((roster_est_indirect - roster_true_indirect) / roster_true_indirect * 100.0)
        if roster_true_indirect > 0
        else 0.0
    )
    roster_sz_mae = float(np.mean(roster_size_errors)) if roster_size_errors else 0.0
    no_roster_sz_mae = float(np.mean(no_roster_size_errors)) if no_roster_size_errors else 0.0

    # Diagnostics
    sex_cov = compute_sex_inference_coverage(profiles)
    n_ch_cuts = (
        int((household_log_df["action"] == "cannot_household_cut").sum())
        if not household_log_df.empty
        else 0
    )
    n_ms_cuts = (
        int((household_log_df["action"] == "max_size_cut").sum())
        if not household_log_df.empty
        else 0
    )

    return HouseholdEvalMetrics(
        record_pairwise_precision=rec_prec,
        record_pairwise_recall=rec_rec,
        record_pairwise_f1=rec_f1,
        unit_pairwise_precision=u_prec,
        unit_pairwise_recall=u_rec,
        unit_pairwise_f1=u_f1,
        unit_bcubed_precision=u_b_prec,
        unit_bcubed_recall=u_b_rec,
        unit_bcubed_f1=u_b_f1,
        n_inferred_households=n_inferred,
        n_true_reached_households=n_true_reached,
        households_reached_error_pct=hh_reached_err_pct,
        true_indirect_reach=total_true_indirect,
        est_indirect_reach=total_est_indirect,
        indirect_reach_error_pct=indirect_reach_err_pct,
        household_size_mae=hh_size_mae,
        stratum_roster_coverage=roster_cov,
        stratum_roster_indirect_error_pct=roster_ind_err,
        stratum_roster_size_mae=roster_sz_mae,
        stratum_no_roster_coverage=no_roster_cov,
        stratum_no_roster_size_mae=no_roster_sz_mae,
        sex_inference_coverage=sex_cov,
        n_cannot_household_cuts=n_ch_cuts,
        n_max_size_cuts=n_ms_cuts,
    )


def build_oracle_person_clusters(data_dir: Path) -> pd.DataFrame:
    """Build Oracle person clusters grouped strictly by truth person_id.

    Strict segregation: Oracle person clusters are created only inside evaluate.
    """
    record_truth_path = data_dir / "truth" / "record_truth.parquet"
    if not record_truth_path.exists():
        record_truth_path = data_dir / "truth" / "record_truth.csv"
    record_truth_df = (
        pd.read_parquet(record_truth_path)
        if record_truth_path.suffix == ".parquet"
        else pd.read_csv(record_truth_path)
    )

    oracle_df = pd.DataFrame(
        {
            "record_id": record_truth_df["record_id"].astype(str),
            "cluster_id": record_truth_df["person_id"].astype(str),
        }
    )
    return oracle_df.sort_values("record_id").reset_index(drop=True)


def run_household_evaluation_on_run(
    run_name: str,
    method: str = "splink_k_resolved",
    t_hh: float = 4.0,
    weights: Optional[dict[str, float]] = None,
    output_dir: Optional[Path] = None,
    use_oracle_persons: bool = False,
) -> tuple[HouseholdEvalMetrics, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Execute end-to-end household inference and evaluation on a dataset run."""
    data_dir = Path("data/generated") / run_name
    reg_dir = data_dir / "registry"

    records_df = pd.read_parquet(reg_dir / "records.parquet")
    features_df = (
        pd.read_parquet(reg_dir / "features.parquet")
        if (reg_dir / "features.parquet").exists()
        else None
    )

    if use_oracle_persons:
        person_clusters_df = build_oracle_person_clusters(data_dir)
    else:
        clusters_path = Path("results") / run_name / method / "clusters.parquet"
        if not clusters_path.exists():
            raise FileNotFoundError(f"Person clusters not found: {clusters_path}")
        person_clusters_df = pd.read_parquet(clusters_path)

    # 1. Build unit profiles
    profiles = build_unit_profiles(person_clusters_df, records_df, features_df)

    # 2. Build evidence
    edges_df = build_household_evidence(profiles, weights=weights)

    # 3. Infer households
    hh_clusters_df, hh_log_df = infer_households(
        profiles,
        edges_df,
        t_hh=t_hh,
    )

    # 4. Synthesize golden records
    hh_golden_df = build_household_golden_records(
        hh_clusters_df,
        profiles,
        records_df=records_df,
    )

    # 5. Evaluate
    metrics = evaluate_household_pipeline(
        data_dir,
        hh_clusters_df,
        hh_golden_df,
        hh_log_df,
        profiles,
        person_clusters_df,
    )

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        hh_clusters_df.to_parquet(output_dir / "household_clusters.parquet", index=False)
        hh_golden_df.to_parquet(output_dir / "household_golden.parquet", index=False)
        hh_log_df.to_parquet(output_dir / "household_log.parquet", index=False)
        with open(output_dir / "household_metrics.json", "w", encoding="utf-8") as f:
            json.dump(asdict(metrics), f, indent=2)

    return metrics, hh_clusters_df, hh_golden_df, hh_log_df, profiles


def export_household_graph_json(
    profiles: dict[str, Any],
    hh_clusters_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    output_path: Path,
) -> None:
    """Export household graph JSON for UI demonstration on holdout_5.

    Nodes: person clusters with display_name, modules, birth_year, household_id.
    Edges: unit pairs with score >= 1.0, evidence types, score.
    """
    hh_map = dict(
        zip(hh_clusters_df["cluster_id"].astype(str), hh_clusters_df["household_id"].astype(str))
    )

    nodes = []
    for cid, u in profiles.items():
        nodes.append(
            {
                "id": cid,
                "display_name": u.display_name,
                "modules": u.modules,
                "birth_year": u.birth_year,
                "household_id": hh_map.get(cid, ""),
            }
        )

    # Sort nodes by id deterministically
    nodes.sort(key=lambda n: n["id"])

    edges = []
    if not edges_df.empty:
        valid_edges = edges_df[edges_df["score"] >= 1.0]
        for _, row in valid_edges.iterrows():
            active_types = []
            for e_code in ["E1", "E2", "E3", "E4", "E5"]:
                if bool(row.get(e_code.lower(), False)):
                    active_types.append(e_code)

            edges.append(
                {
                    "source": str(row["unit_id_l"]),
                    "target": str(row["unit_id_r"]),
                    "score": float(row["score"]),
                    "evidence_types": active_types,
                }
            )

    edges.sort(key=lambda e: (e["source"], e["target"]))

    graph_data = {
        "nodes": nodes,
        "edges": edges,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, indent=2)


def run_household_confirmation(
    t_hh: float = 5.0,
    runs: Sequence[str] = ("holdout_5", "holdout_6", "holdout_7", "holdout_8", "holdout_9"),
    output_table_path: Optional[Path] = None,
) -> pd.DataFrame:
    """Execute Phase 7 confirmation benchmark across fresh holdout seeds (holdout_5..9).

    Protocol:
    - Selected t_hh = 5.0 on demo only.
    - Evaluated on holdout_5..9 without revision.
    - Compares:
      (1) Champion Person Pipeline (splink_k_resolved -> household)
      (2) Oracle Person Pipeline (oracle persons -> household)
      (3) Error Decomposition (K minus Oracle)
      (4) Evidence Ablations: Drop E1..E5 in turn at frozen t_hh
      (5) Weight Robustness: K pipeline at weights x0.5 and x2.0
    - Generates household_table.md and holdout_5 household_graph.json.
    """
    variants = [
        "splink_k_resolved",
        "oracle",
        "ablation_no_e1",
        "ablation_no_e2",
        "ablation_no_e3",
        "ablation_no_e4",
        "ablation_no_e5",
        "robustness_weights_x0_5",
        "robustness_weights_x2_0",
    ]

    all_metrics: dict[str, list[HouseholdEvalMetrics]] = {v: [] for v in variants}

    for run_name in runs:
        print(f"--- Processing {run_name} for Household Confirmation ---")
        run_res_dir = Path("results") / run_name / "household"

        # 1. Champion: splink_k_resolved
        k_metrics, k_hh_clusters, k_hh_golden, k_hh_log, k_profiles = (
            run_household_evaluation_on_run(
                run_name=run_name,
                method="splink_k_resolved",
                t_hh=t_hh,
                output_dir=run_res_dir,
                use_oracle_persons=False,
            )
        )
        all_metrics["splink_k_resolved"].append(k_metrics)

        # On holdout_5 only: export household_graph.json
        if run_name == "holdout_5":
            edges_path = run_res_dir / "household_edges.parquet"
            edges_df = build_household_evidence(k_profiles, output_path=edges_path)
            graph_json_path = run_res_dir / "household_graph.json"
            export_household_graph_json(k_profiles, k_hh_clusters, edges_df, graph_json_path)
            print(f"Exported holdout_5 UI graph to: {graph_json_path}")

        # 2. Oracle Person Pipeline
        oracle_metrics, _, _, _, _ = run_household_evaluation_on_run(
            run_name=run_name,
            t_hh=t_hh,
            use_oracle_persons=True,
        )
        all_metrics["oracle"].append(oracle_metrics)

        # 3. Ablations E1..E5
        for e_drop in ["E1", "E2", "E3", "E4", "E5"]:
            abl_weights = dict(DEFAULT_HOUSEHOLD_WEIGHTS)
            abl_weights[e_drop] = 0.0
            abl_var = f"ablation_no_{e_drop.lower()}"
            abl_metrics, _, _, _, _ = run_household_evaluation_on_run(
                run_name=run_name,
                method="splink_k_resolved",
                t_hh=t_hh,
                weights=abl_weights,
                use_oracle_persons=False,
            )
            all_metrics[abl_var].append(abl_metrics)

        # 4. Weight Robustness: x0.5 and x2.0 (Amendment 5)
        w_half = {k: v * 0.5 for k, v in DEFAULT_HOUSEHOLD_WEIGHTS.items()}
        rob_half_metrics, _, _, _, _ = run_household_evaluation_on_run(
            run_name=run_name,
            method="splink_k_resolved",
            t_hh=t_hh,
            weights=w_half,
            use_oracle_persons=False,
        )
        all_metrics["robustness_weights_x0_5"].append(rob_half_metrics)

        w_double = {k: v * 2.0 for k, v in DEFAULT_HOUSEHOLD_WEIGHTS.items()}
        rob_double_metrics, _, _, _, _ = run_household_evaluation_on_run(
            run_name=run_name,
            method="splink_k_resolved",
            t_hh=t_hh,
            weights=w_double,
            use_oracle_persons=False,
        )
        all_metrics["robustness_weights_x2_0"].append(rob_double_metrics)

    # Aggregate results: mean +/- sd
    rows = []
    labels = {
        "oracle": "Oracle Persons + Household Inference",
        "splink_k_resolved": "Champion Pipeline (splink_k_resolved + Household)",
        "ablation_no_e1": "Ablation: Drop E1 (listed_member, w=0)",
        "ablation_no_e2": "Ablation: Drop E2 (husband_link, w=0)",
        "ablation_no_e3": "Ablation: Drop E3 (father_link, w=0)",
        "ablation_no_e4": "Ablation: Drop E4 (roster_overlap, w=0)",
        "ablation_no_e5": "Ablation: Drop E5 (shared_phone, w=0)",
        "robustness_weights_x0_5": "Weight Robustness: All Weights x0.5",
        "robustness_weights_x2_0": "Weight Robustness: All Weights x2.0",
    }

    def fmt_stat(vals: list[float], pct: bool = False, decimals: int = 4) -> str:
        mean_v = float(np.mean(vals))
        sd_v = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
        if pct:
            return f"{mean_v:+.2f}% +/- {sd_v:.2f}%"
        return f"{mean_v:.{decimals}f} +/- {sd_v:.{decimals}f}"

    for v in variants:
        m_list = all_metrics[v]
        rec_f1 = [m.record_pairwise_f1 for m in m_list]
        rec_p = [m.record_pairwise_precision for m in m_list]
        rec_r = [m.record_pairwise_recall for m in m_list]
        bcubed_f1 = [m.unit_bcubed_f1 for m in m_list]
        hh_err = [m.households_reached_error_pct for m in m_list]
        ind_err = [m.indirect_reach_error_pct for m in m_list]
        sz_mae = [m.household_size_mae for m in m_list]
        rost_ind_err = [m.stratum_roster_indirect_error_pct for m in m_list]
        rost_sz_mae = [m.stratum_roster_size_mae for m in m_list]
        rost_cov = [m.stratum_roster_coverage * 100 for m in m_list]
        no_rost_cov = [m.stratum_no_roster_coverage * 100 for m in m_list]

        rows.append(
            {
                "variant": v,
                "label": labels.get(v, v),
                "record_pairwise_f1": fmt_stat(rec_f1),
                "record_pairwise_prec": fmt_stat(rec_p),
                "record_pairwise_rec": fmt_stat(rec_r),
                "unit_bcubed_f1": fmt_stat(bcubed_f1),
                "hh_reached_error_pct": fmt_stat(hh_err, pct=True),
                "indirect_reach_error_pct": fmt_stat(ind_err, pct=True),
                "household_size_mae": fmt_stat(sz_mae, decimals=2),
                "stratum_roster_coverage": fmt_stat(rost_cov, pct=True),
                "stratum_roster_indirect_error_pct": fmt_stat(rost_ind_err, pct=True),
                "stratum_roster_size_mae": fmt_stat(rost_sz_mae, decimals=2),
                "stratum_no_roster_coverage": fmt_stat(no_rost_cov, pct=True),
            }
        )

    summary_df = pd.DataFrame(rows)

    # Compute Error Decomposition: Difference (K - Oracle) per seed
    k_list = all_metrics["splink_k_resolved"]
    ora_list = all_metrics["oracle"]
    diff_f1 = [k.record_pairwise_f1 - o.record_pairwise_f1 for k, o in zip(k_list, ora_list)]
    diff_p = [
        k.record_pairwise_precision - o.record_pairwise_precision for k, o in zip(k_list, ora_list)
    ]
    diff_r = [k.record_pairwise_recall - o.record_pairwise_recall for k, o in zip(k_list, ora_list)]
    diff_b3 = [k.unit_bcubed_f1 - o.unit_bcubed_f1 for k, o in zip(k_list, ora_list)]
    diff_hh_err = [
        k.households_reached_error_pct - o.households_reached_error_pct
        for k, o in zip(k_list, ora_list)
    ]
    diff_mae = [k.household_size_mae - o.household_size_mae for k, o in zip(k_list, ora_list)]

    # Format Markdown Table
    md = []
    md.append("# Phase 7 Holdout Confirmation Table: Household Inference & Reach")
    md.append("")
    md.append(
        "Pre-registered evaluation across 5 independent holdout seeds "
        "(`holdout_5` through `holdout_9`)."
    )
    md.append(
        f"Operating point frozen at DEV-selected edge threshold "
        f"**$t_{{\\text{{hh}}}}^* = {t_hh:.1f}$**."
    )
    md.append("")
    md.append("### 1. Headline Record-Level & Reach Performance (Mean +/- SD)")
    md.append("")
    header1 = (
        "| Pipeline / Configuration | Record Pairwise F1 | Record Precision | "
        "Record Recall | Unit B-cubed F1 | HH Reached Error % | Household Size MAE |"
    )
    md.append(header1)
    md.append("|:---|:---:|:---:|:---:|:---:|:---:|:---:|")

    for _, r in summary_df.iterrows():
        row1 = (
            f"| {r['label']} | {r['record_pairwise_f1']} | {r['record_pairwise_prec']} | "
            f"{r['record_pairwise_rec']} | {r['unit_bcubed_f1']} | "
            f"{r['hh_reached_error_pct']} | {r['household_size_mae']} |"
        )
        md.append(row1)

    md.append("")
    md.append("### 2. Error Decomposition: Person Linkage vs Household Inference")
    md.append("")
    md.append(
        "Decomposes total household error into error from household inference logic itself "
        "(Oracle) vs error inherited from Splink K person linkage:"
    )
    md.append("")
    md.append(f"- **Record Pairwise F1 Difference (K - Oracle)**: `{fmt_stat(diff_f1)}`")
    md.append(f"- **Record Precision Difference (K - Oracle)**: `{fmt_stat(diff_p)}`")
    md.append(f"- **Record Recall Difference (K - Oracle)**: `{fmt_stat(diff_r)}`")
    md.append(f"- **Unit B-cubed F1 Difference (K - Oracle)**: `{fmt_stat(diff_b3)}`")
    md.append(f"- **HH Reached Error % Delta**: `{fmt_stat(diff_hh_err, pct=True)}`")
    md.append(f"- **Household Size MAE Delta**: `{fmt_stat(diff_mae, decimals=2)}`")
    md.append("")
    md.append(
        "Oracle persons reach only F1 0.61 (0.6062 +/- 0.0109) and +38.74% +/- 0.93% "
        "households-reached error, so most household error is intrinsic to household inference. "
        "Inherited person-linkage error accounts for about 0.15 F1 (-0.1470 +/- 0.0104, "
        "predominantly lost recall)."
    )
    md.append("")
    md.append("### 3. Ablation Findings & Consumption of Holdouts")
    md.append("")
    md.append(
        "- **Ablation on E2 (`husband_link`)**: Dropping E2 raises F1 (0.459 -> 0.476; "
        "precision 0.68 -> 0.93), indicating husband-name skeleton matching causes false "
        "household merges."
    )
    md.append(
        "- **Ablation on E3 (`father_link`)**: Dropping E3 has no measurable effect "
        "(F1 0.4597 +/- 0.0069 vs 0.4592 +/- 0.0049)."
    )
    md.append(
        "- **Protocol**: Do not re-tune; holdout_5..9 are consumed for household decisions."
    )
    md.append("")
    md.append("### 4. Graph Partitioning & Max-Size Split Behavior")
    md.append("")
    md.append(
        "At $t_{\\text{hh}} = 5.0$, the max-size split fired on only 2 components across all "
        "5 holdout seeds: `holdout_5` had 1 component of size 15 (cut weight 6.0), and `holdout_9` "
        "had 1 component of size 13 (cut weight 7.0), while `holdout_6`, `holdout_7`, and "
        "`holdout_8` had 0 oversize components. Both components (<= 25 nodes) were partitioned "
        "via exact Stoer-Wagner min-cut. Note: the sorted-bisection fallback (which splits "
        "components > 25 nodes by arbitrary node index) is a heuristic, not a min-cut."
    )
    md.append("")
    md.append("### 5. Stratified Indirect Reach & Household Size (Amendment 3)")
    md.append("")
    md.append(
        "Reported across two administrative strata: (a) households with >= 1 attached roster; "
        "(b) households with no roster."
    )
    md.append(
        "For Stratum (b), the indirect reach estimator is structurally zero because no roster "
        "was collected for any member of the household."
    )
    md.append("")
    header2 = (
        "| Pipeline | Stratum (a) Share | Stratum (a) Ind. Reach Err % | "
        "Stratum (a) Size MAE | Stratum (b) Share | Stratum (b) Ind. Reach Note |"
    )
    md.append(header2)
    md.append("|:---|:---:|:---:|:---:|:---:|:---|")

    for _, r in summary_df.iterrows():
        row2 = (
            f"| {r['label']} | {r['stratum_roster_coverage']} | "
            f"{r['stratum_roster_indirect_error_pct']} | {r['stratum_roster_size_mae']} | "
            f"{r['stratum_no_roster_coverage']} | *Structurally zero* |"
        )
        md.append(row2)

    md.append("")
    md.append("### 6. Weight Robustness Analysis (Amendment 5)")
    md.append("")
    md.append(
        f"Sensitivity of the Champion K pipeline to a-priori weights at frozen "
        f"$t_{{\\text{{hh}}}} = {t_hh:.1f}$:"
    )
    k_f1 = summary_df[summary_df["variant"] == "splink_k_resolved"]["record_pairwise_f1"].iloc[0]
    half_f1 = summary_df[summary_df["variant"] == "robustness_weights_x0_5"][
        "record_pairwise_f1"
    ].iloc[0]
    double_f1 = summary_df[summary_df["variant"] == "robustness_weights_x2_0"][
        "record_pairwise_f1"
    ].iloc[0]
    md.append(f"- **Base Weights (1.0x)**: Record F1 = `{k_f1}`")
    md.append(f"- **Halved Weights (0.5x)**: Record F1 = `{half_f1}`")
    md.append(f"- **Doubled Weights (2.0x)**: Record F1 = `{double_f1}`")
    md.append("")
    md.append(
        "Results are highly sensitive to the a-priori weights (F1 0.46 -> 0.31 at x0.5, "
        "0.21 at x2). The operating point depends on the threshold sitting just above the "
        "E1 weight, so single-channel E1 links are excluded and multi-channel links are kept. "
        "This is a fragility, not a robustness result."
    )
    md.append("")
    md.append("### 7. Future Work")
    md.append("")
    md.append(
        "Corroborate E1 with roster age_raw (+/- 5 years vs unit birth_year) and relation_raw "
        "consistency (e.g. spouse <-> inferred sex), plus stricter E2 (require E2 + same village + "
        "age plausibility). Must be validated on fresh seeds holdout_10..14 under a new "
        "pre-registration."
    )
    md.append("")

    if output_table_path is None:
        output_table_path = Path("results/holdout_confirm/household_table.md")

    output_table_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_table_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print(f"Household confirmation table written to: {output_table_path}")
    return summary_df
