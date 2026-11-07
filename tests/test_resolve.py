"""Unit tests for Phase 5: Entity Resolution, Kinship Golden Records,
and Budgeted Clerical Review.
"""

import ast
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from barilink.evaluate.review_eval import simulate_clerical_review
from barilink.resolve.golden import build_golden_records
from barilink.resolve.graph import build_resolved_graph
from barilink.resolve.review import build_review_queue


def test_weak_bridge_cut_vs_kept():
    """Verify bridge of weight 3 joining two dense triangles is cut at t_bridge=5, kept at 2."""
    # Two triangles: {r1, r2, r3} and {r4, r5, r6}
    # Bridge: (r3, r4) with weight 3.0
    records_df = pd.DataFrame(
        {
            "record_id": [f"r{i}" for i in range(1, 7)],
            "sex_raw": ["F"] * 6,
            "birth_year_est": [1990] * 6,
        }
    )

    # Intra-triangle edges: weight 10.0
    preds_df = pd.DataFrame(
        [
            # Triangle 1
            {"record_id_l": "r1", "record_id_r": "r2", "match_weight": 10.0},
            {"record_id_l": "r2", "record_id_r": "r3", "match_weight": 10.0},
            {"record_id_l": "r1", "record_id_r": "r3", "match_weight": 10.0},
            # Bridge
            {"record_id_l": "r3", "record_id_r": "r4", "match_weight": 3.0},
            # Triangle 2
            {"record_id_l": "r4", "record_id_r": "r5", "match_weight": 10.0},
            {"record_id_l": "r5", "record_id_r": "r6", "match_weight": 10.0},
            {"record_id_l": "r4", "record_id_r": "r6", "match_weight": 10.0},
        ]
    )

    # 1. With t_bridge = 5.0 (t_link = 2.0) -> bridge cut, 2 clusters
    clusters_cut, log_cut = build_resolved_graph(preds_df, records_df, t_link=2.0, t_bridge=5.0)
    c1 = clusters_cut[clusters_cut["record_id"] == "r1"]["cluster_id"].iloc[0]
    c4 = clusters_cut[clusters_cut["record_id"] == "r4"]["cluster_id"].iloc[0]
    assert c1 != c4, "Bridge of weight 3 should be cut when t_bridge=5"
    assert len(clusters_cut["cluster_id"].unique()) == 2
    assert len(log_cut) == 1
    assert log_cut.iloc[0]["action"] == "bridge_cut"

    # 2. With t_bridge = 2.0 -> bridge kept, 1 cluster
    clusters_kept, log_kept = build_resolved_graph(preds_df, records_df, t_link=2.0, t_bridge=2.0)
    c1_k = clusters_kept[clusters_kept["record_id"] == "r1"]["cluster_id"].iloc[0]
    c4_k = clusters_kept[clusters_kept["record_id"] == "r4"]["cluster_id"].iloc[0]
    assert c1_k == c4_k, "Bridge of weight 3 should be kept when t_bridge=2"
    assert len(clusters_kept["cluster_id"].unique()) == 1
    assert len(log_kept) == 0


def test_strong_bridge_kept():
    """Verify strong bridge (weight 12) joining two triangles is kept at t_bridge=5."""
    records_df = pd.DataFrame(
        {
            "record_id": [f"r{i}" for i in range(1, 7)],
            "sex_raw": ["F"] * 6,
            "birth_year_est": [1990] * 6,
        }
    )

    preds_df = pd.DataFrame(
        [
            {"record_id_l": "r1", "record_id_r": "r2", "match_weight": 15.0},
            {"record_id_l": "r2", "record_id_r": "r3", "match_weight": 15.0},
            {"record_id_l": "r1", "record_id_r": "r3", "match_weight": 15.0},
            # Strong bridge: weight 12.0
            {"record_id_l": "r3", "record_id_r": "r4", "match_weight": 12.0},
            {"record_id_l": "r4", "record_id_r": "r5", "match_weight": 15.0},
            {"record_id_l": "r5", "record_id_r": "r6", "match_weight": 15.0},
            {"record_id_l": "r4", "record_id_r": "r6", "match_weight": 15.0},
        ]
    )

    clusters, log = build_resolved_graph(preds_df, records_df, t_link=2.0, t_bridge=5.0)
    c1 = clusters[clusters["record_id"] == "r1"]["cluster_id"].iloc[0]
    c4 = clusters[clusters["record_id"] == "r4"]["cluster_id"].iloc[0]
    assert c1 == c4, "Bridge of weight 12 should be kept when t_bridge=5"
    assert len(clusters["cluster_id"].unique()) == 1
    assert len(log) == 0


def test_cannot_link_sex_conflict_cuts_weakest_edge():
    """Verify cannot-link sex conflict on chain A-B-C cuts the weakest edge."""
    # A(F) - B(None) - C(M)
    # Edge A-B: weight 8.0, Edge B-C: weight 4.0
    # Must cut B-C, ending with {A, B} in one cluster and {C} in another
    records_df = pd.DataFrame(
        {
            "record_id": ["A", "B", "C"],
            "sex_raw": ["F", None, "M"],
            "birth_year_est": [1990, 1990, 1990],
        }
    )

    preds_df = pd.DataFrame(
        [
            {"record_id_l": "A", "record_id_r": "B", "match_weight": 8.0},
            {"record_id_l": "B", "record_id_r": "C", "match_weight": 4.0},
        ]
    )

    clusters, log = build_resolved_graph(preds_df, records_df, t_link=2.0, t_bridge=2.0)
    c_a = clusters[clusters["record_id"] == "A"]["cluster_id"].iloc[0]
    c_b = clusters[clusters["record_id"] == "B"]["cluster_id"].iloc[0]
    c_c = clusters[clusters["record_id"] == "C"]["cluster_id"].iloc[0]

    assert c_a == c_b, "A and B should remain clustered"
    assert c_a != c_c, "A and C have conflicting sex and must not share a cluster"
    assert len(log) == 1
    assert log.iloc[0]["action"] == "constraint_cut"
    assert log.iloc[0]["record_id_l"] == "B"
    assert log.iloc[0]["record_id_r"] == "C"
    assert log.iloc[0]["weight"] == 4.0


def test_cannot_link_min_cut_four_node_parallel_weak_edges():
    """Verify min-cut removes two parallel weak edges (wt 3) rather than one strong edge (wt 12).

    Amendment 1 test:
    Nodes: A, B, C, D. Cannot-link pair: (A, D) via birth year gap or sex.
    Edges:
      (A, B) weight 12
      (B, C) weight 3
      (C, D) weight 100
      (B, D) weight 3
    Unshifted cut capacity = weight removes (B, C) and (B, D) (total capacity 6 < 12).
    A shift C=10 would incorrectly cost 26 vs 22 and cut (A, B).
    """
    records_df = pd.DataFrame(
        {
            "record_id": ["A", "B", "C", "D"],
            "sex_raw": [
                "F",
                "F",
                "M",
                "M",
            ],  # A (F) vs D (M) cannot link; C (M) is compatible with D
            "birth_year_est": [1990, 1990, 1990, 1990],
        }
    )

    preds_df = pd.DataFrame(
        [
            {"record_id_l": "A", "record_id_r": "B", "match_weight": 12.0},
            {"record_id_l": "B", "record_id_r": "C", "match_weight": 3.0},
            {"record_id_l": "C", "record_id_r": "D", "match_weight": 100.0},
            {"record_id_l": "B", "record_id_r": "D", "match_weight": 3.0},
        ]
    )

    clusters, log = build_resolved_graph(preds_df, records_df, t_link=2.0, t_bridge=2.0)
    c_a = clusters[clusters["record_id"] == "A"]["cluster_id"].iloc[0]
    c_b = clusters[clusters["record_id"] == "B"]["cluster_id"].iloc[0]
    c_c = clusters[clusters["record_id"] == "C"]["cluster_id"].iloc[0]
    c_d = clusters[clusters["record_id"] == "D"]["cluster_id"].iloc[0]

    # A and B must stay together!
    assert c_a == c_b, "Strong edge A-B (weight 12) must NOT be cut"
    # C and D stay together (weight 100)
    assert c_c == c_d, "Edge C-D (weight 100) must NOT be cut"
    # A and D must be separated
    assert c_a != c_d, "Cannot-link pair A and D must be separated"

    # Verify log cut the two weak edges (B, C) and (B, D)
    cut_edges = set((r["record_id_l"], r["record_id_r"]) for _, r in log.iterrows())
    assert ("B", "C") in cut_edges
    assert ("B", "D") in cut_edges
    assert ("A", "B") not in cut_edges


def test_cannot_link_birth_year_gap():
    """Verify birth year gap exceeding max_birth_year_gap (10) severs connected records."""
    records_df = pd.DataFrame(
        {
            "record_id": ["r1", "r2"],
            "sex_raw": ["F", "F"],
            "birth_year_est": [1980, 1995],  # Gap = 15 years > 10
        }
    )

    preds_df = pd.DataFrame(
        [
            {"record_id_l": "r1", "record_id_r": "r2", "match_weight": 7.0},
        ]
    )

    clusters, log = build_resolved_graph(
        preds_df, records_df, t_link=2.0, t_bridge=2.0, max_birth_year_gap=10
    )
    c1 = clusters[clusters["record_id"] == "r1"]["cluster_id"].iloc[0]
    c2 = clusters[clusters["record_id"] == "r2"]["cluster_id"].iloc[0]
    assert c1 != c2, "Records with 15-year birth year gap must not share a cluster"
    assert len(log) == 1
    assert log.iloc[0]["reason"] == "birth_year_gap"


def test_resolution_determinism():
    """Verify resolved cluster IDs are identical regardless of input record/edge row ordering."""
    records_df_1 = pd.DataFrame(
        {
            "record_id": ["r1", "r2", "r3", "r4"],
            "sex_raw": ["F", "F", "F", "F"],
            "birth_year_est": [1990, 1990, 1991, 1990],
        }
    )
    records_df_2 = records_df_1.sample(frac=1.0, random_state=42).reset_index(drop=True)

    preds_df_1 = pd.DataFrame(
        [
            {"record_id_l": "r1", "record_id_r": "r2", "match_weight": 8.0},
            {"record_id_l": "r2", "record_id_r": "r3", "match_weight": 7.5},
            {"record_id_l": "r3", "record_id_r": "r4", "match_weight": 2.5},
        ]
    )
    preds_df_2 = preds_df_1.sample(frac=1.0, random_state=99).reset_index(drop=True)

    clusters_1, _ = build_resolved_graph(preds_df_1, records_df_1, t_link=3.0, t_bridge=5.0)
    clusters_2, _ = build_resolved_graph(preds_df_2, records_df_2, t_link=3.0, t_bridge=5.0)

    pd.testing.assert_frame_equal(
        clusters_1.sort_values("record_id"), clusters_2.sort_values("record_id")
    )


def test_golden_record_guardian_switch_and_lineage():
    """Verify golden record correctly handles guardian switch, median birth year, and phone."""
    clusters_df = pd.DataFrame(
        {
            "record_id": ["rec_1", "rec_2"],
            "cluster_id": ["c_test_001", "c_test_001"],
        }
    )

    # rec_1: unmarried (guardian=father), age 20 (est 2004), no phone
    # rec_2: married later (guardian=husband), age 23 (est 2003), has phone
    records_df = pd.DataFrame(
        [
            {
                "record_id": "rec_1",
                "full_name_raw": "Mst. Parvin Akter",
                "name_canon": "parvin",
                "guardian_name_raw": "Md. Abdul Karim",
                "guardian_type_raw": "father",
                "birth_year_est": 2004,
                "phone_norm": None,
                "sex_raw": "F",
                "village_raw": "Mondal Para",
                "union_raw": "Ramna",
                "upazila_raw": "Chilmari",
                "district_raw": "Kurigram",
                "source_module": "club_formation",
                "enrolment_date": "2024-01-15",
            },
            {
                "record_id": "rec_2",
                "full_name_raw": "Parvin Begum",
                "name_canon": "parvin",
                "guardian_name_raw": "Mohammad Rafiqul Islam",
                "guardian_type_raw": "husband",
                "birth_year_est": 2002,
                "phone_norm": "01712345678",
                "sex_raw": "F",
                "village_raw": "Mondal Para",
                "union_raw": "Ramna",
                "upazila_raw": "Chilmari",
                "district_raw": "Kurigram",
                "source_module": "microfinance_group",
                "enrolment_date": "2025-06-20",
            },
        ]
    )

    golden_df = build_golden_records(clusters_df, records_df)
    assert len(golden_df) == 1
    g = golden_df.iloc[0]

    # Kinship separation: both father_name and husband_name must be populated!
    assert g["father_name"] == "Md. Abdul Karim"
    assert g["husband_name"] == "Mohammad Rafiqul Islam"

    # Median birth year of 2004 and 2002 -> 2003
    assert g["birth_year"] == 2003
    assert g["birth_year_spread"] == 2

    # Most recent valid phone
    assert g["phone"] == "01712345678"
    assert g["phones_all"] == ["01712345678"]

    # Lineage check
    lineage = eval(g["field_lineage"])
    assert "father_name" in lineage
    assert lineage["father_name"]["source_record_id"] == "rec_1"
    assert lineage["father_name"]["rule"] == "mode_guardian_father_tie_date"
    assert "husband_name" in lineage
    assert lineage["husband_name"]["source_record_id"] == "rec_2"
    assert lineage["husband_name"]["rule"] == "mode_guardian_husband_tie_date"
    assert "display_name" in lineage
    assert "birth_year" in lineage
    assert "phone" in lineage


def test_review_queue_ranking():
    """Verify review queue prioritizes cut edges first, then lowest uncertainty |w - t_link|."""
    clusters_df = pd.DataFrame(
        {
            "record_id": ["r1", "r2", "r3", "r4"],
            "cluster_id": ["c1", "c1", "c2", "c3"],
        }
    )
    preds_df = pd.DataFrame(
        [
            # Cross-cluster within window: w=8.5 (uncertainty=0.5)
            {"record_id_l": "r2", "record_id_r": "r3", "match_weight": 8.5},
            # Cross-cluster within window: w=11.0 (uncertainty=2.0)
            {"record_id_l": "r1", "record_id_r": "r4", "match_weight": 11.0},
            # Intra-cluster within window: w=9.2 (uncertainty=0.2)
            {"record_id_l": "r1", "record_id_r": "r2", "match_weight": 9.2},
        ]
    )
    res_log_df = pd.DataFrame(
        [
            # Cut edge: w=14.0 (even though uncertainty is high, cut edge is ranked first!)
            {
                "component_id": "c_init",
                "action": "constraint_cut",
                "record_id_l": "r3",
                "record_id_r": "r4",
                "weight": 14.0,
                "reason": "sex_conflict",
            }
        ]
    )

    queue_df = build_review_queue(preds_df, clusters_df, res_log_df, t_link=9.0)
    assert len(queue_df) == 4

    # Top item must be the cut edge!
    assert queue_df.iloc[0]["is_cut_edge"]
    assert queue_df.iloc[0]["record_id_l"] == "r3"
    assert queue_df.iloc[0]["record_id_r"] == "r4"

    # Second item must be the lowest uncertainty uncut edge (|9.2 - 9.0| = 0.2)
    assert queue_df.iloc[1]["record_id_l"] == "r1"
    assert queue_df.iloc[1]["record_id_r"] == "r2"
    assert np.isclose(queue_df.iloc[1]["uncertainty"], 0.2)


def test_review_simulation_monotonic_toy(tmp_path):
    """Verify review simulation on toy graph exhibits non-increasing cost as K grows."""
    # Build toy run in tmp_path
    data_dir = tmp_path / "data" / "demo_toy"
    reg_dir = data_dir / "registry"
    truth_dir = data_dir / "truth"
    reg_dir.mkdir(parents=True)
    truth_dir.mkdir(parents=True)

    records_df = pd.DataFrame(
        {
            "record_id": ["r1", "r2", "r3", "r4"],
            "sex_raw": ["F", "F", "F", "F"],
            "birth_year_est": [1990, 1990, 1990, 1990],
        }
    )
    records_df.to_parquet(reg_dir / "records.parquet", index=False)

    # Truth: r1 and r2 are Person 1; r3 and r4 are Person 2
    truth_df = pd.DataFrame(
        {
            "record_id": ["r1", "r2", "r3", "r4"],
            "person_id": ["P1", "P1", "P2", "P2"],
        }
    )
    truth_df.to_parquet(truth_dir / "record_truth.parquet", index=False)

    true_pairs_df = pd.DataFrame(
        [
            {"record_id_1": "r1", "record_id_2": "r2"},
            {"record_id_1": "r3", "record_id_2": "r4"},
        ]
    )
    true_pairs_df.to_parquet(truth_dir / "true_pairs.parquet", index=False)

    results_dir = tmp_path / "results"
    res_splink = results_dir / "demo_toy" / "splink_v1"
    res_splink.mkdir(parents=True)
    res_method = results_dir / "demo_toy" / "splink_v1_resolved"
    res_method.mkdir(parents=True)

    # Scored predictions: r1-r2 has weak weight 8.0 (< t_link=9.0), so initially false negative
    preds_df = pd.DataFrame(
        [
            {"record_id_l": "r1", "record_id_r": "r2", "match_weight": 8.0},
            {"record_id_l": "r3", "record_id_r": "r4", "match_weight": 9.5},
        ]
    )
    preds_df.to_parquet(res_splink / "predictions.parquet", index=False)

    # Initial resolution at t_link=9.0: r1-r2 separated, r3-r4 merged
    clusters_df = pd.DataFrame(
        {
            "record_id": ["r1", "r2", "r3", "r4"],
            "cluster_id": ["c1", "c2", "c3", "c3"],
        }
    )
    clusters_df.to_parquet(res_method / "clusters.parquet", index=False)
    pd.DataFrame(columns=["action", "record_id_l", "record_id_r", "weight", "reason"]).to_parquet(
        res_method / "resolution_log.parquet", index=False
    )

    # Frozen thresholds
    sel_dir = results_dir / "splink_v1_resolved"
    sel_dir.mkdir(parents=True)
    import json

    with open(sel_dir / "selected_thresholds.json", "w") as f:
        json.dump({"t_link": 9.0, "t_bridge": 12.0}, f)

    # Review simulation: K=0 has 1 FN (cost=1.0). With K review, r1-r2 is merged -> cost=0.0!
    curve_df = simulate_clerical_review(
        run_name="demo_toy",
        method="splink_v1_resolved",
        base_data_dir=str(tmp_path / "data"),
        base_results_dir=str(results_dir),
        k_values=(0, 2500, 5000),
        write_md=False,
    )

    costs = curve_df["expected_cost"].tolist()
    assert costs[0] >= costs[1] >= costs[2]
    assert costs[-1] == 0.0


def test_resolve_report_mode_fails_without_selected_thresholds(tmp_path):
    """Verify report mode raises FileNotFoundError if selected_thresholds.json missing."""
    from barilink.cli import run_resolve

    # Fake run directory
    run_dir = tmp_path / "data" / "holdout_test" / "registry"
    run_dir.mkdir(parents=True)
    pd.DataFrame({"record_id": ["r1"]}).to_parquet(run_dir / "records.parquet")

    splink_dir = tmp_path / "results" / "holdout_test" / "splink_v1"
    splink_dir.mkdir(parents=True)
    pd.DataFrame(columns=["record_id_l", "record_id_r", "match_weight"]).to_parquet(
        splink_dir / "predictions.parquet"
    )

    with pytest.raises(FileNotFoundError, match="Selected thresholds file not found"):
        run_resolve(
            run_name="holdout_test",
            mode="report",
            base_data_dir=str(tmp_path / "data"),
            base_results_dir=str(tmp_path / "results"),
        )


def test_resolve_truth_access_forbidden():
    """Verify barilink.resolve contains zero forbidden string references."""
    resolve_dir = Path("src/barilink/resolve")
    violations = []
    for py_file in resolve_dir.rglob("*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            code = f.read()
        tree = ast.parse(code, filename=str(py_file))
        docstrings = set()
        mod_doc = ast.get_docstring(tree)
        if mod_doc:
            docstrings.add(mod_doc)
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                d = ast.get_docstring(n)
                if d:
                    docstrings.add(d)

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                s = node.value
                if s in docstrings:
                    continue
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

    assert not violations, f"Forbidden ground-truth reference found in resolve: {violations}"


def test_listed_as_other_member_cannot_link_cut():
    """Verify that listed_as_other_member triggers cannot-link min-cut in resolution."""
    records_df = pd.DataFrame(
        {
            "record_id": ["r1", "r2"],
            "sex_raw": [None, None],
            "birth_year_est": [1990, 1990],
        }
    )
    features_df = pd.DataFrame(
        {
            "record_id": ["r1", "r2"],
            "name_skeleton": ["FATEMA", "ROKEYA"],
            "roster_skels_v3": [[], ["FATEMA"]],
        }
    )
    preds_df = pd.DataFrame(
        [
            {"record_id_l": "r1", "record_id_r": "r2", "match_weight": 10.0},
        ]
    )

    # 1. With apply_listed_as_other_member=True: cannot-link cut severs the edge
    clusters_cut, log_cut = build_resolved_graph(
        preds_df,
        records_df,
        t_link=5.0,
        t_bridge=5.0,
        features_df=features_df,
        apply_listed_as_other_member=True,
    )
    c1 = clusters_cut[clusters_cut["record_id"] == "r1"]["cluster_id"].iloc[0]
    c2 = clusters_cut[clusters_cut["record_id"] == "r2"]["cluster_id"].iloc[0]
    assert c1 != c2, "r1 and r2 must be in distinct clusters due to listed_as_other_member"
    assert len(log_cut) == 1
    assert log_cut.iloc[0]["reason"] == "listed_as_other_member"

    # 2. With apply_listed_as_other_member=False: kept in same cluster
    clusters_kept, log_kept = build_resolved_graph(
        preds_df,
        records_df,
        t_link=5.0,
        t_bridge=5.0,
        features_df=features_df,
        apply_listed_as_other_member=False,
    )
    k1 = clusters_kept[clusters_kept["record_id"] == "r1"]["cluster_id"].iloc[0]
    k2 = clusters_kept[clusters_kept["record_id"] == "r2"]["cluster_id"].iloc[0]
    assert k1 == k2, "r1 and r2 must remain merged when apply_listed_as_other_member=False"
    assert len(log_kept) == 0

