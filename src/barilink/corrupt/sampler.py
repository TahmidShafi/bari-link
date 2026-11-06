"""Enrolment module sampler and doppelganger injector for bari-link."""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Final, Optional

import numpy as np
import pandas as pd

EXACT_MODULE_NAMES: Final[list[str]] = [
    "club_formation",
    "upg_enrolment",
    "microfinance_group",
    "livelihood_support",
]


@dataclass
class RosterMemberRaw:
    """A single co-resident member record in a household roster."""

    record_id: str
    member_person_id: str  # Evaluation truth
    member_name_raw: str
    relation_raw: str
    age_raw: int


@dataclass
class EnrolmentCandidate:
    """A sampled beneficiary enrolment record prior to output formatting."""

    person_id: str
    household_id: str
    source_module: str
    enrolment_date: date
    is_re_registration: bool
    is_doppelganger: bool
    is_injected: bool

    # Clean attributes at enrolment date
    clean_full_name: str
    clean_given_name: str
    clean_surname_or_title: str
    clean_sex: str
    clean_religion_group: str
    clean_birth_year: int
    clean_age_at_enrolment: int
    clean_marital_status: str
    clean_role_in_household: str
    clean_father_id: Optional[str]
    clean_mother_id: Optional[str]
    clean_spouse_id: Optional[str]
    clean_father_name: str
    clean_spouse_name: Optional[str]
    clean_guardian_type: str
    clean_guardian_name: str
    clean_phone: Optional[str]
    clean_household_phone: Optional[str]
    clean_village: str
    clean_union: str
    clean_upazila: str
    clean_district: str
    group_id: Optional[str] = None
    roster_members: Optional[list[RosterMemberRaw]] = None


class EnrolmentSampler:
    """Samples beneficiaries into the four NGO enrolment modules with realistic overlap."""

    def __init__(
        self,
        config: dict[str, Any],
        persons_df: pd.DataFrame,
        households_df: pd.DataFrame,
        rng: np.random.Generator,
    ) -> None:
        self.config = config
        self.persons_df = persons_df.copy()
        self.households_df = households_df.copy()
        self.rng = rng

        enrol_cfg = config.get("enrolment", {})
        date_range = enrol_cfg.get("date_range", ["2023-01-01", "2026-06-30"])
        self.start_date = date.fromisoformat(date_range[0])
        self.end_date = date.fromisoformat(date_range[1])
        self.total_days = (self.end_date - self.start_date).days

        self.re_registration_rate: float = float(
            enrol_cfg.get("re_registration_rate", 0.03)
        )
        self.module_cfgs = enrol_cfg.get("modules", {})
        self.cross_cfg = enrol_cfg.get("cross_module_conditional", {})

        doppel_cfg = config.get("doppelganger", {})
        self.min_doppelganger_pairs: int = int(doppel_cfg.get("min_pairs", 50))

        # Lookups
        self.person_dict = self.persons_df.set_index("person_id").to_dict(orient="index")
        self.hh_dict = self.households_df.set_index("household_id").to_dict(
            orient="index"
        )
        self.hh_members = (
            self.persons_df.groupby("household_id")["person_id"].apply(list).to_dict()
        )

        self.skipped_reregistrations = 0
        self.natural_doppelganger_person_pairs = 0
        self.injected_doppelganger_person_pairs = 0
        self.audit_stats: dict[str, Any] = {}

        # Draw a potential enrolment date for every person in the population
        # to evaluate eligibility at enrolment date (enrolment year - birth_year)
        self.person_enrol_dates: dict[str, date] = {}
        for p_id in self.persons_df["person_id"]:
            self.person_enrol_dates[p_id] = self._sample_date()

    def _sample_date(self) -> date:
        """Sample a uniform enrolment date within the configured window."""
        offset = int(self.rng.integers(0, self.total_days + 1))
        return self.start_date + timedelta(days=offset)

    def _age_at_date(self, birth_year: int, target_date: date) -> int:
        """Calculate person age at a specific enrolment date."""
        return max(0, target_date.year - birth_year)

    def sample_all_modules(self) -> list[EnrolmentCandidate]:
        """Sample candidates across all four enrolment modules and handle doppelgangers."""
        candidates: list[EnrolmentCandidate] = []

        # 1. UPG Enrolment (Household level)
        upg_candidates = self._sample_upg()
        candidates.extend(upg_candidates)

        # 2. Microfinance Group (female target share, male quota, elevated UPG overlap)
        upg_person_ids = {c.person_id for c in upg_candidates}
        mfg_candidates = self._sample_microfinance(upg_person_ids)
        candidates.extend(mfg_candidates)

        # 3. Livelihood Support (adults 18-60, both sexes, with elevated UPG overlap)
        livelihood_candidates = self._sample_livelihood(upg_person_ids)
        candidates.extend(livelihood_candidates)

        # 4. Club Formation (adolescent/young women 10-24)
        club_candidates = self._sample_club()
        candidates.extend(club_candidates)

        # 5. Add within-module re-registration duplicates (~3%)
        candidates = self._add_reregistration_duplicates(candidates)

        # 6. Check and inject doppelgangers if natural pairs < min_pairs
        candidates = self._audit_and_inject_doppelgangers(candidates)

        return candidates

    def _create_candidate(
        self,
        person_id: str,
        module_name: str,
        enrol_date: date,
        is_re_registration: bool = False,
        group_id: Optional[str] = None,
        is_doppelganger: bool = False,
        is_injected: bool = False,
    ) -> EnrolmentCandidate:
        """Create an EnrolmentCandidate object from person truth."""
        p = self.person_dict[person_id]
        hh_id = p["household_id"]
        hh = self.hh_dict.get(hh_id, {"household_phone": None})

        age = self._age_at_date(p["birth_year"], enrol_date)
        full_name = f"{p['given_name']} {p['surname_or_title']}"

        return EnrolmentCandidate(
            person_id=person_id,
            household_id=hh_id,
            source_module=module_name,
            enrolment_date=enrol_date,
            is_re_registration=is_re_registration,
            is_doppelganger=is_doppelganger,
            is_injected=is_injected,
            clean_full_name=full_name,
            clean_given_name=p["given_name"],
            clean_surname_or_title=p["surname_or_title"],
            clean_sex=p["sex"],
            clean_religion_group=p["religion_group"],
            clean_birth_year=int(p["birth_year"]),
            clean_age_at_enrolment=age,
            clean_marital_status=p["marital_status"],
            clean_role_in_household=p["role_in_household"],
            clean_father_id=p["father_id"],
            clean_mother_id=p["mother_id"],
            clean_spouse_id=p["spouse_id"],
            clean_father_name=p["father_name"],
            clean_spouse_name=p["spouse_name"],
            clean_guardian_type=p["guardian_type"],
            clean_guardian_name=p["guardian_name"],
            clean_phone=p["phone"],
            clean_household_phone=hh["household_phone"],
            clean_village=p["village"],
            clean_union=p["union"],
            clean_upazila=p["upazila"],
            clean_district=p["district"],
            group_id=group_id,
        )

    # --------------------------------------------------------------------------
    # UPG Enrolment
    # --------------------------------------------------------------------------
    def _sample_upg(self) -> list[EnrolmentCandidate]:
        """Sample UPG participants (household-level) and construct rosters."""
        cfg = self.module_cfgs.get("upg_enrolment", {})
        target_share = float(cfg.get("target_share", 0.18))

        all_hh_ids = list(self.hh_dict.keys())
        target_count = round(len(all_hh_ids) * target_share)
        selected_hh = self.rng.choice(all_hh_ids, size=target_count, replace=False)

        candidates: list[EnrolmentCandidate] = []
        for hh_id in selected_hh:
            member_ids = self.hh_members[hh_id]
            head_id = self.hh_dict[hh_id]["head_person_id"]

            # Prefer adult female 18-60 at her drawn enrolment date
            eligible_females = [
                m_id
                for m_id in member_ids
                if self.person_dict[m_id]["sex"] == "F"
                and 18
                <= self._age_at_date(
                    self.person_dict[m_id]["birth_year"],
                    self.person_enrol_dates[m_id],
                )
                <= 60
            ]
            if eligible_females:
                primary_id = eligible_females[0]
            else:
                primary_id = head_id

            enrol_date = self.person_enrol_dates[primary_id]
            cand = self._create_candidate(primary_id, "upg_enrolment", enrol_date)

            # Build full household roster of other members
            roster: list[RosterMemberRaw] = []
            for m_id in member_ids:
                if m_id == primary_id:
                    continue
                mp = self.person_dict[m_id]
                m_age = self._age_at_date(mp["birth_year"], enrol_date)
                m_full_name = f"{mp['given_name']} {mp['surname_or_title']}"
                rel = mp["role_in_household"]
                roster.append(
                    RosterMemberRaw(
                        record_id="",
                        member_person_id=m_id,
                        member_name_raw=m_full_name,
                        relation_raw=rel,
                        age_raw=m_age,
                    )
                )
            cand.roster_members = roster
            candidates.append(cand)

        self.audit_stats["upg_enrolment"] = {
            "eligible_pool_size": len(all_hh_ids),
            "enrolled_unique": len(candidates),
            "target_share": target_share,
            "realised_share": len(candidates) / len(all_hh_ids),
            "conditional_overlap_count": 0,
        }
        return candidates

    # --------------------------------------------------------------------------
    # Microfinance Group
    # --------------------------------------------------------------------------
    def _sample_microfinance(
        self, upg_person_ids: set[str]
    ) -> list[EnrolmentCandidate]:
        """Sample microfinance borrowers with group_id, female target share and male quota."""
        cfg = self.module_cfgs.get("microfinance_group", {})
        target_share = float(cfg.get("target_share", 0.30))
        male_share = float(cfg.get("male_share", 0.08))
        upg_to_mfg = float(self.cross_cfg.get("upg_to_microfinance", 0.55))

        all_pids = list(self.persons_df["person_id"])

        # Eligible pool = women aged 18-60 at enrolment date
        female_eligible = [
            p_id
            for p_id in all_pids
            if self.person_dict[p_id]["sex"] == "F"
            and 18
            <= self._age_at_date(
                self.person_dict[p_id]["birth_year"],
                self.person_enrol_dates[p_id],
            )
            <= 60
        ]
        target_count_female = round(target_share * len(female_eligible))

        # Male quota = round(target_count_female * male_share / (1 - male_share))
        target_count_male = round(target_count_female * male_share / (1.0 - male_share))
        male_eligible = [
            p_id
            for p_id in all_pids
            if self.person_dict[p_id]["sex"] == "M"
            and 18
            <= self._age_at_date(
                self.person_dict[p_id]["birth_year"],
                self.person_enrol_dates[p_id],
            )
            <= 60
        ]

        candidates: list[EnrolmentCandidate] = []
        enrolled_female: set[str] = set()
        enrolled_male: set[str] = set()
        group_counters: dict[str, int] = {}
        n_mfg_conditional = 0

        def get_group_id(p: dict[str, Any]) -> str:
            u_name = p["union"].replace(" ", "")
            g_idx = group_counters.setdefault(u_name, 1)
            gid = f"MFG_{u_name}_{g_idx:03d}"
            if self.rng.random() < 0.20:
                group_counters[u_name] += 1
            return gid

        # 1. Enrol UPG-conditional candidates who are in eligible pools
        upg_shuffled = sorted(list(upg_person_ids))
        self.rng.shuffle(upg_shuffled)
        for p_id in upg_shuffled:
            p = self.person_dict[p_id]
            is_f = p["sex"] == "F"
            if is_f and p_id in female_eligible and len(enrolled_female) < target_count_female:
                if self.rng.random() < upg_to_mfg:
                    enrol_date = self.person_enrol_dates[p_id]
                    cand = self._create_candidate(
                        p_id, "microfinance_group", enrol_date, group_id=get_group_id(p)
                    )
                    candidates.append(cand)
                    enrolled_female.add(p_id)
                    n_mfg_conditional += 1
            elif not is_f and p_id in male_eligible and len(enrolled_male) < target_count_male:
                if self.rng.random() < upg_to_mfg:
                    enrol_date = self.person_enrol_dates[p_id]
                    cand = self._create_candidate(
                        p_id, "microfinance_group", enrol_date, group_id=get_group_id(p)
                    )
                    candidates.append(cand)
                    enrolled_male.add(p_id)
                    n_mfg_conditional += 1

        # 2. Top up females
        needed_female = target_count_female - len(enrolled_female)
        remaining_female = [p_id for p_id in female_eligible if p_id not in enrolled_female]
        selected_remaining_female = self.rng.choice(
            remaining_female, size=needed_female, replace=False
        )
        for p_id in selected_remaining_female:
            p = self.person_dict[p_id]
            enrol_date = self.person_enrol_dates[p_id]
            cand = self._create_candidate(
                p_id, "microfinance_group", enrol_date, group_id=get_group_id(p)
            )
            candidates.append(cand)
            enrolled_female.add(p_id)

        # 3. Top up males
        needed_male = target_count_male - len(enrolled_male)
        remaining_male = [p_id for p_id in male_eligible if p_id not in enrolled_male]
        selected_remaining_male = self.rng.choice(
            remaining_male, size=needed_male, replace=False
        )
        for p_id in selected_remaining_male:
            p = self.person_dict[p_id]
            enrol_date = self.person_enrol_dates[p_id]
            cand = self._create_candidate(
                p_id, "microfinance_group", enrol_date, group_id=get_group_id(p)
            )
            candidates.append(cand)
            enrolled_male.add(p_id)

        self.audit_stats["microfinance_group"] = {
            "eligible_pool_size": len(female_eligible),
            "enrolled_unique": len(enrolled_female) + len(enrolled_male),
            "enrolled_female": len(enrolled_female),
            "target_count_female": target_count_female,
            "male_quota": target_count_male,
            "target_share": target_share,
            "realised_share": len(enrolled_female) / len(female_eligible),
            "conditional_overlap_count": n_mfg_conditional,
        }
        return candidates

    # --------------------------------------------------------------------------
    # Livelihood Support
    # --------------------------------------------------------------------------
    def _sample_livelihood(
        self, upg_person_ids: set[str]
    ) -> list[EnrolmentCandidate]:
        """Sample livelihood recipients (adults 18-60, short roster)."""
        cfg = self.module_cfgs.get("livelihood_support", {})
        target_share = float(cfg.get("target_share", 0.22))
        upg_to_live = float(self.cross_cfg.get("upg_to_livelihood", 0.45))

        all_pids = list(self.persons_df["person_id"])
        adult_eligible = [
            p_id
            for p_id in all_pids
            if 18
            <= self._age_at_date(
                self.person_dict[p_id]["birth_year"],
                self.person_enrol_dates[p_id],
            )
            <= 60
        ]
        target_count = round(target_share * len(adult_eligible))

        candidates: list[EnrolmentCandidate] = []
        enrolled_persons: set[str] = set()
        n_live_conditional = 0

        # 1. Enrol UPG-conditional candidates who are in eligible pool
        upg_shuffled = sorted(list(upg_person_ids))
        self.rng.shuffle(upg_shuffled)
        for p_id in upg_shuffled:
            if p_id in adult_eligible and len(enrolled_persons) < target_count:
                if self.rng.random() < upg_to_live:
                    enrol_date = self.person_enrol_dates[p_id]
                    cand = self._create_candidate(p_id, "livelihood_support", enrol_date)
                    self._attach_short_roster(cand, enrol_date)
                    candidates.append(cand)
                    enrolled_persons.add(p_id)
                    n_live_conditional += 1

        # 2. Top up from remaining eligible pool
        needed = target_count - len(enrolled_persons)
        remaining = [p_id for p_id in adult_eligible if p_id not in enrolled_persons]
        selected_remaining = self.rng.choice(remaining, size=needed, replace=False)
        for p_id in selected_remaining:
            enrol_date = self.person_enrol_dates[p_id]
            cand = self._create_candidate(p_id, "livelihood_support", enrol_date)
            self._attach_short_roster(cand, enrol_date)
            candidates.append(cand)
            enrolled_persons.add(p_id)

        self.audit_stats["livelihood_support"] = {
            "eligible_pool_size": len(adult_eligible),
            "enrolled_unique": len(candidates),
            "target_share": target_share,
            "realised_share": len(candidates) / len(adult_eligible),
            "conditional_overlap_count": n_live_conditional,
        }
        return candidates

    def _attach_short_roster(
        self, cand: EnrolmentCandidate, enrol_date: date
    ) -> None:
        """Attach short roster: head plus up to 3 members."""
        hh_id = cand.household_id
        member_ids = self.hh_members[hh_id]
        head_id = self.hh_dict[hh_id]["head_person_id"]

        roster_pids: list[str] = []
        if head_id != cand.person_id:
            roster_pids.append(head_id)

        other_members = [
            m for m in member_ids if m != cand.person_id and m != head_id
        ]
        for m in other_members[:2]:
            roster_pids.append(m)

        roster: list[RosterMemberRaw] = []
        for m_id in roster_pids:
            mp = self.person_dict[m_id]
            m_age = self._age_at_date(mp["birth_year"], enrol_date)
            m_full_name = f"{mp['given_name']} {mp['surname_or_title']}"
            rel = mp["role_in_household"]
            roster.append(
                RosterMemberRaw(
                    record_id="",
                    member_person_id=m_id,
                    member_name_raw=m_full_name,
                    relation_raw=rel,
                    age_raw=m_age,
                )
            )
        cand.roster_members = roster

    # --------------------------------------------------------------------------
    # Club Formation
    # --------------------------------------------------------------------------
    def _sample_club(self) -> list[EnrolmentCandidate]:
        """Sample adolescent/young women (females aged 10-24 at enrolment date)."""
        cfg = self.module_cfgs.get("club_formation", {})
        target_share = float(cfg.get("target_share", 0.25))

        all_pids = list(self.persons_df["person_id"])
        club_eligible = [
            p_id
            for p_id in all_pids
            if self.person_dict[p_id]["sex"] == "F"
            and 10
            <= self._age_at_date(
                self.person_dict[p_id]["birth_year"],
                self.person_enrol_dates[p_id],
            )
            <= 24
        ]
        target_count = round(target_share * len(club_eligible))

        selected = self.rng.choice(club_eligible, size=target_count, replace=False)
        candidates: list[EnrolmentCandidate] = []
        for p_id in selected:
            enrol_date = self.person_enrol_dates[p_id]
            cand = self._create_candidate(p_id, "club_formation", enrol_date)
            candidates.append(cand)

        self.audit_stats["club_formation"] = {
            "eligible_pool_size": len(club_eligible),
            "enrolled_unique": len(candidates),
            "target_share": target_share,
            "realised_share": len(candidates) / len(club_eligible),
            "conditional_overlap_count": 0,
        }
        return candidates

    # --------------------------------------------------------------------------
    # Re-Registration Duplicates
    # --------------------------------------------------------------------------
    def _add_reregistration_duplicates(
        self, candidates: list[EnrolmentCandidate]
    ) -> list[EnrolmentCandidate]:
        """Inject ~3% within-module duplicate records on a later date <= 2026-06-30."""
        dups: list[EnrolmentCandidate] = []
        for cand in candidates:
            if self.rng.random() < self.re_registration_rate:
                # Second date strictly between (enrol_date + 30 days) and end_date
                min_second_date = cand.enrolment_date + timedelta(days=30)
                if min_second_date >= self.end_date:
                    self.skipped_reregistrations += 1
                    continue

                remaining_days = (self.end_date - min_second_date).days
                offset = int(self.rng.integers(0, remaining_days + 1))
                second_date = min_second_date + timedelta(days=offset)

                dup_cand = self._create_candidate(
                    person_id=cand.person_id,
                    module_name=cand.source_module,
                    enrol_date=second_date,
                    is_re_registration=True,
                    group_id=cand.group_id,
                    is_doppelganger=cand.is_doppelganger,
                    is_injected=cand.is_injected,
                )
                if cand.roster_members:
                    dup_roster: list[RosterMemberRaw] = []
                    for rm in cand.roster_members:
                        m_birth = self.person_dict[rm.member_person_id]["birth_year"]
                        new_age = self._age_at_date(m_birth, second_date)
                        dup_roster.append(
                            RosterMemberRaw(
                                record_id="",
                                member_person_id=rm.member_person_id,
                                member_name_raw=rm.member_name_raw,
                                relation_raw=rm.relation_raw,
                                age_raw=new_age,
                            )
                        )
                    dup_cand.roster_members = dup_roster

                dups.append(dup_cand)

        return candidates + dups

    # --------------------------------------------------------------------------
    # Doppelgangers (Hard Negatives)
    # --------------------------------------------------------------------------
    def _audit_and_inject_doppelgangers(
        self, candidates: list[EnrolmentCandidate]
    ) -> list[EnrolmentCandidate]:
        """Audit natural enrolled doppelgangers across distinct households and inject if needed."""
        enrolled_pids = {c.person_id for c in candidates}
        enrolled_persons_df = self.persons_df[
            self.persons_df["person_id"].isin(enrolled_pids)
        ]

        grouped = enrolled_persons_df.groupby(
            ["village", "given_name", "guardian_name"]
        )
        natural_pairs: set[tuple[str, str]] = set()
        for _, g in grouped:
            if len(g["household_id"].unique()) > 1:
                p_list = g.to_dict(orient="records")
                for i in range(len(p_list)):
                    for j in range(i + 1, len(p_list)):
                        p1 = p_list[i]
                        p2 = p_list[j]
                        if p1["household_id"] != p2["household_id"]:
                            pair = tuple(sorted([p1["person_id"], p2["person_id"]]))
                            natural_pairs.add(pair)

        self.natural_doppelganger_person_pairs = len(natural_pairs)
        self.injected_doppelganger_person_pairs = 0

        if len(natural_pairs) >= self.min_doppelganger_pairs:
            return candidates

        needed = self.min_doppelganger_pairs - len(natural_pairs)
        hh_nums = self.households_df["household_id"].str.extract(r"(\d+)")[0].astype(int)
        max_hh_num = int(hh_nums.max())
        p_nums = self.persons_df["person_id"].str.extract(r"(\d+)")[0].astype(int)
        max_p_num = int(p_nums.max())

        chosen_candidates = [c for c in candidates if not c.is_re_registration][:needed]
        new_candidates: list[EnrolmentCandidate] = []

        for base_cand in chosen_candidates:
            max_hh_num += 1
            max_p_num += 1
            new_hh_id = f"HH_{max_hh_num:06d}"
            cousin_id = f"P_{max_p_num:07d}"

            cousin_cand = EnrolmentCandidate(
                person_id=cousin_id,
                household_id=new_hh_id,
                source_module=base_cand.source_module,
                enrolment_date=base_cand.enrolment_date,
                is_re_registration=False,
                is_doppelganger=True,
                is_injected=True,
                clean_full_name=base_cand.clean_full_name,
                clean_given_name=base_cand.clean_given_name,
                clean_surname_or_title=base_cand.clean_surname_or_title,
                clean_sex=base_cand.clean_sex,
                clean_religion_group=base_cand.clean_religion_group,
                clean_birth_year=base_cand.clean_birth_year,
                clean_age_at_enrolment=base_cand.clean_age_at_enrolment,
                clean_marital_status=base_cand.clean_marital_status,
                clean_role_in_household="head",
                clean_father_id=None,
                clean_mother_id=None,
                clean_spouse_id=None,
                clean_father_name=base_cand.clean_father_name,
                clean_spouse_name=base_cand.clean_spouse_name,
                clean_guardian_type=base_cand.clean_guardian_type,
                clean_guardian_name=base_cand.clean_guardian_name,
                clean_phone=base_cand.clean_phone,
                clean_household_phone=base_cand.clean_household_phone,
                clean_village=base_cand.clean_village,
                clean_union=base_cand.clean_union,
                clean_upazila=base_cand.clean_upazila,
                clean_district=base_cand.clean_district,
                group_id=base_cand.group_id,
            )
            new_candidates.append(cousin_cand)
            self.injected_doppelganger_person_pairs += 1

            # Update dictionaries so injected person is recognized if looked up
            self.person_dict[cousin_id] = {
                "person_id": cousin_id,
                "household_id": new_hh_id,
                "given_name": base_cand.clean_given_name,
                "surname_or_title": base_cand.clean_surname_or_title,
                "sex": base_cand.clean_sex,
                "religion_group": base_cand.clean_religion_group,
                "birth_year": base_cand.clean_birth_year,
                "age_at_reference_date": base_cand.clean_age_at_enrolment,
                "marital_status": base_cand.clean_marital_status,
                "role_in_household": "head",
                "father_id": None,
                "mother_id": None,
                "spouse_id": None,
                "father_name": base_cand.clean_father_name,
                "spouse_name": base_cand.clean_spouse_name,
                "guardian_type": base_cand.clean_guardian_type,
                "guardian_name": base_cand.clean_guardian_name,
                "phone": base_cand.clean_phone,
                "village": base_cand.clean_village,
                "union": base_cand.clean_union,
                "upazila": base_cand.clean_upazila,
                "district": base_cand.clean_district,
                "is_injected": True,
            }
            self.hh_dict[new_hh_id] = {
                "household_id": new_hh_id,
                "village": base_cand.clean_village,
                "union": base_cand.clean_union,
                "upazila": base_cand.clean_upazila,
                "district": base_cand.clean_district,
                "head_person_id": cousin_id,
                "n_members": 1,
                "household_phone": base_cand.clean_household_phone,
            }

        return candidates + new_candidates
