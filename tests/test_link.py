"""Unit and integration tests for Phase 4 normalisation, Splink modeling, and diagnostics."""

from __future__ import annotations

import ast
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from barilink.link.diagnostics import export_model_diagnostics
from barilink.link.model import (
    create_splink_settings,
    predict_splink_model,
    train_splink_model,
)
from barilink.link.normalise import (
    canonicalise_name,
    canonicalise_village,
    clean_text_basic,
    compute_name_tokens_sorted,
    compute_skeleton,
    extract_title_token,
    normalise_phone_11,
)


def test_splink4_imports_and_api():
    """Verify Splink 4 API classes are available and DuckDB backend functions."""
    import splink.comparison_level_library as cll
    import splink.comparison_library as cl
    from splink import DuckDBAPI, Linker, SettingsCreator, block_on

    db_api = DuckDBAPI()
    assert db_api is not None
    assert callable(block_on)
    assert hasattr(cl, "ExactMatch")
    assert hasattr(cll, "ExactMatchLevel")
    assert Linker is not None
    assert SettingsCreator is not None


def test_package_layout():
    """Verify required Phase 4 module files exist."""
    link_dir = Path("src/barilink/link")
    assert (link_dir / "__init__.py").exists()
    assert (link_dir / "normalise.py").exists()
    assert (link_dir / "model.py").exists()
    assert (link_dir / "diagnostics.py").exists()
    assert Path("src/barilink/evaluate/error_analysis.py").exists()


def test_link_truth_access_forbidden():
    """Verify barilink.link contains zero references to 'truth'."""
    link_dir = Path("src/barilink/link")
    violations = []
    for py_file in link_dir.rglob("*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            code = f.read()
        tree = ast.parse(code, filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                s = node.value
                if s == "truth" or "truth/" in s or "/truth" in s or "\\truth" in s:
                    violations.append((str(py_file), s))
    assert not violations, f"Forbidden truth directory reference found in: {violations}"


def test_normalise_does_not_import_generator_rules():
    """Verify normalise.py does not import or reference GENERATOR_ONLY_RULES."""
    norm_file = Path("src/barilink/link/normalise.py")
    with open(norm_file, "r", encoding="utf-8") as f:
        code = f.read()
    assert "GENERATOR_ONLY_RULES" not in code


def test_normaliser_examples():
    """Verify normalisation transformation rules per spec and approved amendments."""
    # 1. Prefix stripping & title extraction
    clean_mst = clean_text_basic("Mst. Rohima Khatoon")
    trimmed, title = extract_title_token(clean_mst)
    assert title == "khatun"
    assert trimmed == "rohima"

    # 2. Canonical ordering: Khatoon -> katun (oo->u runs before o->a, kh->k)
    canon_khatoon = canonicalise_name("khatoon")
    canon_khatun = canonicalise_name("khatun")
    assert canon_khatoon == "katun"
    assert canon_khatun == "katun"
    assert canon_khatoon == canon_khatun

    # 3. Vowel shift equivalence: Rohima vs Rahima
    canon_rohima = canonicalise_name("rohima")
    canon_rahima = canonicalise_name("rahima")
    assert canon_rohima == "rahima"
    assert canon_rahima == "rahima"

    # 4. Generator-only distinction: Kolsum vs Kulsum remain distinct
    canon_kolsum = canonicalise_name("kolsum")
    canon_kulsum = canonicalise_name("kulsum")
    assert canon_kolsum == "kalsum"
    assert canon_kulsum == "kulsum"
    assert canon_kolsum != canon_kulsum

    # 5. Hyphen and space removal
    clean_karim1 = clean_text_basic("Md. Abdul-Karim")
    clean_karim2 = clean_text_basic("Abdulkarim")
    assert canonicalise_name(clean_karim1) == "abdulkarim"
    assert canonicalise_name(clean_karim2) == "abdulkarim"

    # 6. Phone normalisation
    p_norm, p_last8 = normalise_phone_11("+880 1712-345678")
    assert p_norm == "01712345678"
    assert p_last8 == "12345678"

    # 7. Village canonicalisation
    assert canonicalise_village("Uttar Para") == "uttarpara"
    assert canonicalise_village("Mondal Para") == "mandalpara"


def test_consonant_skeleton_from_canon():
    """Verify consonant skeleton computation keeps 1st char, drops vowels, collapses dupes."""
    # rahima -> rhm
    assert compute_skeleton("rahima") == "rhm"
    # khatun -> khtn
    assert compute_skeleton("khatun") == "khtn"
    # abdulkarim -> abdlkrm
    assert compute_skeleton("abdulkarim") == "abdlkrm"
    # hassain -> hsn
    assert compute_skeleton("hassain") == "hsn"


def test_name_tokens_sorted():
    """Verify Amendment 4: canonical tokens sorted alphabetically handle transposition."""
    res1 = compute_name_tokens_sorted("Mia Abdul Karim")
    res2 = compute_name_tokens_sorted("Abdul Karim Mia")
    assert res1 == "abdulkarimmia"
    assert res2 == "abdulkarimmia"
    assert res1 == res2


def test_kinship_redesign_levels():
    """Verify Amendment 1: kinship comparison levels and null handling."""
    from splink import DuckDBAPI, Linker

    config = {
        "linkage": {
            "use_term_frequency": False,
            "use_kinship": True,
        }
    }
    settings = create_splink_settings(config)

    # Record 1 & 2: same guardian skeleton, but neither has rosters -> falls in NULL level
    # Record 3: has roster containing 'g1' -> cross-household match with Record 1
    # Record 4: has roster ['a', 'b', 'c'], Record 5: has roster ['a', 'b', 'd'] -> intersect >= 2
    df = pd.DataFrame([
        {
            "record_id": "r1",
            "name_clean": "a",
            "name_canon": "a",
            "name_skeleton": "a",
            "given_first_skel": "a",
            "name_tokens_sorted": "a",
            "title_token": "khatun",
            "guardian_clean": "g",
            "guardian_canon": "g",
            "guardian_skeleton": "g1",
            "phone_norm": "01711111111",
            "phone_last8": "11111111",
            "birth_year_est": 1990,
            "village_canon": "vil",
            "union_raw": "u",
            "sex_raw": "F",
            "source_module": "m",
            "enrolment_date": "2024-01-01",
            "roster_skels": None,
        },
        {
            "record_id": "r2",
            "name_clean": "b",
            "name_canon": "b",
            "name_skeleton": "b",
            "given_first_skel": "b",
            "name_tokens_sorted": "b",
            "title_token": "khatun",
            "guardian_clean": "g",
            "guardian_canon": "g",
            "guardian_skeleton": "g1",
            "phone_norm": "01722222222",
            "phone_last8": "22222222",
            "birth_year_est": 1991,
            "village_canon": "vil",
            "union_raw": "u",
            "sex_raw": "F",
            "source_module": "m",
            "enrolment_date": "2024-01-01",
            "roster_skels": None,
        },
        {
            "record_id": "r3",
            "name_clean": "a",
            "name_canon": "a",
            "name_skeleton": "a",
            "given_first_skel": "a",
            "name_tokens_sorted": "a",
            "title_token": "khatun",
            "guardian_clean": "h",
            "guardian_canon": "h",
            "guardian_skeleton": "h1",
            "phone_norm": "01733333333",
            "phone_last8": "33333333",
            "birth_year_est": 1992,
            "village_canon": "vil",
            "union_raw": "u",
            "sex_raw": "F",
            "source_module": "m",
            "enrolment_date": "2024-01-01",
            "roster_skels": ["g1", "x2"],
        },
    ])

    linker = Linker(df, settings, DuckDBAPI())
    preds = linker.inference.predict().as_pandas_dataframe()

    # r1 and r2: both rosters are null -> gamma_kinship must be -1 (null level)
    pair_1_2 = preds[
        ((preds["record_id_l"] == "r1") & (preds["record_id_r"] == "r2"))
        | ((preds["record_id_l"] == "r2") & (preds["record_id_r"] == "r1"))
    ]
    assert len(pair_1_2) == 1
    assert pair_1_2.iloc[0]["gamma_kinship"] == -1

    # r1 and r3: r3's roster contains r1's guardian 'g1' -> cross-household level (gamma=2)
    pair_1_3 = preds[
        ((preds["record_id_l"] == "r1") & (preds["record_id_r"] == "r3"))
        | ((preds["record_id_l"] == "r3") & (preds["record_id_r"] == "r1"))
    ]
    assert len(pair_1_3) == 1
    assert pair_1_3.iloc[0]["gamma_kinship"] == 2


def test_training_determinism():
    """Verify Amendment 5: single-threaded DuckDB connection achieves determinism."""
    df = pd.DataFrame([
        {
            "record_id": f"r{i}",
            "name_clean": f"name{i % 5}",
            "name_canon": f"name{i % 5}",
            "name_skeleton": f"nm{i % 5}",
            "given_first_skel": f"nm{i % 5}",
            "name_tokens_sorted": f"name{i % 5}",
            "title_token": "khatun" if i % 2 == 0 else "begum",
            "guardian_clean": f"guard{i % 4}",
            "guardian_canon": f"guard{i % 4}",
            "guardian_skeleton": f"grd{i % 4}",
            "phone_norm": f"0170000000{i % 10}",
            "phone_last8": f"000000{i % 10:02d}",
            "birth_year_est": 1980 + (i % 10),
            "village_canon": f"village{i % 3}",
            "union_raw": f"union{i % 2}",
            "sex_raw": "F" if i % 2 == 0 else "M",
            "source_module": "livelihood_support",
            "enrolment_date": "2024-01-01",
            "roster_skels": [f"skel{i % 3}"] if i % 3 != 0 else None,
        }
        for i in range(100)
    ])

    config = {
        "seed": 42,
        "linkage": {
            "use_term_frequency": False,
            "use_kinship": True,
            "prob_random_match_recall": 0.60,
            "u_max_pairs": 10000,
        },
    }

    with tempfile.TemporaryDirectory() as tmp_dir:
        m1_path = Path(tmp_dir) / "m1.json"
        m2_path = Path(tmp_dir) / "m2.json"

        # Train run 1 with threads=1
        train_splink_model(df, config, m1_path, threads=1)
        preds1, _, _ = predict_splink_model(df, m1_path, "test1", tmp_dir, threads=1)

        # Train run 2 with threads=1
        train_splink_model(df, config, m2_path, threads=1)
        preds2, _, _ = predict_splink_model(df, m2_path, "test2", tmp_dir, threads=1)

        # Merge on record pairs and compare match_weight
        merged = pd.merge(preds1, preds2, on=["record_id_l", "record_id_r"], suffixes=("_1", "_2"))
        diff = np.abs(merged["match_weight_1"] - merged["match_weight_2"]).max()
        assert diff < 1e-6, f"Non-deterministic match weights: max difference was {diff}"


def test_holdout_model_persistence():
    """Verify model loaded from JSON on holdout has identical m and u parameters."""
    with tempfile.TemporaryDirectory():
        model_path = Path("results/models/splink_v1/model.json")
        if not model_path.exists():
            pytest.skip("splink_v1 model.json does not exist yet")

        features_path = Path("data/generated/demo/registry/features.parquet")
        if not features_path.exists():
            pytest.skip("features.parquet does not exist yet")

        features_df = pd.read_parquet(features_path)
        from splink import DuckDBAPI, Linker

        db1 = DuckDBAPI()
        db2 = DuckDBAPI()
        linker1 = Linker(features_df, str(model_path), db1)
        linker2 = Linker(features_df, str(model_path), db2)

        # Compare settings dicts
        s1 = linker1._settings_obj.as_dict()
        s2 = linker2._settings_obj.as_dict()

        for c1, c2 in zip(s1["comparisons"], s2["comparisons"]):
            assert c1["output_column_name"] == c2["output_column_name"]
            for l1, l2 in zip(c1["comparison_levels"], c2["comparison_levels"]):
                assert np.isclose(
                    l1.get("m_probability", 0.0), l2.get("m_probability", 0.0), atol=1e-6
                )
                assert np.isclose(
                    l1.get("u_probability", 0.0), l2.get("u_probability", 0.0), atol=1e-6
                )


def test_diagnostics_and_error_analysis():
    """Verify diagnostic HTML charts and markdown error analysis export."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        model_path = Path("results/models/splink_v1/model.json")
        if not model_path.exists():
            pytest.skip("splink_v1 model.json does not exist yet")

        charts_dir = Path(tmp_dir) / "charts"
        w_path, mu_path = export_model_diagnostics(model_path, charts_dir)
        assert w_path.exists()
        assert mu_path.exists()
        assert w_path.stat().st_size > 0
        assert mu_path.stat().st_size > 0
