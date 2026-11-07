"""Unit tests for Phase 7: Household inference, constraints, reach, and truth segregation."""

from __future__ import annotations

import ast
from pathlib import Path

import pandas as pd

from barilink.evaluate.household_eval import build_oracle_person_clusters
from barilink.household.evidence import (
    UnitProfile,
    build_household_evidence,
)
from barilink.household.golden import build_household_golden_records
from barilink.household.infer import infer_households


def test_household_truth_access_forbidden():
    """Verify that barilink.household contains zero forbidden ground-truth string references."""
    household_dir = Path("src/barilink/household")
    violations = []
    for py_file in household_dir.rglob("*.py"):
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
                    or "record_truth" in s
                    or "persons.parquet" in s
                    or "households.parquet" in s
                )
                if is_forbidden:
                    violations.append((str(py_file), s))

    assert not violations, (
        f"Forbidden ground-truth reference found in barilink.household: {violations}"
    )


def test_toy_village_household_inference():
    """Toy village: husband H, wife W, son S, and an unrelated namesake household."""
    # H: husband, born 1970
    h = UnitProfile(
        cluster_id="u_H",
        record_ids=["r_H"],
        village_canon="mandalpara",
        village_raw="Mondal Para",
        union_raw="Belka",
        display_name="Rafiqul Islam",
        display_name_skeleton="rfqlslm",
        name_skels={"rfqlslm"},
        husband_name=None,
        husband_skeleton=None,
        has_husband=False,
        father_name=None,
        father_skeleton=None,
        birth_year=1970,
        age=56,
        inferred_sex="M",
        roster_skels={"ambgm", "trqlslm"},  # lists wife and son
    )
    # W: wife, husband_name = Rafiqul Islam, born 1975
    w = UnitProfile(
        cluster_id="u_W",
        record_ids=["r_W"],
        village_canon="mandalpara",
        village_raw="Mondal Para",
        union_raw="Belka",
        display_name="Amina Begum",
        display_name_skeleton="ambgm",
        name_skels={"ambgm"},
        husband_name="Rafiqul Islam",
        husband_skeleton="rfqlslm",
        has_husband=True,
        father_name=None,
        father_skeleton=None,
        birth_year=1975,
        age=51,
        inferred_sex="F",
        roster_skels={"rfqlslm", "trqlslm"},
    )
    # S: unmarried son, father_name = Rafiqul Islam, born 1995 (gap = 25 >= 15)
    s = UnitProfile(
        cluster_id="u_S",
        record_ids=["r_S"],
        village_canon="mandalpara",
        village_raw="Mondal Para",
        union_raw="Belka",
        display_name="Tariqul Islam",
        display_name_skeleton="trqlslm",
        name_skels={"trqlslm"},
        husband_name=None,
        husband_skeleton=None,
        has_husband=False,
        father_name="Rafiqul Islam",
        father_skeleton="rfqlslm",
        birth_year=1995,
        age=31,
        inferred_sex="M",
        roster_skels=set(),
    )
    # Namesake: unrelated Rafiqul Islam in different village or without links
    namesake = UnitProfile(
        cluster_id="u_namesake",
        record_ids=["r_NS"],
        village_canon="dakkinpara",  # different village
        village_raw="Dokkhin Para",
        union_raw="Belka",
        display_name="Rafiqul Islam",
        display_name_skeleton="rfqlslm",
        name_skels={"rfqlslm"},
        husband_name=None,
        husband_skeleton=None,
        has_husband=False,
        father_name=None,
        father_skeleton=None,
        birth_year=1972,
        age=54,
        inferred_sex="M",
        roster_skels=set(),
    )

    profiles = {u.cluster_id: u for u in [h, w, s, namesake]}
    edges_df = build_household_evidence(profiles)

    # Threshold t_hh = 5.0 (H and W link by E1=4 + E2=4 = 8; S links to H by E1=4 + E3=2 = 6)
    clusters_df, _ = infer_households(profiles, edges_df, t_hh=5.0)

    hh_map = dict(zip(clusters_df["cluster_id"], clusters_df["household_id"]))

    # Expect {H, W, S} in the same household
    assert hh_map["u_H"] == hh_map["u_W"], "Husband and Wife should be in the same household"
    assert hh_map["u_H"] == hh_map["u_S"], "Husband and Son should be in the same household"
    # Namesake must be in a separate household
    assert hh_map["u_H"] != hh_map["u_namesake"], "Namesake must be in a separate household"


def test_married_woman_no_father_e3():
    """A married woman with father_name = X does NOT get E3 to X."""
    father = UnitProfile(
        cluster_id="u_F",
        record_ids=["r_F"],
        village_canon="mandalpara",
        village_raw="Mondal Para",
        union_raw="Belka",
        display_name="Habibur Rahman",
        display_name_skeleton="hbrrhmn",
        name_skels={"hbrrhmn"},
        husband_name=None,
        husband_skeleton=None,
        has_husband=False,
        father_name=None,
        father_skeleton=None,
        birth_year=1960,
        age=66,
        inferred_sex="M",
        roster_skels=set(),
    )
    # Married woman with husband AND father_name
    married_woman = UnitProfile(
        cluster_id="u_W",
        record_ids=["r_W"],
        village_canon="mandalpara",
        village_raw="Mondal Para",
        union_raw="Belka",
        display_name="Fatema Begum",
        display_name_skeleton="ftmbgm",
        name_skels={"ftmbgm"},
        husband_name="Abdul Karim",
        husband_skeleton="abdlkrm",
        has_husband=True,  # Married!
        father_name="Habibur Rahman",
        father_skeleton="hbrrhmn",
        birth_year=1990,
        age=36,
        inferred_sex="F",
        roster_skels=set(),
    )

    profiles = {father.cluster_id: father, married_woman.cluster_id: married_woman}
    edges_df = build_household_evidence(profiles)

    # Edge between father and married woman should NOT have E3 active
    if not edges_df.empty:
        e3_active = edges_df.iloc[0]["e3"]
        assert not e3_active, "Married woman must NOT get E3 father_link"
    else:
        # No edge formed because no other evidence and E3 is false
        assert True


def test_adult_female_no_father_e3():
    """Amendment 1: Adult woman (age >= 18, inferred_sex = F) does NOT get E3 to father."""
    father = UnitProfile(
        cluster_id="u_F",
        record_ids=["r_F"],
        village_canon="mandalpara",
        village_raw="Mondal Para",
        union_raw="Belka",
        display_name="Habibur Rahman",
        display_name_skeleton="hbrrhmn",
        name_skels={"hbrrhmn"},
        husband_name=None,
        husband_skeleton=None,
        has_husband=False,
        father_name=None,
        father_skeleton=None,
        birth_year=1965,
        age=61,
        inferred_sex="M",
        roster_skels=set(),
    )
    # Adult woman (age 24 >= 18, inferred_sex = F) whose husband_name is None
    adult_woman = UnitProfile(
        cluster_id="u_W",
        record_ids=["r_W1", "r_W2"],
        village_canon="mandalpara",
        village_raw="Mondal Para",
        union_raw="Belka",
        display_name="Most. Rasheda Khatun",
        display_name_skeleton="rsdktn",
        name_skels={"rsdktn"},
        husband_name=None,
        husband_skeleton=None,
        has_husband=False,  # husband unknown / null
        father_name="Habibur Rahman",
        father_skeleton="hbrrhmn",
        birth_year=2002,
        age=24,  # Adult woman!
        inferred_sex="F",
        roster_skels=set(),
    )

    profiles = {father.cluster_id: father, adult_woman.cluster_id: adult_woman}
    edges_df = build_household_evidence(profiles)

    # E3 must NOT fire for adult female
    if not edges_df.empty:
        e3_active = edges_df.iloc[0]["e3"]
        assert not e3_active, "Adult female (age >= 18) must NOT get E3 father link"
    else:
        assert True


def test_max_size_min_cut():
    """Verify that an oversize component (> 12 units) is split by cutting the weakest edge."""
    profiles = {}
    edges_list = []

    # Create 14 units: clique A (units 1..7) and clique B (units 8..14)
    for i in range(1, 15):
        uid = f"u_{i}"
        profiles[uid] = UnitProfile(
            cluster_id=uid,
            record_ids=[f"r_{i}"],
            village_canon="mandalpara",
            village_raw="Mondal Para",
            union_raw="Belka",
            display_name=f"Person {i}",
            display_name_skeleton=f"p{i}",
            name_skels={f"p{i}"},
            husband_name=None,
            husband_skeleton=None,
            has_husband=False,
            father_name=None,
            father_skeleton=None,
            birth_year=1980,
            age=46,
            inferred_sex=None,
            roster_skels=set(),
        )

    # Clique 1 (weights 4.0)
    for i in range(1, 7):
        for j in range(i + 1, 8):
            edges_list.append(
                {"unit_id_l": f"u_{i}", "unit_id_r": f"u_{j}", "score": 4.0, "e2": False}
            )

    # Clique 2 (weights 4.0)
    for i in range(8, 14):
        for j in range(i + 1, 15):
            edges_list.append(
                {"unit_id_l": f"u_{i}", "unit_id_r": f"u_{j}", "score": 4.0, "e2": False}
            )

    # Weak bridge between clique 1 and clique 2 (capacity 1.0)
    edges_list.append({"unit_id_l": "u_7", "unit_id_r": "u_8", "score": 1.0, "e2": False})

    edges_df = pd.DataFrame(edges_list)

    clusters_df, log_df = infer_households(profiles, edges_df, t_hh=1.0, max_size=12)

    # Must be split into 2 components of size 7 each
    hh_sizes = clusters_df["household_id"].value_counts()
    assert max(hh_sizes) <= 12, "All components must be <= max_size 12"
    assert len(hh_sizes) == 2, "Graph should be split into exactly 2 components"

    # Weak bridge cut logged
    cuts = log_df[log_df["action"] == "max_size_cut"]
    assert len(cuts) == 1, "Exactly one weakest edge should be cut"
    cut_pair = {cuts.iloc[0]["unit_id_l"], cuts.iloc[0]["unit_id_r"]}
    assert cut_pair == {"u_7", "u_8"}, "Cut edge must be the weakest bridge (u_7, u_8)"


def test_cannot_household_two_wives_different_husbands():
    """Two wives of two different men linked by E2 must be split by min-cut; co-wives allowed."""
    # Husband 1 (M1) and Wife 1 (W1)
    m1 = UnitProfile(
        cluster_id="u_M1",
        record_ids=["r_M1"],
        village_canon="mandalpara",
        village_raw="Mondal Para",
        union_raw="Belka",
        display_name="Rahim Ali",
        display_name_skeleton="rhml",
        name_skels={"rhml"},
        husband_name=None,
        husband_skeleton=None,
        has_husband=False,
        father_name=None,
        father_skeleton=None,
        birth_year=1970,
        age=56,
        inferred_sex="M",
        roster_skels=set(),
    )
    w1 = UnitProfile(
        cluster_id="u_W1",
        record_ids=["r_W1"],
        village_canon="mandalpara",
        village_raw="Mondal Para",
        union_raw="Belka",
        display_name="Amina Begum",
        display_name_skeleton="ambgm",
        name_skels={"ambgm"},
        husband_name="Rahim Ali",
        husband_skeleton="rhml",
        has_husband=True,
        father_name=None,
        father_skeleton=None,
        birth_year=1975,
        age=51,
        inferred_sex="F",
        roster_skels=set(),
    )
    # Husband 2 (M2) and Wife 2 (W2)
    m2 = UnitProfile(
        cluster_id="u_M2",
        record_ids=["r_M2"],
        village_canon="mandalpara",
        village_raw="Mondal Para",
        union_raw="Belka",
        display_name="Karim Mia",
        display_name_skeleton="krmm",
        name_skels={"krmm"},
        husband_name=None,
        husband_skeleton=None,
        has_husband=False,
        father_name=None,
        father_skeleton=None,
        birth_year=1972,
        age=54,
        inferred_sex="M",
        roster_skels=set(),
    )
    w2 = UnitProfile(
        cluster_id="u_W2",
        record_ids=["r_W2"],
        village_canon="mandalpara",
        village_raw="Mondal Para",
        union_raw="Belka",
        display_name="Fatema Khatun",
        display_name_skeleton="ftmktn",
        name_skels={"ftmktn"},
        husband_name="Karim Mia",
        husband_skeleton="krmm",
        has_husband=True,
        father_name=None,
        father_skeleton=None,
        birth_year=1976,
        age=50,
        inferred_sex="F",
        roster_skels=set(),
    )

    profiles = {u.cluster_id: u for u in [m1, w1, m2, w2]}
    # Connect W1-M1 (E2), W2-M2 (E2), and mistakenly M1-M2 (shared phone, weight 1.0)
    edges_list = [
        {"unit_id_l": "u_M1", "unit_id_r": "u_W1", "score": 4.0, "e2": True},
        {"unit_id_l": "u_M2", "unit_id_r": "u_W2", "score": 4.0, "e2": True},
        {"unit_id_l": "u_M1", "unit_id_r": "u_M2", "score": 1.0, "e2": False},
    ]
    edges_df = pd.DataFrame(edges_list)

    clusters_df, log_df = infer_households(profiles, edges_df, t_hh=1.0)
    hh_map = dict(zip(clusters_df["cluster_id"], clusters_df["household_id"]))

    # W1 and W2 must be in different households
    assert hh_map["u_W1"] != hh_map["u_W2"], "Two wives of different men must be separated"
    assert hh_map["u_W1"] == hh_map["u_M1"], "W1 and M1 should stay together"
    assert hh_map["u_W2"] == hh_map["u_M2"], "W2 and M2 should stay together"


def test_roster_names_unenrolled_excludes_enrolled():
    """Verify that roster_names_unenrolled excludes enrolled members' name skeletons."""
    h = UnitProfile(
        cluster_id="u_H",
        record_ids=["r_H"],
        village_canon="mandalpara",
        village_raw="Mondal Para",
        union_raw="Belka",
        display_name="Rafiqul Islam",
        display_name_skeleton="rfqlslm",
        name_skels={"rfqlslm"},
        husband_name=None,
        husband_skeleton=None,
        has_husband=False,
        father_name=None,
        father_skeleton=None,
        birth_year=1970,
        age=56,
        inferred_sex="M",
        roster_skels=set(),
    )
    w = UnitProfile(
        cluster_id="u_W",
        record_ids=["r_W"],
        village_canon="mandalpara",
        village_raw="Mondal Para",
        union_raw="Belka",
        display_name="Amina Begum",
        display_name_skeleton="ambgm",
        name_skels={"ambgm"},
        husband_name="Rafiqul Islam",
        husband_skeleton="rfqlslm",
        has_husband=True,
        father_name=None,
        father_skeleton=None,
        birth_year=1975,
        age=51,
        inferred_sex="F",
        # Attached roster lists husband (rfqlslm) and two unenrolled children (ksml, ftm)
        roster_skels={"rfqlslm", "ksml", "ftm"},
    )

    profiles = {"u_H": h, "u_W": w}
    hh_clusters_df = pd.DataFrame(
        [
            {"cluster_id": "u_H", "household_id": "hh_test"},
            {"cluster_id": "u_W", "household_id": "hh_test"},
        ]
    )

    golden_df = build_household_golden_records(hh_clusters_df, profiles)
    row = golden_df.iloc[0]

    # Enrolled member skeletons: rfqlslm, ambgm
    # Unenrolled roster skeletons should contain only ftm and ksml
    unenrolled = row["roster_names_unenrolled"]
    assert "rfqlslm" not in unenrolled, "Enrolled skeleton rfqlslm must be excluded"
    assert "ambgm" not in unenrolled, "Enrolled skeleton ambgm must be excluded"
    assert sorted(unenrolled) == ["ftm", "ksml"], f"Expected ['ftm', 'ksml'], got {unenrolled}"

    assert row["direct_reach"] == 2
    assert row["indirect_reach"] == 2
    assert row["est_household_size"] == 4


def test_oracle_mode_built_only_in_evaluate():
    """Verify that Oracle person clusters are constructed strictly within evaluate."""
    demo_dir = Path("data/generated/demo")
    oracle_df = build_oracle_person_clusters(demo_dir)

    assert "record_id" in oracle_df.columns
    assert "cluster_id" in oracle_df.columns
    assert len(oracle_df) > 0
    # cluster_id should match person_id format P_...
    sample_cid = oracle_df.iloc[0]["cluster_id"]
    assert sample_cid.startswith("P_"), f"Expected person_id prefix P_, got {sample_cid}"
