"""Test that running evaluate summarize reproduces committed results/summary/*.json exactly
and verifies all authoritative reference values from PROJECT_CONTEXT.md.
"""

import json
from pathlib import Path

import pytest

from barilink.evaluate.summary import summarize_all


@pytest.mark.artifacts
def test_evaluate_summarize_reproduces_committed_jsons(tmp_path):
    summary_dir = Path("results/summary")
    required_files = [
        "leakage_comparison.json",
        "h1_dev_outcome.json",
        "h2_dev_outcome.json",
        "confirm_table.json",
        "household_table.json",
    ]

    # Verify committed files exist
    for fn in required_files:
        p = summary_dir / fn
        assert p.exists(), f"Committed summary file missing: {p}"

    # Re-run summarize into temporary directory
    tmp_out = tmp_path / "summary"
    summarize_all(
        results_dir="results",
        data_dir="data/generated",
        output_dir=tmp_out,
    )

    # Compare re-generated against committed files
    for fn in required_files:
        committed_p = summary_dir / fn
        regen_p = tmp_out / fn
        assert regen_p.exists(), f"Regenerated file missing: {regen_p}"

        with open(committed_p, "r", encoding="utf-8") as f:
            committed_json = json.load(f)
        with open(regen_p, "r", encoding="utf-8") as f:
            regen_json = json.load(f)

        assert (
            regen_json == committed_json
        ), f"Mismatch between regenerated and committed {fn}!"


@pytest.mark.artifacts
def test_summary_matches_authoritative_reference_values():
    """Assert all authoritative reference values committed in PROJECT_CONTEXT.md."""
    summary_dir = Path("results/summary")

    # 1. H1 reference dev costs: splink_v1 = 960 at w = 9.25, splink_v2 = 937
    with open(summary_dir / "h1_dev_outcome.json", "r", encoding="utf-8") as f:
        h1 = json.load(f)
    assert pytest.approx(960.0, abs=0.5) == h1["baseline_dev_cost"]
    assert pytest.approx(937.0, abs=0.5) == h1["candidate_dev_cost"]
    assert pytest.approx(9.25, abs=0.01) == h1["decision_threshold"]

    # 2. H2 reference dev costs: splink_v3 = 876 at w = 8.0,
    # splink_v3_1_resolved = 828, splink_k_resolved = 782
    with open(summary_dir / "h2_dev_outcome.json", "r", encoding="utf-8") as f:
        h2 = json.load(f)
    assert pytest.approx(937.0, abs=0.5) == h2["baseline_dev_cost"]
    assert pytest.approx(876.0, abs=0.5) == h2["candidate_dev_cost"]
    assert pytest.approx(8.00, abs=0.01) == h2["decision_threshold"]

    with open(summary_dir / "confirm_table.json", "r", encoding="utf-8") as f:
        confirm = json.load(f)
    dev_adopt = confirm["dev_adoption"]
    assert pytest.approx(828.0, abs=0.5) == dev_adopt["reference_dev_cost"]
    assert pytest.approx(782.0, abs=0.5) == dev_adopt["candidate_dev_cost"]

    # 3. Cost-ratio sensitivity (holdout_5..9, 5-seed mean paired K - ref):
    # 1:1 -> -8.8 (3/5 seeds), 2:1 -> -25.6 (5/5), 5:1 -> -76.0 (5/5), 10:1 -> -160.0 (5/5)
    cost_ratios = {row["ratio"]: row for row in confirm["cost_ratio_sensitivity"]}
    assert "20:1" not in cost_ratios, "There should be no 20:1 row in cost-ratio sensitivity"

    assert pytest.approx(-8.8, abs=0.5) == cost_ratios["1:1"]["delta_cost"]
    assert cost_ratios["1:1"]["seeds_won"] == "3/5 seeds"

    assert pytest.approx(-25.6, abs=0.5) == cost_ratios["2:1"]["delta_cost"]
    assert cost_ratios["2:1"]["seeds_won"] == "5/5 seeds"

    assert pytest.approx(-76.0, abs=0.5) == cost_ratios["5:1"]["delta_cost"]
    assert cost_ratios["5:1"]["seeds_won"] == "5/5 seeds"

    assert pytest.approx(-160.0, abs=0.5) == cost_ratios["10:1"]["delta_cost"]
    assert cost_ratios["10:1"]["seeds_won"] == "5/5 seeds"

    # 4. Household weight robustness:
    # x2 -> F1 0.2129, size MAE 7.21; x0.5 -> F1 0.3069, size MAE 1.70
    with open(summary_dir / "household_table.json", "r", encoding="utf-8") as f:
        hh = json.load(f)
    champ = hh["champion"]
    wr = hh["weight_robustness"]

    # Champion and base_1_0x must strictly come from ONE single source of truth
    assert champ["record_pairwise_f1_mean"] == wr["base_1_0x"]["record_pairwise_f1_mean"]
    assert champ["record_precision_mean"] == wr["base_1_0x"]["record_precision_mean"]
    assert pytest.approx(0.4601, abs=0.0005) == champ["record_pairwise_f1_mean"]
    assert pytest.approx(0.6886, abs=0.0005) == champ["record_precision_mean"]

    assert pytest.approx(0.2129, abs=0.0005) == wr["doubled_2_0x"]["record_pairwise_f1"]
    assert pytest.approx(7.21, abs=0.01) == wr["doubled_2_0x"]["household_size_mae"]

    assert pytest.approx(0.3069, abs=0.0005) == wr["halved_0_5x"]["record_pairwise_f1"]
    assert pytest.approx(1.70, abs=0.5) == wr["halved_0_5x"]["household_size_mae"]


@pytest.mark.artifacts
def test_publish_pipeline_household_metrics_match_holdout_5_in_confirm_json():
    """Assert that the publish pipeline's publish_holdout_5 household metrics equal
    the holdout_5 values in the 5-seed household JSON exactly (same code, same inputs).
    """
    hh_metrics_p = Path("results/publish_holdout_5/household/household_metrics.json")
    assert hh_metrics_p.exists(), f"Missing {hh_metrics_p}"

    with open(hh_metrics_p, "r", encoding="utf-8") as f:
        publish_hh = json.load(f)

    with open("results/holdout_confirm/household_table.json", "r", encoding="utf-8") as f:
        confirm_data = json.load(f)

    h5_confirm = confirm_data["champion"]["per_seed"]["holdout_5"]

    # Compare all headline metrics exactly
    assert publish_hh["record_pairwise_precision"] == h5_confirm["record_pairwise_precision"]
    assert publish_hh["record_pairwise_recall"] == h5_confirm["record_pairwise_recall"]
    assert publish_hh["record_pairwise_f1"] == h5_confirm["record_pairwise_f1"]
    assert publish_hh["unit_bcubed_f1"] == h5_confirm["unit_bcubed_f1"]
    assert publish_hh["households_reached_error_pct"] == h5_confirm["households_reached_error_pct"]
    assert publish_hh["household_size_mae"] == h5_confirm["household_size_mae"]
    assert publish_hh["n_inferred_households"] == h5_confirm["n_inferred_households"]
    assert publish_hh["n_cannot_household_cuts"] == h5_confirm["n_cannot_household_cuts"]
    assert publish_hh["n_max_size_cuts"] == h5_confirm["n_max_size_cuts"]


@pytest.mark.artifacts
def test_prefix_snapshot_matches_git_provenance():
    """Verify that results/summary/prefix_snapshot.json values match the historical
    pre-fix baseline_comparison.md file via git show <commit>:<path>."""
    import subprocess

    snapshot_path = Path("results/summary/prefix_snapshot.json")
    assert snapshot_path.exists(), f"Missing {snapshot_path}"

    with open(snapshot_path, "r", encoding="utf-8") as f:
        snapshot = json.load(f)

    commit = snapshot["commit"]
    path = snapshot["path"]
    git_ref = f"{commit}:{path}"

    raw_md = subprocess.check_output(
        ["git", "show", git_ref],
        text=True,
        encoding="utf-8",
    )

    methods = snapshot["methods"]
    v1 = methods["splink_v1_pre_fix"]
    v1_res = methods["splink_v1_resolved_pre_fix"]

    # Verify each pre-fix method against the table in baseline_comparison.md
    found_v1 = False
    found_v1_res = False

    for line in raw_md.splitlines():
        if "`splink_v1`" in line and "resolved" not in line:
            parts = [p.strip() for p in line.split("|")]
            assert f"{v1['cluster_precision_mean']:.4f}" in parts[2]
            assert f"{v1['cluster_recall_mean']:.4f}" in parts[3]
            assert f"{v1['cluster_f1_mean']:.4f}" in parts[4]
            assert f"{v1['doppelganger_fm_rate'] * 100:.2f}%" in parts[6]
            assert f"{v1['reach_error_pct_mean']:.2f}%" in parts[7]
            found_v1 = True
        elif "`splink_v1_resolved`" in line:
            parts = [p.strip() for p in line.split("|")]
            assert f"{v1_res['cluster_precision_mean']:.4f}" in parts[2]
            assert f"{v1_res['cluster_recall_mean']:.4f}" in parts[3]
            assert f"{v1_res['cluster_f1_mean']:.4f}" in parts[4]
            assert f"{v1_res['doppelganger_fm_rate'] * 100:.2f}%" in parts[6]
            assert f"{v1_res['reach_error_pct_mean']:.2f}%" in parts[7]
            found_v1_res = True

    assert found_v1, f"`splink_v1` not found in {git_ref}"
    assert found_v1_res, f"`splink_v1_resolved` not found in {git_ref}"


@pytest.mark.artifacts
def test_summary_py_contains_no_illegal_float_literals():
    """Verify that summary.py contains no float literals other than tolerances or 0/1/100."""
    import ast

    summary_file = Path("src/barilink/evaluate/summary.py")
    assert summary_file.exists()

    with open(summary_file, "r", encoding="utf-8") as f:
        code = f.read()

    tree = ast.parse(code)
    # Allowed float literals: 0.0, 1.0, 100.0, or tolerance (0.98 adoption margin discount)
    allowed_floats = {0.0, 1.0, 100.0, 0.98}

    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            if node.value not in allowed_floats:
                violations.append((node.lineno, node.value))

    assert not violations, (
        f"Found illegal float literals in summary.py (allowed only {allowed_floats}): "
        f"{violations}"
    )
