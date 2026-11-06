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
                true_pairs_list.append(
                    {"record_id_1": record_ids[i], "record_id_2": record_ids[j]}
                )
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

    preds = pd.DataFrame(
        [{"record_id_l": "r1", "record_id_r": "r2", "match_probability": 0.9}]
    )

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

    preds = pd.DataFrame(
        [{"record_id_l": "r1", "record_id_r": "r2", "match_probability": 0.9}]
    )

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

    preds = pd.DataFrame(
        [{"record_id_l": "r1", "record_id_r": "r2", "match_probability": 0.9}]
    )

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
    """Verify only evaluate, generate, and corrupt reference 'truth' as path component."""
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
                is_path_usage = (
                    s == "truth"
                    or "/truth" in s
                    or "\\truth" in s
                    or "truth/" in s
                    or "truth\\" in s
                )
                if is_path_usage:
                    violations.append((str(py_file), s))

    assert not violations, f"Forbidden truth directory reference found in: {violations}"
