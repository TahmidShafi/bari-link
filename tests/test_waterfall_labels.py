"""Test that exported model_summary.json comparison level_map matches Splink's own level assignments."""

import json
from pathlib import Path
import pandas as pd
import pytest
from splink import SettingsCreator


def test_exported_level_map_matches_splink_levels():
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
            assert (
                exported_level["label"] == cl.label_for_charts
            ), f"Label mismatch for {name} level {cvv_str}: {exported_level['label']} vs {cl.label_for_charts}"


def test_exported_level_map_on_real_pairs():
    """Verify that applying exported level_map to gamma columns on real pairs yields correct labels."""
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

