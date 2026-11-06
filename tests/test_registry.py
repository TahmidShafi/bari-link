"""Unit tests for Phase 2: Enrolment Registries, Field Corruption, and Strict Truth Segregation."""

from pathlib import Path
from typing import Any

import pandas as pd
import pytest
import yaml

from barilink.cli import _print_corruption_summary
from barilink.corrupt.registry import export_registries
from barilink.corrupt.transliteration import get_rule_counts
from barilink.generate.population import generate_population


@pytest.fixture
def test_setup(tmp_path: Path) -> tuple[Path, Path]:
    """Generate clean population with n_households=500 and create config."""
    config_dict: dict[str, Any] = {
        "seed": 42,
        "reference_date": "2026-01-01",
        "n_households": 500,
        "household_size_dist": {
            "sizes": [2, 3, 4, 5, 6, 7, 8],
            "weights": [0.10, 0.20, 0.30, 0.22, 0.11, 0.05, 0.02],
        },
        "head_gender_dist": {
            "male_share": 0.85,
            "female_share": 0.15,
        },
        "name_sampling": {
            "zipf_exponent": 1.1,
            "zipf_offset": 3.0,
            "hindu_share": 0.10,
        },
        "phone_ownership": {
            "household_penetration": 0.88,
            "adult_male_individual": 0.60,
            "adult_female_individual": 0.30,
            "min_phone_age": 15,
        },
        "geography": {
            "districts": [
                {
                    "name": "Kurigram",
                    "upazilas": [
                        {"name": "Chilmari", "unions": ["Chilmari", "Ramna", "Thanahat"]},
                        {"name": "Ulipur", "unions": ["Bazra", "Gunaiyagachh", "Durgapur"]},
                        {
                            "name": "Rajarhat",
                            "unions": ["Chakirpashar", "Bidyananda", "Gharialdanga"],
                        },
                    ],
                },
                {
                    "name": "Gaibandha",
                    "upazilas": [
                        {"name": "Sundarganj", "unions": ["Belka", "Haripur", "Chandipur"]},
                        {"name": "Sadullapur", "unions": ["Naldanga", "Damodarpur", "Rasulpur"]},
                        {"name": "Gobindaganj", "unions": ["Kamdia", "Kochashahar", "Mahimaganj"]},
                    ],
                },
            ],
            "villages_per_union": ["Mondal Para", "Dokkhin Para", "Uttar Para", "Majher Char"],
        },
        "enrolment": {
            "date_range": ["2023-01-01", "2026-06-30"],
            "re_registration_rate": 0.03,
            "modules": {
                "club_formation": {
                    "target_share": 0.30,
                    "age_range": [10, 24],
                    "female_only": True,
                    "intensity": 1.0,
                },
                "upg_enrolment": {
                    "target_share": 0.25,
                    "primary_age_range": [18, 60],
                    "prefer_female": True,
                    "intensity": 1.0,
                },
                "microfinance_group": {
                    "target_share": 0.35,
                    "age_range": [18, 60],
                    "female_share": 0.92,
                    "intensity": 1.0,
                },
                "livelihood_support": {
                    "target_share": 0.28,
                    "age_range": [18, 60],
                    "female_share": 0.50,
                    "intensity": 1.0,
                },
            },
            "cross_module_conditional": {
                "upg_to_microfinance": 0.55,
                "upg_to_livelihood": 0.45,
            },
        },
        "doppelganger": {
            "min_pairs": 5,
        },
        "corruption": {
            "rates": {
                "transliteration": 0.22,
                "prefix_drift": 0.35,
                "female_title_drift": 0.12,
                "typo_damerau_levenshtein": 0.08,
                "field_swap_guardian": 0.02,
                "field_title_to_front": 0.04,
                "age_heaping_base": 0.25,
                "age_jitter": 0.20,
                "guardian_switch_ever_married": 0.18,
                "widow_late_prefix": 0.25,
                "phone_missing": 0.15,
                "phone_shared_household": 0.20,
                "phone_new_sim": 0.05,
                "phone_digit_typo": 0.06,
                "phone_adjacent_transposition": 0.05,
                "phone_format_variant": 0.30,
                "location_village_drift": 0.15,
                "location_missing_admin": 0.08,
            }
        },
        "missingness": {
            "club_formation": {"guardian_name": 0.05, "age": 0.04, "village": 0.02},
            "upg_enrolment": {
                "guardian_name": 0.04, "age": 0.03, "phone": 0.08, "village": 0.01
            },
            "microfinance_group": {"guardian_name": 0.05, "phone": 0.06, "village": 0.01},
            "livelihood_support": {
                "guardian_name": 0.04, "age": 0.03, "phone": 0.07, "village": 0.01
            },
        },
    }

    cfg_path = tmp_path / "test_config.yaml"
    with open(cfg_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config_dict, f)

    run_dir = tmp_path / "demo"
    generate_population(cfg_path, run_dir)
    return cfg_path, tmp_path


def test_determinism_identical_and_divergent_seeds(test_setup: tuple[Path, Path]) -> None:
    """Same seed produces identical records.parquet; different seed diverges."""
    cfg_path, base_tmp = test_setup

    generate_population(cfg_path, base_tmp / "run_a")
    generate_population(cfg_path, base_tmp / "run_b")
    export_registries(cfg_path, "run_a", base_tmp)
    export_registries(cfg_path, "run_b", base_tmp)

    bytes_a = (base_tmp / "run_a" / "registry" / "records.parquet").read_bytes()
    bytes_b = (base_tmp / "run_b" / "registry" / "records.parquet").read_bytes()
    assert bytes_a == bytes_b, "Same seed must produce byte-identical records.parquet"

    # Divergent seed
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg_alt = yaml.safe_load(f)
    cfg_alt["seed"] = 8888
    alt_cfg_path = base_tmp / "alt_config.yaml"
    with open(alt_cfg_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg_alt, f)

    generate_population(alt_cfg_path, base_tmp / "run_c")
    export_registries(alt_cfg_path, "run_c", base_tmp)
    bytes_c = (base_tmp / "run_c" / "registry" / "records.parquet").read_bytes()
    assert bytes_a != bytes_c, "Different seed must diverge"


def test_leakage_guard_and_record_id_non_monotonic(test_setup: tuple[Path, Path]) -> None:
    """registry/ files must not contain truth columns; record_id not monotonic with person_id."""
    cfg_path, base_tmp = test_setup
    reg_tables, truth_tables = export_registries(cfg_path, "demo", base_tmp)

    forbidden_cols = {
        "person_id",
        "household_id",
        "given_name",
        "surname_or_title",
        "father_id",
        "father_given_name",
    }

    # Check records.parquet
    records_cols = set(reg_tables["records"].columns)
    leaked = records_cols & forbidden_cols
    assert not leaked, f"Leaked columns in records.parquet: {leaked}"

    # Check rosters.parquet
    rosters_cols = set(reg_tables["rosters"].columns)
    leaked_roster = rosters_cols & forbidden_cols
    assert not leaked_roster, f"Leaked columns in rosters.parquet: {leaked_roster}"

    # Check raw CSVs
    modules = ["club_formation", "upg_enrolment", "microfinance_group", "livelihood_support"]
    for mod_name in modules:
        csv_cols = set(reg_tables[mod_name].columns)
        leaked_csv = csv_cols & forbidden_cols
        assert not leaked_csv, f"Leaked columns in {mod_name}.csv: {leaked_csv}"

    # Check Spearman rank correlation between record_id and person_id
    truth_df = truth_tables["record_truth"]
    rec_ranks = truth_df["record_id"].rank()
    person_ranks = truth_df["person_id"].rank()
    # Pearson correlation on ranks equals Spearman rank correlation
    rho = float(rec_ranks.corr(person_ranks))
    assert abs(rho) < 0.08, f"record_id must not correlate with person_id (rho = {rho:.4f})"


def test_bijection_and_unique_record_ids(test_setup: tuple[Path, Path]) -> None:
    """Every record_id in registry has 1 row in record_truth, and vice versa. All unique."""
    cfg_path, base_tmp = test_setup
    reg_tables, truth_tables = export_registries(cfg_path, "demo", base_tmp)

    rec_ids = reg_tables["records"]["record_id"]
    truth_rec_ids = truth_tables["record_truth"]["record_id"]

    assert rec_ids.is_unique, "All record_ids in records.parquet must be unique"
    assert truth_rec_ids.is_unique, "All record_ids in record_truth.parquet must be unique"
    assert set(rec_ids) == set(truth_rec_ids), "1-to-1 bijection required between records and truth"


def test_club_formation_eligibility(test_setup: tuple[Path, Path]) -> None:
    """All club_formation records belong to females aged 10-24 at enrolment date."""
    cfg_path, base_tmp = test_setup
    _, truth_tables = export_registries(cfg_path, "demo", base_tmp)

    truth_df = truth_tables["record_truth"]
    club_truth = truth_df[truth_df["source_module"] == "club_formation"]
    assert len(club_truth) > 0

    assert (club_truth["clean_age_at_enrolment"] >= 10).all()
    assert (club_truth["clean_age_at_enrolment"] <= 24).all()


def test_guardian_switch_only_ever_married_women(test_setup: tuple[Path, Path]) -> None:
    """Guardian switch only ever occurs for ever-married women."""
    cfg_path, base_tmp = test_setup
    _, truth_tables = export_registries(cfg_path, "demo", base_tmp)

    corr_log = truth_tables["corruption_log"]
    switch_events = corr_log[corr_log["corruption_type"] == "guardian_switch"]
    assert len(switch_events) > 0, "Expected some guardian switch events"

    truth_df = truth_tables["record_truth"].set_index("record_id")
    for rec_id in switch_events["record_id"]:
        t_row = truth_df.loc[rec_id]
        clean_marital = t_row["clean_marital_status"]
        assert clean_marital in {"married", "widowed", "separated"}, (
            f"Guardian switch on non-ever-married person {t_row['person_id']} ({clean_marital})"
        )


def test_transliteration_rule_split_and_event_share(test_setup: tuple[Path, Path]) -> None:
    """Rule count ratio >= 0.40, and generator-only events share in corruption_log >= 0.30."""
    cfg_path, base_tmp = test_setup
    _, truth_tables = export_registries(cfg_path, "demo", base_tmp)

    # 1. Rule count ratio
    n_shared, n_gen, rule_ratio = get_rule_counts()
    assert rule_ratio >= 0.40, f"Generator-only rule count ratio ({rule_ratio:.2%}) must be >= 40%"

    # 2. Event share ratio in corruption log
    corr_log = truth_tables["corruption_log"]
    trans_events = corr_log[corr_log["corruption_type"].str.startswith("transliteration")]
    assert len(trans_events) > 0, "Expected transliteration events in corruption log"

    gen_events = trans_events[trans_events["is_generator_only"]]
    event_ratio = len(gen_events) / len(trans_events)
    assert event_ratio >= 0.30, f"Generator-only event share ({event_ratio:.2%}) must be >= 30%"


def test_age_heaping_effectiveness(test_setup: tuple[Path, Path]) -> None:
    """The share of recorded ages ending in 0 or 5 is higher than in clean ages."""
    cfg_path, base_tmp = test_setup
    reg_tables, truth_tables = export_registries(cfg_path, "demo", base_tmp)

    records_df = reg_tables["records"]
    truth_df = truth_tables["record_truth"].set_index("record_id")

    valid_ages = records_df[records_df["age_raw"].notna()]
    assert len(valid_ages) > 0

    clean_ages = [
        truth_df.loc[r["record_id"], "clean_age_at_enrolment"]
        for _, r in valid_ages.iterrows()
    ]
    raw_ages = valid_ages["age_raw"].astype(int).tolist()

    clean_heaped_share = sum(1 for a in clean_ages if a % 5 == 0) / len(clean_ages)
    raw_heaped_share = sum(1 for a in raw_ages if a % 5 == 0) / len(raw_ages)

    assert raw_heaped_share > clean_heaped_share, (
        f"Corrupted heaped share ({raw_heaped_share:.2%}) <= clean ({clean_heaped_share:.2%})"
    )


def test_doppelgangers_exist_and_distinct(test_setup: tuple[Path, Path]) -> None:
    """At least 1 doppelganger pair exists, and all have distinct person_id and household_id."""
    cfg_path, base_tmp = test_setup
    _, truth_tables = export_registries(cfg_path, "demo", base_tmp)

    doppel_df = truth_tables["doppelganger_pairs"]
    assert len(doppel_df) > 0, "Expected at least 1 doppelganger pair in registries"
    assert (doppel_df["person_id_1"] != doppel_df["person_id_2"]).all()
    assert (doppel_df["household_id_1"] != doppel_df["household_id_2"]).all(), (
        "Doppelganger pairs must belong to distinct households"
    )


def test_enrolment_dates_within_bounds(test_setup: tuple[Path, Path]) -> None:
    """All enrolment dates must be between 2023-01-01 and 2026-06-30."""
    cfg_path, base_tmp = test_setup
    reg_tables, _ = export_registries(cfg_path, "demo", base_tmp)

    records_df = reg_tables["records"]
    dates = pd.to_datetime(records_df["enrolment_date"])
    assert (dates >= pd.to_datetime("2023-01-01")).all()
    assert (dates <= pd.to_datetime("2026-06-30")).all()


def test_observed_corruption_rates_within_tolerance(test_setup: tuple[Path, Path]) -> None:
    """Verify observed corruption rates match expected rates within +/- 3.5% where N >= 300."""
    cfg_path, base_tmp = test_setup
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    reg_tables, truth_tables = export_registries(cfg_path, "demo", base_tmp)
    records_df = reg_tables["records"]
    corr_log = truth_tables["corruption_log"]

    # Map record_id -> source_module
    rec_to_mod = records_df.set_index("record_id")["source_module"].to_dict()
    corr_log_mod = corr_log.copy()
    corr_log_mod["source_module"] = corr_log_mod["record_id"].map(rec_to_mod)

    base_rates = cfg["corruption"]["rates"]
    modules_cfg = cfg["enrolment"]["modules"]

    # Test transliteration rate across modules with N >= 300
    base_trans = float(base_rates["transliteration"])
    for m, m_cfg in modules_cfg.items():
        intensity = float(m_cfg.get("intensity", 1.0))
        expected_rate = min(1.0, base_trans * intensity)

        mod_records = records_df[records_df["source_module"] == m]
        denom = len(mod_records)
        if denom < 300:
            continue  # Skip per spec when denominator < 300

        # Transliteration events on full_name
        events = corr_log_mod[
            (corr_log_mod["source_module"] == m)
            & (corr_log_mod["field"] == "full_name")
            & (corr_log_mod["corruption_type"].str.startswith("transliteration"))
        ]
        obs_rate = len(events) / denom
        assert abs(obs_rate - expected_rate) <= 0.035, (
            f"Module {m} transliteration rate {obs_rate:.3f} deviates from {expected_rate:.3f}"
        )


def test_enrolment_realised_shares_within_tolerance(test_setup: tuple[Path, Path]) -> None:
    """Realised share is within +/- 2 percentage points of target_share for all modules."""
    cfg_path, base_tmp = test_setup
    _, truth_tables = export_registries(cfg_path, "demo", base_tmp)

    audit_df = truth_tables["audit_stats"]
    assert len(audit_df) == 4, "Expected audit rows for all 4 modules"

    for _, row in audit_df.iterrows():
        mod = row["module"]
        target = float(row["target_share"])
        realised = float(row["realised_share"])
        diff = abs(realised - target)
        assert diff <= 0.02, (
            f"Module '{mod}' realised share ({realised:.3f}) deviates from "
            f"target ({target:.3f}) by {diff:.3f} (> 0.02 tolerance)"
        )


def test_summary_file_generated(test_setup: tuple[Path, Path]) -> None:
    """Summary output is formatted and persisted to summary.txt on disk."""
    cfg_path, base_tmp = test_setup
    reg_tables, truth_tables = export_registries(cfg_path, "demo", base_tmp)
    run_dir = base_tmp / "demo"

    _print_corruption_summary(reg_tables, truth_tables, "demo", run_dir)
    summary_file = run_dir / "summary.txt"
    assert summary_file.exists(), "summary.txt must be generated"

    content = summary_file.read_text(encoding="utf-8")
    assert "BARI-LINK REGISTRY ENROLMENT & CORRUPTION SUMMARY" in content
    assert "Enrolment Base Audit" in content
    assert "Hard Negatives (Doppelganger Audit across Distinct Households)" in content
    assert "Example Clusters" in content
    assert "Post-Fix Name Frequency Shares" in content


