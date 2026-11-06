"""Registry orchestration and strict data segregation for bari-link.

Applies field corruptions to enrolled candidates, assigns collision-free
opaque record_ids, permutes row orders, and partitions outputs into:
- data/generated/<run>/registry/ (model-visible ONLY)
- data/generated/<run>/truth/    (evaluation ONLY)
"""

import json
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd
import yaml

from barilink.corrupt.corruption import FieldCorruptor
from barilink.corrupt.sampler import EnrolmentSampler

FORBIDDEN_REGISTRY_COLUMNS: set[str] = {
    "person_id",
    "household_id",
    "given_name",
    "surname_or_title",
    "father_id",
    "father_given_name",
    "clean_full_name",
    "clean_given_name",
    "clean_surname_or_title",
    "clean_sex",
    "clean_marital_status",
}


class RegistryOrchestrator:
    """Orchestrates sampling, corrupting, and exporting administrative registries."""

    def __init__(self, config: dict[str, Any], seed: Optional[int] = None) -> None:
        self.config = config
        self.seed = seed if seed is not None else int(config.get("seed", 42))
        self.rng = np.random.default_rng(self.seed)
        self.corruptor = FieldCorruptor(config, self.rng)
        self.seen_record_ids: set[str] = set()

    def _next_record_id(self) -> str:
        """Generate a random, non-sequential 10-char hex record_id with collision redraw."""
        while True:
            token = self.rng.bytes(5).hex()
            if token not in self.seen_record_ids:
                self.seen_record_ids.add(token)
                return token

    def process(
        self, persons_df: pd.DataFrame, households_df: pd.DataFrame
    ) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
        """Run the end-to-end enrolment and corruption process."""
        # 1. Enrolment sampling
        sampler = EnrolmentSampler(self.config, persons_df, households_df, self.rng)
        candidates = sampler.sample_all_modules()
        # Shuffle candidates so record_id assignment is completely independent of candidate order
        self.rng.shuffle(candidates)

        # 2. Corrupt candidates and populate tables
        records_rows: list[dict[str, Any]] = []
        truth_rows: list[dict[str, Any]] = []
        rosters_rows: list[dict[str, Any]] = []

        modules_cfg = self.config.get("enrolment", {}).get("modules", {})

        for cand in candidates:
            rec_id = self._next_record_id()
            mod_name = cand.source_module
            mod_intensity = float(modules_cfg.get(mod_name, {}).get("intensity", 1.0))

            # --- Name Corruption ---
            # Start with full name
            curr_name = cand.clean_full_name
            # Title to front
            curr_name = self.corruptor.corrupt_title_to_front(
                curr_name, rec_id, "full_name", mod_intensity
            )
            # Prefix drift
            curr_name = self.corruptor.corrupt_prefix(
                curr_name, cand.clean_sex, rec_id, "full_name", mod_intensity
            )
            # Female title drift
            curr_name = self.corruptor.corrupt_female_title(
                curr_name, cand.clean_sex, rec_id, "full_name", mod_intensity
            )
            # Transliteration drift
            curr_name = self.corruptor.corrupt_transliteration(
                curr_name, rec_id, "full_name", mod_intensity
            )
            # Typo drift
            curr_name = self.corruptor.corrupt_typos(
                curr_name, rec_id, "full_name", mod_intensity
            )

            # --- Guardian Corruption ---
            g_name, g_type = self.corruptor.corrupt_guardian(
                guardian_name=cand.clean_guardian_name,
                guardian_type=cand.clean_guardian_type,
                father_name=cand.clean_father_name,
                marital_status=cand.clean_marital_status,
                sex=cand.clean_sex,
                record_id=rec_id,
                intensity=mod_intensity,
            )
            # Prefix drift on guardian
            g_name = self.corruptor.corrupt_prefix(
                g_name, "M", rec_id, "guardian_name", mod_intensity
            )
            # Transliteration on guardian
            g_name = self.corruptor.corrupt_transliteration(
                g_name, rec_id, "guardian_name", mod_intensity
            )
            # Typo on guardian
            g_name = self.corruptor.corrupt_typos(
                g_name, rec_id, "guardian_name", mod_intensity
            )

            # Possible field swap (given name <-> guardian name)
            swap_rate = self.corruptor._effective_rate(
                "field_swap_guardian", mod_intensity
            )
            if self.rng.random() < swap_rate:
                self.corruptor.log_event(
                    rec_id, "guardian_name", "field_swap_guardian", g_name, curr_name
                )
                curr_name, g_name = g_name, curr_name

            # --- Age Corruption ---
            corrupt_age = self.corruptor.corrupt_age(
                cand.clean_age_at_enrolment, rec_id, mod_intensity
            )

            # --- Phone Corruption ---
            corrupt_phone = self.corruptor.corrupt_phone(
                cand.clean_phone,
                cand.clean_household_phone,
                rec_id,
                mod_intensity,
            )

            # --- Location Corruption ---
            c_village, c_union, c_upazila, c_district = (
                self.corruptor.corrupt_location(
                    cand.clean_village,
                    cand.clean_union,
                    cand.clean_upazila,
                    cand.clean_district,
                    rec_id,
                    mod_intensity,
                )
            )

            # --- Module-Specific Schema Construction & Missingness ---
            # 1. club_formation: collects member_name, age, guardian, village
            # 2. upg_enrolment: collects participant_name, age, guardian_name,
            #    guardian_type, phone, full location
            # 3. microfinance_group: collects borrower_name, husband_or_father,
            #    phone, village, union, group_id
            # 4. livelihood_support: collects recipient_name, age, father_name,
            #    phone, full location

            final_full_name: Optional[str] = curr_name
            final_guardian_name: Optional[str] = g_name
            final_guardian_type: Optional[str] = g_type
            final_age: Optional[int] = corrupt_age
            final_sex: Optional[str] = cand.clean_sex
            final_phone: Optional[str] = corrupt_phone
            final_village: Optional[str] = c_village
            final_union: Optional[str] = c_union
            final_upazila: Optional[str] = c_upazila
            final_district: Optional[str] = c_district
            final_group_id: Optional[str] = cand.group_id

            # Apply structural nulls and configured missingness
            if mod_name == "club_formation":
                final_guardian_type = None
                final_phone = None
                final_union = None
                final_upazila = None
                final_district = None
                final_group_id = None
                # Apply missingness
                final_guardian_name = self.corruptor.apply_missingness(
                    mod_name, "guardian_name", final_guardian_name, rec_id
                )
                final_age = self.corruptor.apply_missingness(
                    mod_name, "age", final_age, rec_id
                )
                final_village = self.corruptor.apply_missingness(
                    mod_name, "village", final_village, rec_id
                )

            elif mod_name == "upg_enrolment":
                final_group_id = None
                final_guardian_name = self.corruptor.apply_missingness(
                    mod_name, "guardian_name", final_guardian_name, rec_id
                )
                final_age = self.corruptor.apply_missingness(
                    mod_name, "age", final_age, rec_id
                )
                final_phone = self.corruptor.apply_missingness(
                    mod_name, "phone", final_phone, rec_id
                )
                final_village = self.corruptor.apply_missingness(
                    mod_name, "village", final_village, rec_id
                )
                final_union = self.corruptor.apply_missingness(
                    mod_name, "union", final_union, rec_id
                )
                final_upazila = self.corruptor.apply_missingness(
                    mod_name, "upazila", final_upazila, rec_id
                )
                final_district = self.corruptor.apply_missingness(
                    mod_name, "district", final_district, rec_id
                )

            elif mod_name == "microfinance_group":
                final_age = None
                final_guardian_type = None
                final_upazila = None
                final_district = None
                final_guardian_name = self.corruptor.apply_missingness(
                    mod_name, "guardian_name", final_guardian_name, rec_id
                )
                final_phone = self.corruptor.apply_missingness(
                    mod_name, "phone", final_phone, rec_id
                )
                final_village = self.corruptor.apply_missingness(
                    mod_name, "village", final_village, rec_id
                )
                final_union = self.corruptor.apply_missingness(
                    mod_name, "union", final_union, rec_id
                )

            elif mod_name == "livelihood_support":
                final_group_id = None
                final_guardian_type = "father"
                final_guardian_name = self.corruptor.apply_missingness(
                    mod_name, "guardian_name", final_guardian_name, rec_id
                )
                final_age = self.corruptor.apply_missingness(
                    mod_name, "age", final_age, rec_id
                )
                final_phone = self.corruptor.apply_missingness(
                    mod_name, "phone", final_phone, rec_id
                )
                final_village = self.corruptor.apply_missingness(
                    mod_name, "village", final_village, rec_id
                )
                final_union = self.corruptor.apply_missingness(
                    mod_name, "union", final_union, rec_id
                )
                final_upazila = self.corruptor.apply_missingness(
                    mod_name, "upazila", final_upazila, rec_id
                )
                final_district = self.corruptor.apply_missingness(
                    mod_name, "district", final_district, rec_id
                )

            # Build harmonised records row
            records_rows.append(
                {
                    "record_id": rec_id,
                    "source_module": mod_name,
                    "enrolment_date": cand.enrolment_date.isoformat(),
                    "full_name_raw": final_full_name,
                    "guardian_name_raw": final_guardian_name,
                    "guardian_type_raw": final_guardian_type,
                    "age_raw": final_age,
                    "sex_raw": final_sex,
                    "phone_raw": final_phone,
                    "village_raw": final_village,
                    "union_raw": final_union,
                    "upazila_raw": final_upazila,
                    "district_raw": final_district,
                    "group_id": final_group_id,
                }
            )

            # Build roster rows if present
            roster_pids: list[str] = []
            if cand.roster_members:
                for rm in cand.roster_members:
                    roster_pids.append(rm.member_person_id)
                    # Corrupt roster member name and age
                    r_name = rm.member_name_raw
                    r_name = self.corruptor.corrupt_transliteration(
                        r_name, rec_id, "roster_member_name", mod_intensity
                    )
                    r_name = self.corruptor.corrupt_typos(
                        r_name, rec_id, "roster_member_name", mod_intensity
                    )
                    r_age = self.corruptor.corrupt_age(
                        rm.age_raw, rec_id, mod_intensity
                    )
                    rosters_rows.append(
                        {
                            "record_id": rec_id,
                            "member_name_raw": r_name,
                            "relation_raw": rm.relation_raw,
                            "age_raw": r_age,
                        }
                    )

            # Build truth evaluation row
            truth_rows.append(
                {
                    "record_id": rec_id,
                    "person_id": cand.person_id,
                    "household_id": cand.household_id,
                    "source_module": mod_name,
                    "enrolment_date": cand.enrolment_date.isoformat(),
                    "is_re_registration": cand.is_re_registration,
                    "is_doppelganger": cand.is_doppelganger,
                    "is_injected": cand.is_injected,
                    "clean_full_name": cand.clean_full_name,
                    "clean_given_name": cand.clean_given_name,
                    "clean_surname_or_title": cand.clean_surname_or_title,
                    "clean_sex": cand.clean_sex,
                    "clean_marital_status": cand.clean_marital_status,
                    "clean_guardian_name": cand.clean_guardian_name,
                    "clean_guardian_type": cand.clean_guardian_type,
                    "clean_age_at_enrolment": cand.clean_age_at_enrolment,
                    "clean_phone": cand.clean_phone,
                    "clean_village": cand.clean_village,
                    "clean_union": cand.clean_union,
                    "clean_upazila": cand.clean_upazila,
                    "clean_district": cand.clean_district,
                    "roster_person_ids": json.dumps(roster_pids),
                }
            )

        # Convert to DataFrames and shuffle rows
        records_df = pd.DataFrame(records_rows)
        truth_df = pd.DataFrame(truth_rows)
        rosters_df = pd.DataFrame(rosters_rows) if rosters_rows else pd.DataFrame(
            columns=["record_id", "member_name_raw", "relation_raw", "age_raw"]
        )

        # Shuffle all tables using seeded permutation
        rand_seed = int(self.rng.integers(1, 1000000))
        records_df = records_df.sample(frac=1.0, random_state=rand_seed).reset_index(drop=True)
        # Note: truth_df does not need to be in matching order to records_df
        truth_df = truth_df.sample(frac=1.0, random_state=rand_seed).reset_index(drop=True)
        if not rosters_df.empty:
            rosters_df = rosters_df.sample(frac=1.0, random_state=rand_seed).reset_index(drop=True)

        # Build raw module CSVs
        club_df = records_df[records_df["source_module"] == "club_formation"][
            ["full_name_raw", "age_raw", "guardian_name_raw", "village_raw"]
        ].rename(
            columns={
                "full_name_raw": "member_name",
                "age_raw": "age",
                "guardian_name_raw": "guardian",
                "village_raw": "village",
            }
        )

        upg_df = records_df[records_df["source_module"] == "upg_enrolment"][
            [
                "full_name_raw",
                "age_raw",
                "guardian_name_raw",
                "guardian_type_raw",
                "phone_raw",
                "village_raw",
                "union_raw",
                "upazila_raw",
                "district_raw",
            ]
        ].rename(
            columns={
                "full_name_raw": "participant_name",
                "age_raw": "age",
                "guardian_name_raw": "guardian_name",
                "guardian_type_raw": "guardian_type",
                "phone_raw": "phone",
                "village_raw": "village",
                "union_raw": "union",
                "upazila_raw": "upazila",
                "district_raw": "district",
            }
        )

        mfg_df = records_df[records_df["source_module"] == "microfinance_group"][
            [
                "full_name_raw",
                "guardian_name_raw",
                "phone_raw",
                "village_raw",
                "union_raw",
                "group_id",
            ]
        ].rename(
            columns={
                "full_name_raw": "borrower_name",
                "guardian_name_raw": "husband_or_father",
                "phone_raw": "phone",
                "village_raw": "village",
                "union_raw": "union",
            }
        )

        livelihood_df = records_df[records_df["source_module"] == "livelihood_support"][
            [
                "full_name_raw",
                "age_raw",
                "guardian_name_raw",
                "phone_raw",
                "village_raw",
                "union_raw",
                "upazila_raw",
                "district_raw",
            ]
        ].rename(
            columns={
                "full_name_raw": "recipient_name",
                "age_raw": "age",
                "guardian_name_raw": "father_name",
                "phone_raw": "phone",
                "village_raw": "village",
                "union_raw": "union",
                "upazila_raw": "upazila",
                "district_raw": "district",
            }
        )

        # Build true pairs table
        true_pairs_rows: list[dict[str, Any]] = []
        person_grouped = truth_df.groupby("person_id")
        for p_id, p_records in person_grouped:
            if len(p_records) > 1:
                r_list = p_records.to_dict(orient="records")
                for i in range(len(r_list)):
                    for j in range(i + 1, len(r_list)):
                        r1 = r_list[i]
                        r2 = r_list[j]
                        r1_id, r2_id = sorted([r1["record_id"], r2["record_id"]])
                        true_pairs_rows.append(
                            {
                                "record_id_1": r1_id,
                                "record_id_2": r2_id,
                                "person_id": p_id,
                                "source_module_1": r1["source_module"],
                                "source_module_2": r2["source_module"],
                                "is_same_module": r1["source_module"] == r2["source_module"],
                            }
                        )
        true_pairs_df = (
            pd.DataFrame(true_pairs_rows)
            if true_pairs_rows
            else pd.DataFrame(
                columns=[
                    "record_id_1",
                    "record_id_2",
                    "person_id",
                    "source_module_1",
                    "source_module_2",
                    "is_same_module",
                ]
            )
        )

        # Build doppelganger pairs table (cross-household pairs ONLY)
        doppel_rows: list[dict[str, Any]] = []
        name_loc_cols = ["clean_village", "clean_given_name", "clean_guardian_name"]
        name_loc_grouped = truth_df.groupby(name_loc_cols)
        for _, g in name_loc_grouped:
            distinct_pids = g["person_id"].unique()
            if len(distinct_pids) > 1:
                g_list = g.to_dict(orient="records")
                for i in range(len(g_list)):
                    for j in range(i + 1, len(g_list)):
                        r1 = g_list[i]
                        r2 = g_list[j]
                        if (
                            r1["person_id"] != r2["person_id"]
                            and r1["household_id"] != r2["household_id"]
                        ):
                            r1_id, r2_id = sorted([r1["record_id"], r2["record_id"]])
                            is_inj = bool(
                                r1.get("is_injected", False) or r2.get("is_injected", False)
                            )
                            doppel_rows.append(
                                {
                                    "record_id_1": r1_id,
                                    "record_id_2": r2_id,
                                    "person_id_1": r1["person_id"],
                                    "person_id_2": r2["person_id"],
                                    "household_id_1": r1["household_id"],
                                    "household_id_2": r2["household_id"],
                                    "canonical_given_name": r1["clean_given_name"],
                                    "canonical_guardian_name": r1["clean_guardian_name"],
                                    "canonical_village": r1["clean_village"],
                                    "is_injected": is_inj,
                                }
                            )
        doppel_cols = [
            "record_id_1",
            "record_id_2",
            "person_id_1",
            "person_id_2",
            "household_id_1",
            "household_id_2",
            "canonical_given_name",
            "canonical_guardian_name",
            "canonical_village",
            "is_injected",
        ]
        doppel_df = (
            pd.DataFrame(doppel_rows) if doppel_rows else pd.DataFrame(columns=doppel_cols)
        )
        if not doppel_df.empty:
            doppel_df = doppel_df.drop_duplicates(
                subset=["record_id_1", "record_id_2"]
            ).reset_index(drop=True)

        # Person-level doppelgangers
        person_pair_cols = [
            "person_id_1",
            "person_id_2",
            "household_id_1",
            "household_id_2",
            "canonical_given_name",
            "canonical_guardian_name",
            "canonical_village",
            "is_injected",
        ]
        if not doppel_df.empty:
            doppel_person_df = (
                doppel_df[person_pair_cols]
                .drop_duplicates(subset=["person_id_1", "person_id_2"])
                .reset_index(drop=True)
            )
        else:
            doppel_person_df = pd.DataFrame(columns=person_pair_cols)

        # Build audit stats DataFrame
        audit_rows: list[dict[str, Any]] = []
        for mod_name, stats in sampler.audit_stats.items():
            audit_rows.append(
                {
                    "module": mod_name,
                    "eligible_pool_size": stats["eligible_pool_size"],
                    "enrolled_unique": stats["enrolled_unique"],
                    "target_share": stats["target_share"],
                    "realised_share": stats["realised_share"],
                    "conditional_overlap_count": stats.get("conditional_overlap_count", 0),
                    "male_quota": stats.get("male_quota", 0),
                }
            )
        audit_df = pd.DataFrame(audit_rows)

        # Build corruption log DataFrame
        corr_log_df = pd.DataFrame(
            [
                {
                    "record_id": ev.record_id,
                    "field": ev.field,
                    "corruption_type": ev.corruption_type,
                    "rule_id": ev.rule_id,
                    "is_generator_only": ev.is_generator_only,
                    "before": ev.before,
                    "after": ev.after,
                }
                for ev in self.corruptor.events
            ]
        )

        registry_tables = {
            "records": records_df,
            "rosters": rosters_df,
            "club_formation": club_df,
            "upg_enrolment": upg_df,
            "microfinance_group": mfg_df,
            "livelihood_support": livelihood_df,
        }

        # Verify zero ground-truth leakage into model-visible registry files
        for tbl_name, tbl_df in registry_tables.items():
            leaked = set(tbl_df.columns) & FORBIDDEN_REGISTRY_COLUMNS
            if leaked:
                raise ValueError(
                    f"CRITICAL: Ground-truth leakage in registry '{tbl_name}': {leaked}"
                )

        truth_tables = {
            "record_truth": truth_df,
            "true_pairs": true_pairs_df,
            "corruption_log": corr_log_df,
            "doppelganger_pairs": doppel_df,
            "doppelganger_person_pairs": doppel_person_df,
            "audit_stats": audit_df,
        }

        return registry_tables, truth_tables


def export_registries(
    config_path: str | Path,
    run_name: str,
    base_data_dir: str | Path = "data/generated",
    seed_offset: int = 0,
    role: Optional[str] = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    """Load clean population, generate corrupted registries, and export to disk."""
    config_path = Path(config_path)
    base_dir = Path(base_data_dir) / run_name

    persons_parquet = base_dir / "persons.parquet"
    households_parquet = base_dir / "households.parquet"

    if not persons_parquet.exists() or not households_parquet.exists():
        err_msg = (
            f"Clean population parquet files not found in {base_dir.resolve()}. "
            "Run 'generate' first."
        )
        raise FileNotFoundError(err_msg)

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if role is None:
        role = "holdout" if seed_offset != 0 else "dev"

    effective_seed = int(config.get("seed", 42)) + seed_offset

    persons_df = pd.read_parquet(persons_parquet)
    households_df = pd.read_parquet(households_parquet)

    orchestrator = RegistryOrchestrator(config, seed=effective_seed)
    registry_tables, truth_tables = orchestrator.process(persons_df, households_df)

    # Output paths
    reg_dir = base_dir / "registry"
    truth_dir = base_dir / "truth"
    reg_dir.mkdir(parents=True, exist_ok=True)
    truth_dir.mkdir(parents=True, exist_ok=True)

    # Update manifest.json if present
    manifest_path = base_dir / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
        manifest_data["role"] = role
        manifest_data["seed_offset"] = seed_offset
        manifest_data["registry_records"] = len(registry_tables["records"])
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)

    # Write registry outputs (MODEL VISIBLE ONLY)
    records_pq = reg_dir / "records.parquet"
    rosters_pq = reg_dir / "rosters.parquet"
    registry_tables["records"].to_parquet(records_pq, engine="pyarrow", index=False)
    registry_tables["rosters"].to_parquet(rosters_pq, engine="pyarrow", index=False)
    registry_tables["club_formation"].to_csv(reg_dir / "club_formation.csv", index=False)
    registry_tables["upg_enrolment"].to_csv(reg_dir / "upg_enrolment.csv", index=False)
    registry_tables["microfinance_group"].to_csv(reg_dir / "microfinance_group.csv", index=False)
    registry_tables["livelihood_support"].to_csv(reg_dir / "livelihood_support.csv", index=False)

    # Write truth outputs (EVALUATION ONLY)
    rtruth_pq = truth_dir / "record_truth.parquet"
    tpairs_pq = truth_dir / "true_pairs.parquet"
    clog_pq = truth_dir / "corruption_log.parquet"
    dpairs_pq = truth_dir / "doppelganger_pairs.parquet"
    dppairs_pq = truth_dir / "doppelganger_person_pairs.parquet"
    astats_pq = truth_dir / "audit_stats.parquet"

    truth_tables["record_truth"].to_parquet(rtruth_pq, engine="pyarrow", index=False)
    truth_tables["true_pairs"].to_parquet(tpairs_pq, engine="pyarrow", index=False)
    truth_tables["corruption_log"].to_parquet(clog_pq, engine="pyarrow", index=False)
    truth_tables["doppelganger_pairs"].to_parquet(dpairs_pq, engine="pyarrow", index=False)
    truth_tables["doppelganger_person_pairs"].to_parquet(dppairs_pq, engine="pyarrow", index=False)
    truth_tables["audit_stats"].to_parquet(astats_pq, engine="pyarrow", index=False)

    return registry_tables, truth_tables
