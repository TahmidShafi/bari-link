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

    def _sample_date(self) -> date:
        """Sample a uniform enrolment date within the configured window."""
        offset = int(self.rng.integers(0, self.total_days + 1))
        return self.start_date + timedelta(days=offset)

    def _age_at_date(self, birth_year: int, target_date: date) -> int:
        """Calculate person age at a specific enrolment date."""
        return max(0, target_date.year - birth_year)

    def sample_all_modules(self) -> list[EnrolmentCandidate]:
        """Sample candidates across all four enrolment modules and handle doppelgangers."""
        # 1. First, find or inject doppelgangers to ensure min_pairs target
        self._ensure_doppelgangers()

        # Rebuild lookups in case households were injected
        self.person_dict = self.persons_df.set_index("person_id").to_dict(orient="index")
        self.hh_dict = self.households_df.set_index("household_id").to_dict(
            orient="index"
        )
        self.hh_members = (
            self.persons_df.groupby("household_id")["person_id"].apply(list).to_dict()
        )

        candidates: list[EnrolmentCandidate] = []

        # 2. UPG Enrolment (Household level)
        upg_candidates = self._sample_upg()
        candidates.extend(upg_candidates)

        # 3. Microfinance Group (mostly women 18-60, with elevated UPG overlap)
        upg_person_ids = {c.person_id for c in upg_candidates}
        mfg_candidates = self._sample_microfinance(upg_person_ids)
        candidates.extend(mfg_candidates)

        # 4. Livelihood Support (adults 18-60, both sexes, with elevated UPG overlap)
        livelihood_candidates = self._sample_livelihood(upg_person_ids)
        candidates.extend(livelihood_candidates)

        # 5. Club Formation (adolescent/young women 10-24)
        club_candidates = self._sample_club()
        candidates.extend(club_candidates)

        # 6. Add within-module re-registration duplicates (~3%)
        candidates = self._add_reregistration_duplicates(candidates)

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
        hh = self.hh_dict[hh_id]

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
        n_upg = int(len(all_hh_ids) * target_share)
        selected_hh = self.rng.choice(all_hh_ids, size=n_upg, replace=False)

        candidates: list[EnrolmentCandidate] = []
        for hh_id in selected_hh:
            member_ids = self.hh_members[hh_id]
            enrol_date = self._sample_date()

            # Prefer adult female 18-60
            eligible_females = [
                m_id
                for m_id in member_ids
                if self.person_dict[m_id]["sex"] == "F"
                and 18
                <= self._age_at_date(self.person_dict[m_id]["birth_year"], enrol_date)
                <= 60
            ]
            if eligible_females:
                primary_id = eligible_females[0]
            else:
                # Fallback to household head or adult member
                primary_id = self.hh_dict[hh_id]["head_person_id"]

            cand = self._create_candidate(
                primary_id, "upg_enrolment", enrol_date
            )

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
                        record_id="",  # Bound later in registry
                        member_person_id=m_id,
                        member_name_raw=m_full_name,
                        relation_raw=rel,
                        age_raw=m_age,
                    )
                )
            cand.roster_members = roster
            candidates.append(cand)

        return candidates

    # --------------------------------------------------------------------------
    # Microfinance Group
    # --------------------------------------------------------------------------
    def _sample_microfinance(
        self, upg_person_ids: set[str]
    ) -> list[EnrolmentCandidate]:
        """Sample microfinance borrowers with group_id and elevated UPG overlap."""
        cfg = self.module_cfgs.get("microfinance_group", {})
        target_share = float(cfg.get("target_share", 0.30))
        female_share = float(cfg.get("female_share", 0.92))
        upg_to_mfg = float(self.cross_cfg.get("upg_to_microfinance", 0.55))

        candidates: list[EnrolmentCandidate] = []
        enrolled_persons: set[str] = set()

        # Group ID generators per union
        group_counters: dict[str, int] = {}

        # 1. Overlap with UPG participants
        for p_id in upg_person_ids:
            p = self.person_dict[p_id]
            enrol_date = self._sample_date()
            age = self._age_at_date(p["birth_year"], enrol_date)
            if 18 <= age <= 60 and self.rng.random() < upg_to_mfg:
                u_name = p["union"].replace(" ", "")
                g_idx = group_counters.setdefault(u_name, 1)
                group_id = f"MFG_{u_name}_{g_idx:03d}"
                if self.rng.random() < 0.20:
                    group_counters[u_name] += 1

                cand = self._create_candidate(
                    p_id, "microfinance_group", enrol_date, group_id=group_id
                )
                candidates.append(cand)
                enrolled_persons.add(p_id)

        # 2. General population sampling
        target_total = int(len(self.persons_df) * target_share)
        all_pids = list(self.persons_df["person_id"])
        self.rng.shuffle(all_pids)

        for p_id in all_pids:
            if len(candidates) >= target_total:
                break
            if p_id in enrolled_persons:
                continue

            p = self.person_dict[p_id]
            enrol_date = self._sample_date()
            age = self._age_at_date(p["birth_year"], enrol_date)
            if not (18 <= age <= 60):
                continue

            # Respect female share
            is_female = p["sex"] == "F"
            if is_female and self.rng.random() > female_share:
                continue
            if not is_female and self.rng.random() < female_share:
                continue

            u_name = p["union"].replace(" ", "")
            g_idx = group_counters.setdefault(u_name, 1)
            group_id = f"MFG_{u_name}_{g_idx:03d}"
            if self.rng.random() < 0.20:
                group_counters[u_name] += 1

            cand = self._create_candidate(
                p_id, "microfinance_group", enrol_date, group_id=group_id
            )
            candidates.append(cand)
            enrolled_persons.add(p_id)

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

        candidates: list[EnrolmentCandidate] = []
        enrolled_persons: set[str] = set()

        # 1. Overlap with UPG participants
        for p_id in upg_person_ids:
            p = self.person_dict[p_id]
            enrol_date = self._sample_date()
            age = self._age_at_date(p["birth_year"], enrol_date)
            if 18 <= age <= 60 and self.rng.random() < upg_to_live:
                cand = self._create_candidate(
                    p_id, "livelihood_support", enrol_date
                )
                self._attach_short_roster(cand, enrol_date)
                candidates.append(cand)
                enrolled_persons.add(p_id)

        # 2. General population
        target_total = int(len(self.persons_df) * target_share)
        all_pids = list(self.persons_df["person_id"])
        self.rng.shuffle(all_pids)

        for p_id in all_pids:
            if len(candidates) >= target_total:
                break
            if p_id in enrolled_persons:
                continue

            p = self.person_dict[p_id]
            enrol_date = self._sample_date()
            age = self._age_at_date(p["birth_year"], enrol_date)
            if not (18 <= age <= 60):
                continue

            cand = self._create_candidate(p_id, "livelihood_support", enrol_date)
            self._attach_short_roster(cand, enrol_date)
            candidates.append(cand)
            enrolled_persons.add(p_id)

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
        """Sample adolescent/young women (females aged 10-24)."""
        cfg = self.module_cfgs.get("club_formation", {})
        target_share = float(cfg.get("target_share", 0.25))

        candidates: list[EnrolmentCandidate] = []
        all_pids = list(self.persons_df["person_id"])
        self.rng.shuffle(all_pids)

        for p_id in all_pids:
            p = self.person_dict[p_id]
            if p["sex"] != "F":
                continue

            enrol_date = self._sample_date()
            age = self._age_at_date(p["birth_year"], enrol_date)
            if not (10 <= age <= 24):
                continue

            if self.rng.random() < target_share:
                cand = self._create_candidate(p_id, "club_formation", enrol_date)
                candidates.append(cand)

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
                    # Duplicate roster members with updated ages
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
    def _ensure_doppelgangers(self) -> None:
        """Ensure clean population has sufficient doppelganger pairs."""
        # Find existing natural pairs
        grouped = self.persons_df.groupby(
            ["village", "given_name", "guardian_name"]
        )
        natural_pairs: list[tuple[str, str]] = []
        for _, g in grouped:
            if len(g["household_id"].unique()) > 1:
                pids = list(g["person_id"])
                for i in range(len(pids)):
                    for j in range(i + 1, len(pids)):
                        hh_i = g.loc[g["person_id"] == pids[i], "household_id"].iloc[0]
                        hh_j = g.loc[g["person_id"] == pids[j], "household_id"].iloc[0]
                        if hh_i != hh_j:
                            natural_pairs.append((pids[i], pids[j]))

        if len(natural_pairs) >= self.min_doppelganger_pairs:
            return

        needed_pairs = self.min_doppelganger_pairs - len(natural_pairs)
        # Inject additional cousin households sharing grandfather's name pattern
        injected_persons: list[dict[str, Any]] = []
        injected_households: list[dict[str, Any]] = []

        hh_nums = self.households_df["household_id"].str.extract(r"(\d+)")[0].astype(int)
        max_hh_num = int(hh_nums.max())
        p_nums = self.persons_df["person_id"].str.extract(r"(\d+)")[0].astype(int)
        max_p_num = int(p_nums.max())

        # Select random existing households to create cousins for
        sample_hhs = self.households_df.sample(
            n=min(needed_pairs, len(self.households_df)),
            random_state=int(self.rng.integers(1, 1000000)),
        )

        for _, base_hh in sample_hhs.iterrows():
            max_hh_num += 1
            new_hh_id = f"HH_{max_hh_num:06d}"
            village = base_hh["village"]
            union = base_hh["union"]
            upazila = base_hh["upazila"]
            district = base_hh["district"]

            # Base household head
            base_head_id = base_hh["head_person_id"]
            base_head = self.persons_df[self.persons_df["person_id"] == base_head_id].iloc[0]

            # Generate cousin head sharing grandfather's surname and living in same village
            max_p_num += 1
            cousin_id = f"P_{max_p_num:07d}"

            cousin_age = int(base_head["age_at_reference_date"])
            cousin_birth = int(base_head["birth_year"])
            cousin_given = base_head["given_name"]  # Identical given name
            cousin_surname = base_head["surname_or_title"]
            cousin_father_name = base_head["father_name"]  # Identical grandfather/guardian name

            cousin_person = {
                "person_id": cousin_id,
                "household_id": new_hh_id,
                "given_name": cousin_given,
                "surname_or_title": cousin_surname,
                "sex": base_head["sex"],
                "religion_group": base_head["religion_group"],
                "birth_year": cousin_birth,
                "age_at_reference_date": cousin_age,
                "marital_status": base_head["marital_status"],
                "role_in_household": "head",
                "father_id": None,
                "mother_id": None,
                "spouse_id": None,
                "father_name": cousin_father_name,
                "spouse_name": base_head["spouse_name"],
                "guardian_type": base_head["guardian_type"],
                "guardian_name": base_head["guardian_name"],
                "phone": base_head["phone"],
                "village": village,
                "union": union,
                "upazila": upazila,
                "district": district,
                "is_injected": True,
            }
            injected_persons.append(cousin_person)

            injected_households.append(
                {
                    "household_id": new_hh_id,
                    "village": village,
                    "union": union,
                    "upazila": upazila,
                    "district": district,
                    "head_person_id": cousin_id,
                    "n_members": 1,
                    "household_phone": base_hh["household_phone"],
                }
            )

        if injected_persons:
            new_p_df = pd.DataFrame(injected_persons)
            new_h_df = pd.DataFrame(injected_households)
            if "is_injected" not in self.persons_df.columns:
                self.persons_df["is_injected"] = False
            self.persons_df = pd.concat([self.persons_df, new_p_df], ignore_index=True)
            self.households_df = pd.concat([self.households_df, new_h_df], ignore_index=True)
