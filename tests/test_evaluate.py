"""Unit and integration tests for Phase 3 evaluation harness and baselines."""

import ast
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from barilink.evaluate.clusters import UnionFind, evaluate_clusters
from barilink.evaluate.contracts import validate_clusters, validate_predictions
from barilink.evaluate.pairwise import compute_pairwise_metrics_from_counts, evaluate_pairwise
from barilink.evaluate.report import generate_evaluation_report, run_threshold_sweep


def test_hand_verified_toy_case():
    """Verify exact hand-calculated metrics on the 5-record toy dataset.

    Records: a, b, c, d, e
    Truth persons: {a, b, c} (P1) and {d, e} (P2)
    Predicted clusters: {a, b} (C1) and {c, d, e} (C2)
    """
    record_truth_df = pd.DataFrame(
        [
            {"record_id": "a", "person_id": "P1"},
            {"record_id": "b", "person_id": "P1"},
            {"record_id": "c", "person_id": "P1"},
            {"record_id": "d", "person_id": "P2"},
            {"record_id": "e", "person_id": "P2"},
        ]
    )

    clusters_df = pd.DataFrame(
        [
            {"record_id": "a", "cluster_id": "C1"},
            {"record_id": "b", "cluster_id": "C1"},
            {"record_id": "c", "cluster_id": "C2"},
            {"record_id": "d", "cluster_id": "C2"},
            {"record_id": "e", "cluster_id": "C2"},
        ]
    )

    # Cluster metrics
    c_metrics = evaluate_clusters(clusters_df, record_truth_df)

    # Hand-verified fractions:
    # B-cubed Precision = 11/15 ~ 0.73333
    # B-cubed Recall = 11/15 ~ 0.73333
    # B-cubed F1 = 11/15 ~ 0.73333
    expected_bcubed = 11.0 / 15.0
    assert np.isclose(c_metrics.bcubed_precision, expected_bcubed, atol=1e-5)
    assert np.isclose(c_metrics.bcubed_recall, expected_bcubed, atol=1e-5)
    assert np.isclose(c_metrics.bcubed_f1, expected_bcubed, atol=1e-5)

    assert c_metrics.false_merge_clusters == 1
    assert c_metrics.false_merged_records == 1
    assert c_metrics.split_persons == 1

    # True pairs: (a,b), (a,c), (b,c), (d,e) -> 4 pairs
    true_pairs = {("a", "b"), ("a", "c"), ("b", "c"), ("d", "e")}
    rec_person_map = {"a": "P1", "b": "P1", "c": "P1", "d": "P2", "e": "P2"}

    dummy_preds = pd.DataFrame(
        [
            {"record_id_l": "a", "record_id_r": "b", "match_probability": 0.9},
            {"record_id_l": "c", "record_id_r": "d", "match_probability": 0.9},
            {"record_id_l": "c", "record_id_r": "e", "match_probability": 0.9},
            {"record_id_l": "d", "record_id_r": "e", "match_probability": 0.9},
        ]
    )

    pw_metrics = evaluate_pairwise(
        predictions_df=dummy_preds,
        true_pairs_set=true_pairs,
        clusters_df=clusters_df,
        record_person_map=rec_person_map,
        threshold=0.5,
    )

    # Hand-verified: TP=2, FP=2, FN=2 -> P=0.5, R=0.5, F1=0.5
    assert pw_metrics.tp == 2
    assert pw_metrics.fp == 2
    assert pw_metrics.fn == 2
    assert np.isclose(pw_metrics.precision, 0.5)
    assert np.isclose(pw_metrics.recall, 0.5)
    assert np.isclose(pw_metrics.f1, 0.5)


def test_cluster_vs_edge_pairwise():
    """Verify distinction between cluster-level pairs and edge-level pairs.

    A-B and B-C are scored above t, but A-C is not scored.
    Cluster-level includes A-C through transitive component {A, B, C}.
    Edge-level only counts scored pairs {A-B, B-C}.
    """
    records = ["A", "B", "C"]
    true_pairs_set = {("A", "B"), ("B", "C"), ("A", "C")}

    # Only A-B and B-C scored above threshold 0.5; A-C is not scored
    preds = pd.DataFrame(
        [
            {"record_id_l": "A", "record_id_r": "B", "match_probability": 0.8},
            {"record_id_l": "B", "record_id_r": "C", "match_probability": 0.8},
        ]
    )

    uf = UnionFind(
        records,
        record_person_map={"A": "P1", "B": "P1", "C": "P1"},
        person_total_counts={"P1": 3},
    )
    uf.union("A", "B")
    uf.union("B", "C")

    # Cluster-level: component has {A, B, C} -> 3 pairs total: AB, BC, AC -> all true
    assert uf.cluster_tp == 3
    assert uf.cluster_fp == 0

    clusters_df = pd.DataFrame(
        [
            {"record_id": "A", "cluster_id": "C1"},
            {"record_id": "B", "cluster_id": "C1"},
            {"record_id": "C", "cluster_id": "C1"},
        ]
    )

    pw = evaluate_pairwise(
        predictions_df=preds,
        true_pairs_set=true_pairs_set,
        clusters_df=clusters_df,
        record_person_map={"A": "P1", "B": "P1", "C": "P1"},
        threshold=0.5,
    )

    assert pw.tp == 3
    assert pw.precision == 1.0
    assert pw.recall == 1.0

    assert pw.edge_tp == 2
    assert pw.edge_fp == 0
    assert pw.edge_fn == 1
    assert pw.edge_precision == 1.0
    assert np.isclose(pw.edge_recall, 2.0 / 3.0)


def test_oracle_predictions():
    """Verify that oracle predictions achieve perfect scores."""
    record_truth_df = pd.DataFrame(
        [
            {"record_id": "r1", "person_id": "P1"},
            {"record_id": "r2", "person_id": "P1"},
            {"record_id": "r3", "person_id": "P2"},
            {"record_id": "r4", "person_id": "P2"},
        ]
    )
    doppel_df = pd.DataFrame([{"person_id_1": "P1", "person_id_2": "P2"}])
    clusters_df = pd.DataFrame(
        [
            {"record_id": "r1", "cluster_id": "P1"},
            {"record_id": "r2", "cluster_id": "P1"},
            {"record_id": "r3", "cluster_id": "P2"},
            {"record_id": "r4", "cluster_id": "P2"},
        ]
    )

    c_metrics = evaluate_clusters(clusters_df, record_truth_df, doppel_df)
    assert c_metrics.bcubed_precision == 1.0
    assert c_metrics.bcubed_recall == 1.0
    assert c_metrics.bcubed_f1 == 1.0
    assert c_metrics.false_merge_clusters == 0
    assert c_metrics.doppelganger_false_merge_rate == 0.0


def test_empty_predictions():
    """Verify empty predictions yield recall 0 and reach equal to record count."""
    record_truth = pd.DataFrame(
        [
            {"record_id": "r1", "person_id": "P1"},
            {"record_id": "r2", "person_id": "P1"},
            {"record_id": "r3", "person_id": "P2"},
        ]
    )
    true_pairs = {("r1", "r2")}
    clusters_df = pd.DataFrame(
        [
            {"record_id": "r1", "cluster_id": "r1"},
            {"record_id": "r2", "cluster_id": "r2"},
            {"record_id": "r3", "cluster_id": "r3"},
        ]
    )
    pw = evaluate_pairwise(
        predictions_df=pd.DataFrame(columns=["record_id_l", "record_id_r", "match_probability"]),
        true_pairs_set=true_pairs,
        clusters_df=clusters_df,
        record_person_map={"r1": "P1", "r2": "P1", "r3": "P2"},
        threshold=0.5,
    )
    assert pw.tp == 0
    assert pw.recall == 0.0
    c_metrics = evaluate_clusters(clusters_df, record_truth)
    assert c_metrics.dedup_reach == 3


def test_recall_denominator():
    """Verify that missing pairs count as FN and lower recall."""
    total_true = 10
    tp = 8
    pw = compute_pairwise_metrics_from_counts(
        tp=tp, fp=0, total_true_pairs=total_true, edge_tp=tp, edge_fp=0
    )
    assert pw.fn == 2
    assert np.isclose(pw.recall, 0.8)


def test_incremental_sweep_equals_from_scratch():
    """Verify incremental Union-Find sweep produces identical metrics to from-scratch clustering."""
    records_df = pd.DataFrame({"record_id": [f"r{i}" for i in range(10)]})
    record_ids = records_df["record_id"].tolist()

    # 4 distinct persons
    persons = ["p1", "p1", "p1", "p2", "p2", "p3", "p3", "p3", "p4", "p4"]
    record_truth_df = pd.DataFrame({"record_id": record_ids, "person_id": persons})

    # Ground truth true pairs
    true_pairs_list = []
    for i in range(len(record_ids)):
        for j in range(i + 1, len(record_ids)):
            if persons[i] == persons[j]:
                true_pairs_list.append({"record_id_1": record_ids[i], "record_id_2": record_ids[j]})
    true_pairs_df = pd.DataFrame(true_pairs_list)

    # Scored predictions with varying probabilities
    preds_df = pd.DataFrame(
        [
            {"record_id_l": "r0", "record_id_r": "r1", "match_probability": 0.95},
            {"record_id_l": "r1", "record_id_r": "r2", "match_probability": 0.85},
            {"record_id_l": "r3", "record_id_r": "r4", "match_probability": 0.70},
            {"record_id_l": "r2", "record_id_r": "r3", "match_probability": 0.50},
            {"record_id_l": "r5", "record_id_r": "r6", "match_probability": 0.40},
            {"record_id_l": "r6", "record_id_r": "r7", "match_probability": 0.25},
            {"record_id_l": "r8", "record_id_r": "r9", "match_probability": 0.15},
        ]
    )

    sweep_df, _ = run_threshold_sweep(
        predictions_df=preds_df,
        record_ids=record_ids,
        record_truth_df=record_truth_df,
        true_pairs_df=true_pairs_df,
        grid="probability",
    )

    # Test at 5 distinct thresholds
    test_thresholds = [0.15, 0.30, 0.50, 0.70, 0.90]
    rec_person_map = dict(zip(record_truth_df["record_id"], record_truth_df["person_id"]))

    for t in test_thresholds:
        # 1. From incremental sweep
        sweep_row = sweep_df[np.isclose(sweep_df["threshold"], t)].iloc[0]

        # 2. From scratch
        scratch_uf = UnionFind(
            record_ids,
            record_person_map=rec_person_map,
            person_total_counts=dict(record_truth_df["person_id"].value_counts()),
        )
        above = preds_df[preds_df["match_probability"] >= t]
        for _, r in above.iterrows():
            scratch_uf.union(str(r["record_id_l"]), str(r["record_id_r"]))

        scratch_metrics = scratch_uf.compute_metrics(total_records=len(record_ids))

        assert sweep_row["tp"] == scratch_uf.cluster_tp
        assert sweep_row["fp"] == scratch_uf.cluster_fp
        assert np.isclose(sweep_row["bcubed_f1"], scratch_metrics.bcubed_f1, atol=1e-5)
        assert sweep_row["false_merge_clusters"] == scratch_metrics.false_merge_clusters
        assert sweep_row["dedup_reach"] == scratch_metrics.dedup_reach


def test_select_fails_on_holdout(tmp_path):
    """Verify that evaluate in select mode raises an error when run on a holdout dataset."""
    run_dir = tmp_path / "data" / "holdout_test"
    reg_dir = run_dir / "registry"
    truth_dir = run_dir / "truth"
    reg_dir.mkdir(parents=True)
    truth_dir.mkdir(parents=True)

    manifest = {"role": "holdout", "seed": 1042}
    with open(run_dir / "manifest.json", "w") as f:
        json.dump(manifest, f)

    records = pd.DataFrame({"record_id": ["r1", "r2"]})
    records.to_parquet(reg_dir / "records.parquet")
    record_truth = pd.DataFrame({"record_id": ["r1", "r2"], "person_id": ["p1", "p2"]})
    record_truth.to_parquet(truth_dir / "record_truth.parquet")
    true_pairs = pd.DataFrame(columns=["record_id_1", "record_id_2"])
    true_pairs.to_parquet(truth_dir / "true_pairs.parquet")
    pd.DataFrame().to_parquet(truth_dir / "doppelganger_person_pairs.parquet")
    pd.DataFrame(columns=["record_id", "corruption_type"]).to_parquet(
        truth_dir / "corruption_log.parquet"
    )

    preds = pd.DataFrame([{"record_id_l": "r1", "record_id_r": "r2", "match_probability": 0.9}])

    with pytest.raises(ValueError, match="holdout"):
        generate_evaluation_report(
            method_name="test_method",
            run_name="holdout_test",
            mode="select",
            predictions_df=preds,
            candidate_pair_count=1,
            base_data_dir=tmp_path / "data",
            base_results_dir=tmp_path / "results",
        )


def test_report_mode_fails_without_selected_thresholds(tmp_path):
    """Verify that evaluate in report mode raises FileNotFoundError if thresholds JSON missing."""
    run_dir = tmp_path / "data" / "holdout_test"
    reg_dir = run_dir / "registry"
    truth_dir = run_dir / "truth"
    reg_dir.mkdir(parents=True)
    truth_dir.mkdir(parents=True)

    manifest = {"role": "holdout", "seed": 1042}
    with open(run_dir / "manifest.json", "w") as f:
        json.dump(manifest, f)

    records = pd.DataFrame({"record_id": ["r1", "r2"]})
    records.to_parquet(reg_dir / "records.parquet")
    record_truth = pd.DataFrame(
        {"record_id": ["r1", "r2"], "person_id": ["p1", "p2"], "clean_given_name": ["a", "b"]}
    )
    record_truth.to_parquet(truth_dir / "record_truth.parquet")
    true_pairs = pd.DataFrame(columns=["record_id_1", "record_id_2"])
    true_pairs.to_parquet(truth_dir / "true_pairs.parquet")
    pd.DataFrame().to_parquet(truth_dir / "doppelganger_person_pairs.parquet")
    pd.DataFrame(columns=["record_id", "corruption_type"]).to_parquet(
        truth_dir / "corruption_log.parquet"
    )

    preds = pd.DataFrame([{"record_id_l": "r1", "record_id_r": "r2", "match_probability": 0.9}])

    with pytest.raises(FileNotFoundError, match="selected_thresholds.json"):
        generate_evaluation_report(
            method_name="test_method",
            run_name="holdout_test",
            mode="report",
            predictions_df=preds,
            candidate_pair_count=1,
            base_data_dir=tmp_path / "data",
            base_results_dir=tmp_path / "results",
        )


def test_report_records_sha256(tmp_path):
    """Verify report mode records dev source run and SHA-256 of selected_thresholds.json."""
    base_data = tmp_path / "data"
    base_results = tmp_path / "results"

    run_dir = base_data / "holdout_test"
    reg_dir = run_dir / "registry"
    truth_dir = run_dir / "truth"
    reg_dir.mkdir(parents=True)
    truth_dir.mkdir(parents=True)

    manifest = {"role": "holdout", "seed": 1042}
    with open(run_dir / "manifest.json", "w") as f:
        json.dump(manifest, f)

    records = pd.DataFrame({"record_id": ["r1", "r2"]})
    records.to_parquet(reg_dir / "records.parquet")
    record_truth = pd.DataFrame(
        {
            "record_id": ["r1", "r2"],
            "person_id": ["p1", "p2"],
            "source_module": ["mod1", "mod2"],
            "clean_given_name": ["a", "b"],
        }
    )
    record_truth.to_parquet(truth_dir / "record_truth.parquet")
    true_pairs = pd.DataFrame(columns=["record_id_1", "record_id_2"])
    true_pairs.to_parquet(truth_dir / "true_pairs.parquet")
    pd.DataFrame().to_parquet(truth_dir / "doppelganger_person_pairs.parquet")
    pd.DataFrame(columns=["record_id", "corruption_type"]).to_parquet(
        truth_dir / "corruption_log.parquet"
    )

    # Write selected_thresholds.json
    method_dir = base_results / "exact"
    method_dir.mkdir(parents=True)
    sel_data = {
        "method": "exact",
        "dev_run": "demo",
        "t_cost": 0.8,
        "t_p99": 0.95,
        "min_cost": 10.0,
    }
    sel_str = json.dumps(sel_data, indent=2)
    with open(method_dir / "selected_thresholds.json", "w") as f:
        f.write(sel_str)
    expected_sha = hashlib.sha256(sel_str.encode("utf-8")).hexdigest()

    preds = pd.DataFrame([{"record_id_l": "r1", "record_id_r": "r2", "match_probability": 0.9}])

    metrics = generate_evaluation_report(
        method_name="exact",
        run_name="holdout_test",
        mode="report",
        predictions_df=preds,
        candidate_pair_count=1,
        base_data_dir=base_data,
        base_results_dir=base_results,
    )

    assert metrics["thresholds_source_run"] == "demo"
    assert metrics["thresholds_sha256"] == expected_sha
    assert metrics["operational_thresholds"]["t_cost"] == 0.8


def test_input_contract_validation():
    """Verify contracts validation rejects invalid predictions formats."""
    records_df = pd.DataFrame({"record_id": ["r1", "r2", "r3"]})

    # Self pair
    bad_self = pd.DataFrame([{"record_id_l": "r1", "record_id_r": "r1", "match_probability": 0.5}])
    with pytest.raises(ValueError, match="Self-pairs"):
        validate_predictions(bad_self, records_df)

    # Invalid probability
    bad_prob = pd.DataFrame([{"record_id_l": "r1", "record_id_r": "r2", "match_probability": 1.5}])
    with pytest.raises(ValueError, match="match_probability"):
        validate_predictions(bad_prob, records_df)

    # Unknown record id
    bad_id = pd.DataFrame(
        [{"record_id_l": "r1", "record_id_r": "unknown", "match_probability": 0.5}]
    )
    with pytest.raises(ValueError, match="unknown record IDs"):
        validate_predictions(bad_id, records_df)

    # Normalization of pairs (swapping l > r)
    unnorm = pd.DataFrame([{"record_id_l": "r3", "record_id_r": "r1", "match_probability": 0.7}])
    normed = validate_predictions(unnorm, records_df)
    assert normed.iloc[0]["record_id_l"] == "r1"
    assert normed.iloc[0]["record_id_r"] == "r3"


def test_cluster_contract_validation():
    """Verify cluster contract validation checks completeness and uniqueness."""
    records_df = pd.DataFrame({"record_id": ["r1", "r2", "r3"]})

    # Missing record
    incomplete = pd.DataFrame([{"record_id": "r1", "cluster_id": "c1"}])
    with pytest.raises(ValueError, match="missing in clusters"):
        validate_clusters(incomplete, records_df)

    # Duplicate record
    duplicate = pd.DataFrame(
        [
            {"record_id": "r1", "cluster_id": "c1"},
            {"record_id": "r1", "cluster_id": "c2"},
            {"record_id": "r2", "cluster_id": "c1"},
            {"record_id": "r3", "cluster_id": "c3"},
        ]
    )
    with pytest.raises(ValueError, match="Duplicate record_id"):
        validate_clusters(duplicate, records_df)


def test_truth_directory_access_security_scan():
    """Verify only evaluate, generate, corrupt reference truth or clean population files."""
    src_dir = Path("src/barilink")
    allowed_packages = {"evaluate", "generate", "corrupt"}

    violations = []
    for py_file in src_dir.rglob("*.py"):
        rel = py_file.relative_to(src_dir)
        top_pkg = rel.parts[0] if len(rel.parts) > 1 else ""

        if top_pkg in allowed_packages:
            continue

        with open(py_file, "r", encoding="utf-8") as f:
            code = f.read()

        try:
            tree = ast.parse(code, filename=str(py_file))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                continue

            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                s = node.value
                is_forbidden = (
                    s == "truth"
                    or "/truth" in s
                    or "\\truth" in s
                    or "truth/" in s
                    or "truth\\" in s
                    or "persons.parquet" in s
                    or "households.parquet" in s
                )
                if is_forbidden:
                    violations.append((str(py_file), s))

    assert not violations, f"Forbidden ground-truth reference found in: {violations}"


def test_stress_run_refused_by_select_mode(tmp_path):
    """Verify that select mode is strictly forbidden on stress datasets."""
    import json

    from barilink.evaluate.report import generate_evaluation_report
    from barilink.evaluate.resolve_eval import run_resolve_select

    # 1. Test generate_evaluation_report refuses select mode on stress dataset
    stress_dir = tmp_path / "stress_test_run"
    stress_dir.mkdir(parents=True)
    manifest_p = stress_dir / "manifest.json"
    with open(manifest_p, "w", encoding="utf-8") as f:
        json.dump({"role": "stress", "run_name": "stress_test_run"}, f)

    with pytest.raises(
        ValueError, match="Cannot run evaluate in 'select' mode on run.*role 'stress'"
    ):
        generate_evaluation_report(
            method_name="exact",
            run_name="stress_test_run",
            mode="select",
            predictions_df=pd.DataFrame(),
            candidate_pair_count=0,
            base_data_dir=tmp_path,
        )

    # 2. Test run_resolve_select refuses stress dataset
    with pytest.raises(ValueError, match="Cannot run select mode on stress dataset"):
        run_resolve_select(
            run_name="stress_test_run",
            base_data_dir=tmp_path,
        )


def test_kinship_bug_check_function_correctness(tmp_path):
    """Verify bug check function runs on synthetic data and identifies cuts."""
    from barilink.evaluate.bug_check import run_kinship_bug_check

    run_dir = tmp_path / "toy"
    reg_dir = run_dir / "registry"
    truth_dir = run_dir / "truth"
    model_dir = run_dir / "splink_toy"
    res_dir = run_dir / "splink_toy_resolved"
    for d in [reg_dir, truth_dir, model_dir, res_dir]:
        d.mkdir(parents=True, exist_ok=True)

    pd.DataFrame({
        "record_id": ["R1", "R2"],
        "person_id": ["P1", "P1"],
    }).to_parquet(truth_dir / "record_truth.parquet", index=False)

    pd.DataFrame({
        "record_id": ["R1", "R2"],
        "full_name_raw": ["Rahim Mia", "Rahim Mia"],
        "guardian_name_raw": ["Father Mia", "Father Mia"],
    }).to_parquet(reg_dir / "records.parquet", index=False)

    pd.DataFrame({
        "record_id": ["R2"],
        "member_name_raw": ["Rahim Mia"],
        "relation_raw": ["self"],
    }).to_parquet(reg_dir / "rosters.parquet", index=False)

    pd.DataFrame({
        "record_id": ["R1", "R2"],
        "name_skeleton": ["RHM", "RHM"],
        "roster_skels_v3": [[], ["RHM"]],
    }).to_parquet(reg_dir / "features.parquet", index=False)

    pd.DataFrame({
        "record_id_l": ["R1"],
        "record_id_r": ["R2"],
        "match_weight": [10.0],
        "match_probability": [0.99],
    }).to_parquet(model_dir / "predictions.parquet", index=False)

    pd.DataFrame({
        "reason": ["listed_as_other_member"],
        "record_id_l": ["R1"],
        "record_id_r": ["R2"],
        "weight": [10.0],
        "component_id": ["comp_0"],
    }).to_parquet(res_dir / "resolution_log.parquet", index=False)

    res = run_kinship_bug_check(
        run_name="toy",
        method="splink_toy",
        resolved_method="splink_toy_resolved",
        base_data_dir=tmp_path,
        base_results_dir=tmp_path,
    )
    assert res["true_pairs_listed_fired_count"] == 1
    assert res["same_person_cuts_count"] == 1


@pytest.mark.artifacts
def test_kinship_bug_check_on_dev():
    """Verify bug check runs on dev and identifies cuts."""
    from barilink.evaluate.bug_check import run_kinship_bug_check

    v31_res = run_kinship_bug_check(method="splink_v3_1", resolved_method="splink_v3_1_resolved")
    assert v31_res["true_pairs_listed_fired_count"] == 2
    assert v31_res["same_person_cuts_count"] == 3


def test_stress_curves_function_correctness(tmp_path):
    """Verify stress curve generation and matched-recall interpolation on synthetic data."""
    from barilink.evaluate.ablation import compute_stress_curves

    run_dir = tmp_path / "toy_stress"
    reg_dir = run_dir / "registry"
    truth_dir = run_dir / "truth"
    model_dir = run_dir / "splink_toy"
    for d in [reg_dir, truth_dir, model_dir]:
        d.mkdir(parents=True, exist_ok=True)

    pd.DataFrame({"record_id": ["R1", "R2", "R3", "R4"]}).to_parquet(
        reg_dir / "records.parquet", index=False
    )
    pd.DataFrame({
        "record_id": ["R1", "R2", "R3", "R4"],
        "person_id": ["P1", "P1", "P2", "P3"],
    }).to_parquet(truth_dir / "record_truth.parquet", index=False)
    pd.DataFrame({
        "record_id_1": ["R1"],
        "record_id_2": ["R2"],
    }).to_parquet(truth_dir / "true_pairs.parquet", index=False)
    pd.DataFrame({
        "person_id_1": ["P2"],
        "person_id_2": ["P3"],
        "is_injected": [False],
    }).to_parquet(truth_dir / "doppelganger_person_pairs.parquet", index=False)

    pd.DataFrame({
        "record_id_l": ["R1", "R2"],
        "record_id_r": ["R2", "R3"],
        "match_weight": [5.0, 1.0],
    }).to_parquet(model_dir / "predictions.parquet", index=False)

    out_dir = tmp_path / "stress_out"
    curves_df, matched_df = compute_stress_curves(
        run_name="toy_stress",
        methods=["splink_toy"],
        base_data_dir=tmp_path,
        base_results_dir=tmp_path,
        output_dir=out_dir,
    )
    assert not curves_df.empty
    assert "pooled_fm_rate" in curves_df.columns
    assert "cluster_recall" in curves_df.columns
    assert not matched_df.empty
    assert (out_dir / "stress_curves.parquet").exists()
    assert (out_dir / "charts" / "stress_fm_vs_recall.html").exists()


@pytest.mark.artifacts
def test_stress_curves_and_matched_recall():
    """Verify stress curve generation and matched-recall interpolation on recorded data."""
    assert Path("results/stress_0/stress_curves.parquet").exists()
    assert Path("results/stress_0/charts/stress_fm_vs_recall.html").exists()


def test_pipeline_k_model_and_resolution():
    """Verify Pipeline K configuration, absence of kinship comparison, and dev cost."""
    model_path = Path("results/models/splink_k/model.json")
    assert model_path.exists()
    with open(model_path, "r", encoding="utf-8") as f:
        m = json.load(f)
    comp_cols = [c.get("output_column_name") for c in m.get("comparisons", [])]
    assert "kinship_co_resident_count" not in comp_cols
    assert "given_name" in comp_cols
    assert "guardian_name" in comp_cols

    sel_path = Path("results/splink_k_resolved/selected_thresholds.json")
    assert sel_path.exists()
    with open(sel_path, "r", encoding="utf-8") as f:
        sel = json.load(f)
    assert sel["t_link"] == 2.0
    assert sel["t_bridge"] == 4.0
    assert sel["min_cost"] == 782.0
    assert sel["min_cost"] <= 811.44  # Pre-registered adoption threshold


def test_confirm_table_function_correctness(tmp_path):
    """Verify confirm table generation function on synthetic inputs."""
    from barilink.evaluate.confirm import generate_confirm_table

    demo_dir = tmp_path / "results" / "demo" / "splink_k_resolved"
    demo_dir.mkdir(parents=True, exist_ok=True)
    demo_ref_dir = tmp_path / "results" / "demo" / "splink_v3_1_resolved"
    demo_ref_dir.mkdir(parents=True, exist_ok=True)

    dummy_metrics = {
        "headline_metrics_at_t_cost": {
            "expected_cost": 800.0,
            "cluster_precision": 0.95,
            "cluster_recall": 0.55,
            "cluster_f1": 0.70,
            "reach_error_pct": 10.0,
            "doppelganger_false_merge_rate": 0.01,
        },
        "operational_thresholds": {"t_link": 2.0, "t_bridge": 4.0},
    }
    with open(demo_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(dummy_metrics, f)
    with open(demo_ref_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(dummy_metrics, f)

    holdout_dir = tmp_path / "results" / "holdout_toy" / "splink_k_resolved"
    holdout_dir.mkdir(parents=True, exist_ok=True)
    holdout_ref_dir = tmp_path / "results" / "holdout_toy" / "splink_v3_1_resolved"
    holdout_ref_dir.mkdir(parents=True, exist_ok=True)
    with open(holdout_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(dummy_metrics, f)
    with open(holdout_ref_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(dummy_metrics, f)

    truth_p = tmp_path / "data" / "holdout_toy" / "truth"
    truth_p.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=["person_id_1", "person_id_2"]).to_parquet(
        truth_p / "doppelganger_person_pairs.parquet", index=False
    )

    out_file = tmp_path / "confirm_output.md"
    df = generate_confirm_table(
        runs=["holdout_toy"],
        methods=["splink_k_resolved", "splink_v3_1_resolved"],
        reference_method="splink_v3_1_resolved",
        dev_run="demo",
        base_data_dir=tmp_path / "data",
        base_results_dir=tmp_path / "results",
        output_path=out_file,
    )
    assert not df.empty
    assert out_file.exists()
    assert out_file.stat().st_size > 0


@pytest.mark.artifacts
def test_confirm_table_generation_and_direction():
    """Verify Hypothesis H3 confirmation table generation and 5/5 seed direction."""
    confirm_file = Path("results/holdout_confirm/confirm_table.md")
    assert confirm_file.exists()
    content = confirm_file.read_text(encoding="utf-8")
    assert "Direction Consistency" in content
    assert "5/5 seeds" in content
    assert "CONFIRMED" in content


@pytest.mark.artifacts
def test_stress_table_contains_requested_variants():
    """Verify stress table contains splink_v3_1_resolved, Pipeline K, and v3_no_kinship."""
    stress_file = Path("results/stress_0/stress_table.md")
    assert stress_file.exists()
    content = stress_file.read_text(encoding="utf-8")
    assert "splink_v3_1_resolved" in content
    assert "splink_k_resolved" in content
    assert "splink_v3_no_kinship" in content
    assert "Matched-Recall Doppelganger False-Merge Comparison" in content


def test_no_hardcoded_data_generated_demo_in_src():
    """Security scan ensuring no hardcoded 'data/generated/demo' literal exists in src/."""
    src_dir = Path("src")
    assert src_dir.exists()
    violations = []
    for p in src_dir.rglob("*.py"):
        content = p.read_text(encoding="utf-8")
        if "data/generated/demo" in content:
            violations.append(str(p))
    assert not violations, f"Hardcoded 'data/generated/demo' found in: {violations}"


def test_conftest_git_mutation_guard(tmp_path):
    """Verify that the conftest mutation guard detects tracked file changes in a git repo."""
    import subprocess

    from conftest import _is_git_repo, _sha256_file

    repo = tmp_path / "throwaway_repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=repo, check=True)

    assert _is_git_repo(repo) is True

    src_f = repo / "tracked_file.txt"
    src_f.write_text("initial content", encoding="utf-8")
    subprocess.run(["git", "add", "tracked_file.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True)

    initial_hash = _sha256_file(src_f)

    # Mutate the file
    src_f.write_text("altered content", encoding="utf-8")
    new_hash = _sha256_file(src_f)
    assert initial_hash != new_hash

    mod_out = subprocess.check_output(["git", "ls-files", "-m"], cwd=repo, text=True)
    assert "tracked_file.txt" in mod_out

