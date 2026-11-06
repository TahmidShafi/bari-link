"""Unit tests for clean ground-truth population generation."""

import json
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from barilink.generate.population import generate_population


@pytest.fixture
def small_config(tmp_path: Path) -> Path:
    """Create a small configuration file with n_households=200 for fast testing."""
    config_dict: dict[str, Any] = {
        "seed": 42,
        "reference_date": "2026-01-01",
        "n_households": 200,
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
    }
    cfg_file = tmp_path / "test_config.yaml"
    with open(cfg_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(config_dict, f)
    return cfg_file


def test_reproducibility_identical_seed(small_config: Path, tmp_path: Path) -> None:
    """Same seed gives byte-identical persons.parquet."""
    out_dir_1 = tmp_path / "run_1"
    out_dir_2 = tmp_path / "run_2"

    generate_population(small_config, out_dir_1)
    generate_population(small_config, out_dir_2)

    bytes_1 = (out_dir_1 / "persons.parquet").read_bytes()
    bytes_2 = (out_dir_2 / "persons.parquet").read_bytes()
    assert bytes_1 == bytes_2, "Outputs for identical seed must be byte-identical."


def test_divergence_different_seeds(small_config: Path, tmp_path: Path) -> None:
    """Different seed gives different output."""
    with open(small_config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    cfg_other = dict(cfg)
    cfg_other["seed"] = 999
    other_config_file = tmp_path / "other_config.yaml"
    with open(other_config_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg_other, f)

    out_dir_1 = tmp_path / "seed_42"
    out_dir_2 = tmp_path / "seed_999"

    generate_population(small_config, out_dir_1)
    generate_population(other_config_file, out_dir_2)

    bytes_1 = (out_dir_1 / "persons.parquet").read_bytes()
    bytes_2 = (out_dir_2 / "persons.parquet").read_bytes()
    assert bytes_1 != bytes_2, "Outputs for different seeds must diverge."


def test_uniqueness_and_non_null_ids(small_config: Path, tmp_path: Path) -> None:
    """person_id and household_id are unique and non-null."""
    out_dir = tmp_path / "uniqueness"
    persons_df, households_df, _ = generate_population(small_config, out_dir)

    # Household IDs
    assert households_df["household_id"].notna().all()
    assert households_df["household_id"].is_unique
    assert len(households_df) == 200

    # Person IDs
    assert persons_df["person_id"].notna().all()
    assert persons_df["person_id"].is_unique
    assert len(persons_df) > 200


def test_referential_integrity(small_config: Path, tmp_path: Path) -> None:
    """Every father_id, mother_id, and spouse_id that is not null refers to an existing person."""
    out_dir = tmp_path / "ref_integrity"
    persons_df, households_df, _ = generate_population(small_config, out_dir)

    all_person_ids = set(persons_df["person_id"])
    all_hh_ids = set(households_df["household_id"])

    # Household references
    assert set(persons_df["household_id"]).issubset(all_hh_ids)
    assert set(households_df["head_person_id"]).issubset(all_person_ids)

    # Father ID integrity
    valid_father_ids = persons_df["father_id"].dropna()
    assert valid_father_ids.isin(all_person_ids).all(), "Every non-null father_id must exist."

    # Mother ID integrity
    valid_mother_ids = persons_df["mother_id"].dropna()
    assert valid_mother_ids.isin(all_person_ids).all(), "Every non-null mother_id must exist."

    # Spouse ID integrity
    valid_spouse_ids = persons_df["spouse_id"].dropna()
    assert valid_spouse_ids.isin(all_person_ids).all(), "Every non-null spouse_id must exist."


def test_parent_child_age_constraint(small_config: Path, tmp_path: Path) -> None:
    """Children are at least 15 years younger than their father."""
    out_dir = tmp_path / "age_constraint"
    persons_df, _, _ = generate_population(small_config, out_dir)

    person_by_id = persons_df.set_index("person_id")

    children_with_father = persons_df[persons_df["father_id"].notna()]
    assert len(children_with_father) > 0

    for _, child in children_with_father.iterrows():
        father = person_by_id.loc[child["father_id"]]
        age_gap = father["age_at_reference_date"] - child["age_at_reference_date"]
        assert age_gap >= 15, (
            f"Child {child['person_id']} (age {child['age_at_reference_date']}) "
            f"must be >= 15 years younger than father {father.name} "
            f"(age {father['age_at_reference_date']})"
        )


def test_under_15_never_married(small_config: Path, tmp_path: Path) -> None:
    """Nobody under 15 is married or has a spouse_id."""
    out_dir = tmp_path / "under_15"
    persons_df, _, _ = generate_population(small_config, out_dir)

    under_15 = persons_df[persons_df["age_at_reference_date"] < 15]
    assert len(under_15) > 0

    assert (under_15["marital_status"] == "unmarried").all()
    assert under_15["spouse_id"].isna().all()


def test_resident_father_name_consistency(small_config: Path, tmp_path: Path) -> None:
    """resident father -> child.father_name == father's full name."""
    out_dir = tmp_path / "father_name_consistency"
    persons_df, _, _ = generate_population(small_config, out_dir)

    person_by_id = persons_df.set_index("person_id")
    children_with_father = persons_df[persons_df["father_id"].notna()]
    assert len(children_with_father) > 0

    for _, child in children_with_father.iterrows():
        father = person_by_id.loc[child["father_id"]]
        expected_father_name = f"{father['given_name']} {father['surname_or_title']}"
        assert child["father_name"] == expected_father_name


def test_sibling_father_name_consistency(small_config: Path, tmp_path: Path) -> None:
    """Siblings with the same mother_id (or the same female head) have identical father_name."""
    out_dir = tmp_path / "sibling_consistency"
    persons_df, _, _ = generate_population(small_config, out_dir)

    # Group by household_id and mother_id where mother_id is not null
    children_with_mother = persons_df[persons_df["mother_id"].notna()]
    grouped = children_with_mother.groupby(["household_id", "mother_id"])

    for (hh_id, mother_id), group in grouped:
        if len(group) > 1:
            distinct_father_names = group["father_name"].unique()
            assert len(distinct_father_names) == 1, (
                f"Siblings in HH {hh_id} with mother {mother_id} have conflicting father names: "
                f"{distinct_father_names}"
            )


def test_ever_married_women_guardian_rule(small_config: Path, tmp_path: Path) -> None:
    """Every ever-married woman has a non-null spouse_name and guardian_type == 'husband'."""
    out_dir = tmp_path / "ever_married_women"
    persons_df, _, _ = generate_population(small_config, out_dir)

    ever_married_statuses = ["married", "widowed", "separated"]
    ever_married_women = persons_df[
        (persons_df["sex"] == "F") & (persons_df["marital_status"].isin(ever_married_statuses))
    ]
    assert len(ever_married_women) > 0

    assert ever_married_women["spouse_name"].notna().all()
    assert (ever_married_women["guardian_type"] == "husband").all()
    assert (ever_married_women["guardian_name"] == ever_married_women["spouse_name"]).all()
    # Also verify father_name is populated
    assert ever_married_women["father_name"].notna().all()


def test_zipf_mandelbrot_distribution_skew(small_config: Path, tmp_path: Path) -> None:
    """Top 10 female given names > 30% of women, and top 1 female name < 12% of women."""
    out_dir = tmp_path / "zipf_skew"
    persons_df, _, _ = generate_population(small_config, out_dir)

    females = persons_df[persons_df["sex"] == "F"]
    n_females = len(females)
    assert n_females > 0

    counts = females["given_name"].value_counts()
    top_1_share = counts.iloc[0] / n_females
    top_10_share = counts.head(10).sum() / n_females

    assert top_10_share > 0.30, f"Top 10 female names share ({top_10_share:.2%}) should be > 30%"
    assert top_1_share < 0.12, f"Top 1 female name share ({top_1_share:.2%}) should be < 12%"


def test_phone_format_regex(small_config: Path, tmp_path: Path) -> None:
    """All non-null phones match the regex ^01[3-9]\\d{8}$."""
    out_dir = tmp_path / "phones"
    persons_df, households_df, _ = generate_population(small_config, out_dir)

    pattern = re.compile(r"^01[3-9]\d{8}$")

    # Personal phones
    personal_phones = persons_df["phone"].dropna()
    assert len(personal_phones) > 0
    for phone in personal_phones:
        assert pattern.match(phone), f"Personal phone {phone} does not match expected format."

    # Household phones
    hh_phones = households_df["household_phone"].dropna()
    assert len(hh_phones) > 0
    for phone in hh_phones:
        assert pattern.match(phone), f"Household phone {phone} does not match expected format."


def test_manifest_structure(small_config: Path, tmp_path: Path) -> None:
    """Manifest JSON is written with valid metadata and matching counts."""
    out_dir = tmp_path / "manifest"
    persons_df, households_df, manifest = generate_population(small_config, out_dir)

    manifest_file = out_dir / "manifest.json"
    assert manifest_file.exists()

    with open(manifest_file, "r", encoding="utf-8") as f:
        disk_manifest = json.load(f)

    assert disk_manifest["seed"] == 42
    assert disk_manifest["package_version"] == "0.1.0"
    assert disk_manifest["row_counts"]["persons"] == len(persons_df)
    assert disk_manifest["row_counts"]["households"] == len(households_df)
    assert "timestamp_utc" in disk_manifest


def test_head_elderly_father_linkage(small_config: Path, tmp_path: Path) -> None:
    """If HH contains resident elderly father, head.father_id == elderly father person_id."""
    out_dir = tmp_path / "elderly_father_linkage"
    persons_df, households_df, _ = generate_population(small_config, out_dir)

    # Find households with a male parent
    is_parent = persons_df["role_in_household"] == "parent"
    is_male = persons_df["sex"] == "M"
    elderly_fathers = persons_df[is_parent & is_male]
    assert len(elderly_fathers) > 0, "Expected at least 1 HH with an elderly father in 200 HHs."

    person_by_id = persons_df.set_index("person_id")
    for _, ef in elderly_fathers.iterrows():
        hh_id = ef["household_id"]
        hh_record = households_df[households_df["household_id"] == hh_id].iloc[0]
        head_id = hh_record["head_person_id"]
        head = person_by_id.loc[head_id]

        assert head["father_id"] == ef["person_id"], (
            f"Head {head_id} father_id ({head['father_id']}) must equal "
            f"resident elderly father {ef['person_id']}"
        )
        expected_name = f"{ef['given_name']} {ef['surname_or_title']}"
        assert head["father_name"] == expected_name, (
            f"Head {head_id} father_name ({head['father_name']}) must equal {expected_name}"
        )

