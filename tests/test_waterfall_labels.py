"""Test that exported model_summary.json comparison level_map
matches Splink's own level assignments."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
from splink import SettingsCreator

from barilink.export.web import build_model_summary


def test_build_model_summary_level_map_unit(tmp_path: Path) -> None:
    """CI-safe unit test for build_model_summary using a hand-built Splink settings dict."""
    model_file = tmp_path / "tiny_model.json"
    settings = {
        "link_type": "dedupe_only",
        "probability_two_random_records_match": 0.05,
        "blocking_rules_to_generate_predictions": ["l.first_name = r.first_name"],
        "comparisons": [
            {
                "output_column_name": "first_name",
                "comparison_levels": [
                    {
                        "sql_condition": "first_name_l IS NULL OR first_name_r IS NULL",
                        "label_for_charts": "first_name is NULL",
                        "is_null_level": True,
                    },
                    {
                        "sql_condition": "first_name_l = first_name_r",
                        "label_for_charts": "Exact match on first_name",
                        "m_probability": 0.8,
                        "u_probability": 0.1,
                    },
                    {
                        "sql_condition": "ELSE",
                        "label_for_charts": "All other comparisons",
                        "m_probability": 0.2,
                        "u_probability": 0.9,
                    },
                ],
            }
        ],
    }
    with open(model_file, "w", encoding="utf-8") as f:
        json.dump(settings, f)

    sc = SettingsCreator.from_path_or_dict(model_file)
    summary = build_model_summary(sc)

    assert summary["prior"] == 0.05
    assert len(summary["comparisons"]) == 1
    comp = summary["comparisons"][0]
    assert comp["name"] == "first_name"

    level_map = comp["level_map"]
    # CVV -1: NULL level
    assert "-1" in level_map
    assert level_map["-1"]["label"] == "first_name is NULL"
    assert level_map["-1"]["m"] is None
    assert level_map["-1"]["u"] is None
    assert level_map["-1"]["bf"] == 1.0

    # CVV 1: Exact match
    assert "1" in level_map
    assert level_map["1"]["label"] == "Exact match on first_name"
    assert level_map["1"]["m"] == 0.8
    assert level_map["1"]["u"] == 0.1
    assert level_map["1"]["bf"] == 8.0

    # CVV 0: Else
    assert "0" in level_map
    assert level_map["0"]["label"] == "All other comparisons"
    assert level_map["0"]["m"] == 0.2
    assert level_map["0"]["u"] == 0.9


@pytest.mark.publish
def test_exported_level_map_matches_splink_levels() -> None:
    summary_path = Path("web/public/data/model_summary.json")
    assert summary_path.exists(), "web/public/data/model_summary.json missing"

    with open(summary_path, "r", encoding="utf-8") as f:
        model_summary = json.load(f)

    # Load Splink settings object
    sc = SettingsCreator.from_path_or_dict("results/models/splink_k/model.json")
    settings_obj = sc.get_settings("duckdb")

    comp_dict = {c.output_column_name: c for c in settings_obj.comparisons}

    for comp_exported in model_summary["comparisons"]:
        name = comp_exported["name"]
        assert name in comp_dict, f"Comparison {name} not in Splink settings"
        splink_comp = comp_dict[name]

        level_map = comp_exported.get("level_map") or comp_exported.get("levels_by_cvv")
        assert level_map is not None, f"Comparison {name} missing level_map"

        for cl in splink_comp.comparison_levels:
            cvv_str = str(cl.comparison_vector_value)
            assert cvv_str in level_map, f"Level {cvv_str} not in exported map for {name}"
            exported_level = level_map[cvv_str]
            expected_chart_label = cl.label_for_charts
            assert (
                exported_level["label"] == expected_chart_label
            ), (
                f"Label mismatch for {name} level {cvv_str}: "
                f"{exported_level['label']} vs {expected_chart_label}"
            )


@pytest.mark.publish
def test_exported_level_map_on_real_pairs() -> None:
    """Verify that applying exported level_map to gamma columns on real pairs
    yields correct labels."""
    summary_path = Path("web/public/data/model_summary.json")
    pairs_path = Path("web/public/data/pairs.parquet")
    assert pairs_path.exists()

    with open(summary_path, "r", encoding="utf-8") as f:
        model_summary = json.load(f)

    level_lookups = {
        c["name"]: (c.get("level_map") or c.get("levels_by_cvv"))
        for c in model_summary["comparisons"]
    }

    sc = SettingsCreator.from_path_or_dict("results/models/splink_k/model.json")
    settings_obj = sc.get_settings("duckdb")
    splink_lookups = {
        c.output_column_name: {
            cl.comparison_vector_value: cl.label_for_charts for cl in c.comparison_levels
        }
        for c in settings_obj.comparisons
    }

    pairs_df = pd.read_parquet(pairs_path).head(100)
    for _, row in pairs_df.iterrows():
        for comp_name, splink_map in splink_lookups.items():
            gamma_key = f"gamma_{comp_name}"
            if gamma_key in row:
                gamma_val = int(row[gamma_key])
                expected_label = splink_map[gamma_val]
                exported_label = level_lookups[comp_name][str(gamma_val)]["label"]
                assert (
                    exported_label == expected_label
                ), f"Pair {row['record_id_l']} vs {row['record_id_r']} mismatch on {comp_name}"
