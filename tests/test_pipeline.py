"""Tests for reproducible pipeline runner and verification."""

import json
from pathlib import Path

import pytest

from barilink.pipeline import (
    _validate_publish_spec,
    run_pipeline,
    verify_pipeline,
)


def test_publish_spec_validation():
    """Verify that the committed publish spec is valid and matches model artifacts."""
    spec_path = Path("results/publish/publish_spec.json")
    spec = _validate_publish_spec(spec_path)
    assert spec["profile"] == "publish"
    assert spec["linkage_switches"]["use_kinship"] is False
    assert spec["linkage_switches"]["kinship_constraint"] is True


def test_publish_spec_missing_fails(tmp_path: Path):
    """Verify that missing publish spec fails loudly without fallback."""
    fake_path = tmp_path / "non_existent_spec.json"
    with pytest.raises(FileNotFoundError, match="Frozen publish spec missing"):
        _validate_publish_spec(fake_path)


def test_publish_spec_invalid_model_fails(tmp_path: Path):
    """Verify that a model containing a kinship comparison fails validation."""
    fake_model_path = tmp_path / "fake_model.json"
    fake_model = {
        "probability_two_random_records_match": 0.001,
        "comparisons": [{"output_column_name": "kinship"}],
    }
    with open(fake_model_path, "w", encoding="utf-8") as f:
        json.dump(fake_model, f)

    fake_spec_path = tmp_path / "fake_spec.json"
    fake_spec = {
        "model_path": str(fake_model_path),
        "resolve_thresholds_path": "results/splink_k_resolved/selected_thresholds.json",
        "household_thresholds_path": "results/household/selected_thresholds.json",
    }
    with open(fake_spec_path, "w", encoding="utf-8") as f:
        json.dump(fake_spec, f)

    with pytest.raises(ValueError, match="violating frozen Pipeline K specification"):
        _validate_publish_spec(fake_spec_path)


def test_ci_pipeline_end_to_end(tmp_path: Path):
    """Verify that the CI profile executes end-to-end under tmp_path."""
    data_dir = tmp_path / "data"
    results_dir = tmp_path / "results"
    web_dir = tmp_path / "web_data"

    summary = run_pipeline(
        profile="ci",
        run_name="ci_smoke",
        config_path="configs/ci.yaml",
        base_data_dir=str(data_dir),
        base_results_dir=str(results_dir),
        web_dir=str(web_dir),
    )

    assert summary["profile"] == "ci"
    assert "person_linkage" in summary
    assert "household_inference" in summary
    assert (web_dir / "manifest.json").exists()


@pytest.mark.publish
def test_verify_pipeline_passes():
    """Verify that pipeline --verify passes against current holdout_5 outputs."""
    assert verify_pipeline(run_name="holdout_5") is True


def test_verify_pipeline_detects_mismatch(tmp_path: Path):
    """Verify that pipeline determinism comparator fails if metrics drift beyond tolerance."""
    mock_run_dir = tmp_path / "mock_run"
    p_dir = mock_run_dir / "splink_k_resolved"
    hh_dir = mock_run_dir / "household"
    p_dir.mkdir(parents=True, exist_ok=True)
    hh_dir.mkdir(parents=True, exist_ok=True)

    p_metrics = {
        "headline_metrics_at_t_cost": {
            "cluster_precision": 0.9650,
            "cluster_recall": 0.5560,
            "cluster_f1": 0.7050,
            "expected_cost": 784.0,
            "false_merge_clusters": 23,
            "split_persons": 427,
            "dedup_reach": 4136,
            "doppelganger_false_merge_rate": 0.0125,
        }
    }
    with open(p_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(p_metrics, f)

    hh_metrics = {
        "record_pairwise_precision": 0.7000,
        "record_pairwise_recall": 0.3520,
        "record_pairwise_f1": 0.4680,
        "unit_bcubed_f1": 0.7530,
        "household_size_mae": 2.0100,
        "households_reached_error_pct": 57.9000,
        "n_inferred_households": 3608,
    }
    with open(hh_dir / "household_metrics.json", "w", encoding="utf-8") as f:
        json.dump(hh_metrics, f)

    expected = {
        "metrics": {
            "person_linkage": p_metrics["headline_metrics_at_t_cost"],
            "household_inference": hh_metrics,
        }
    }
    exp_file = tmp_path / "expected_mock.json"
    with open(exp_file, "w", encoding="utf-8") as f:
        json.dump(expected, f)

    # 1. Matching metrics -> returns True
    assert (
        verify_pipeline(
            run_name="mock_run",
            results_dir=str(tmp_path),
            expected_path=str(exp_file),
        )
        is True
    )

    # 2. Tampered precision (drift by 0.05, exceeding 0.005 tol) -> returns False
    tampered = dict(expected)
    tampered["metrics"]["person_linkage"]["cluster_precision"] += 0.05
    tampered_file = tmp_path / "tampered_mock.json"
    with open(tampered_file, "w", encoding="utf-8") as f:
        json.dump(tampered, f)

    assert (
        verify_pipeline(
            run_name="mock_run",
            results_dir=str(tmp_path),
            expected_path=str(tampered_file),
        )
        is False
    )

