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
    """Verify that pipeline determinism fails if metrics drift beyond tolerance."""
    real_exp_path = Path("results/publish/expected_headline.json")
    if not real_exp_path.exists():
        pytest.skip("results/publish/expected_headline.json not yet generated")

    with open(real_exp_path, "r", encoding="utf-8") as f:
        tampered = json.load(f)

    # Drift precision by 0.05 (well beyond 0.005 tolerance)
    tampered["metrics"]["person_linkage"]["cluster_precision"] += 0.05
    tampered_file = tmp_path / "tampered_headline.json"
    with open(tampered_file, "w", encoding="utf-8") as f:
        json.dump(tampered, f)

    assert (
        verify_pipeline(run_name="holdout_5", expected_path=str(tampered_file)) is False
    )

