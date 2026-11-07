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

    # 2. H2 reference dev costs: splink_v3 = 875 at w = 8.0, splink_v3_1_resolved = 828, splink_k_resolved = 782
    with open(summary_dir / "h2_dev_outcome.json", "r", encoding="utf-8") as f:
        h2 = json.load(f)
    assert pytest.approx(937.0, abs=0.5) == h2["baseline_dev_cost"]
    assert pytest.approx(875.0, abs=0.5) == h2["candidate_dev_cost"]
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

    # 4. Household weight robustness: x2 -> F1 0.2055, size MAE 7.40; x0.5 -> F1 0.3069, size MAE 1.70
    with open(summary_dir / "household_table.json", "r", encoding="utf-8") as f:
        hh = json.load(f)
    champ = hh["champion"]
    wr = hh["weight_robustness"]

    # Champion and base_1_0x must strictly come from ONE single source of truth
    assert champ["record_pairwise_f1_mean"] == wr["base_1_0x"]["record_pairwise_f1_mean"]
    assert champ["record_precision_mean"] == wr["base_1_0x"]["record_precision_mean"]
    assert pytest.approx(0.4592, abs=0.0005) == champ["record_pairwise_f1_mean"]
    assert pytest.approx(0.6848, abs=0.0005) == champ["record_precision_mean"]

    assert pytest.approx(0.2055, abs=0.0005) == wr["doubled_2_0x"]["record_pairwise_f1"]
    assert pytest.approx(7.40, abs=0.5) == wr["doubled_2_0x"]["household_size_mae"]

    assert pytest.approx(0.3069, abs=0.0005) == wr["halved_0_5x"]["record_pairwise_f1"]
    assert pytest.approx(1.70, abs=0.5) == wr["halved_0_5x"]["household_size_mae"]
