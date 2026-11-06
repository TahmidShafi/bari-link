"""Ground-truth synthetic population generator for rural Bangladesh.

Generates household-structured populations ("bari" / khana) with realistic
demographic roles, generational age constraints, kinship relationships,
mobile phone penetration, and Zipf-Mandelbrot nominal distributions.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final, Optional

import numpy as np
import pandas as pd
import yaml

from barilink import __version__
from barilink.generate.name_pools import (
    FEMALE_GIVEN_NAMES_HINDU,
    FEMALE_GIVEN_NAMES_MUSLIM,
    MALE_GIVEN_NAMES_HINDU,
    MALE_GIVEN_NAMES_MUSLIM,
    SURNAMES_HINDU,
    SURNAMES_HINDU_FEMALE_TITLES,
    SURNAMES_MUSLIM_FEMALE,
    SURNAMES_MUSLIM_MALE,
    compute_zipf_mandelbrot_weights,
    sample_name,
)

VALID_MARITAL_STATUSES: Final[set[str]] = {
    "married",
    "unmarried",
    "widowed",
    "separated",
}
VALID_GUARDIAN_TYPES: Final[set[str]] = {"father", "husband"}


@dataclass
class Person:
    """Ground-truth person record."""

    person_id: str
    household_id: str
    given_name: str
    surname_or_title: str
    sex: str  # "F" or "M"
    religion_group: str  # "muslim" or "hindu"
    birth_year: int
    age_at_reference_date: int
    marital_status: str  # "married", "unmarried", "widowed", "separated"
    role_in_household: str  # "head", "spouse", "child", "parent", "daughter_in_law", "grandchild"
    father_id: Optional[str]
    mother_id: Optional[str]
    spouse_id: Optional[str]
    father_name: str
    father_given_name: str
    spouse_name: Optional[str]
    guardian_type: str  # "father" or "husband"
    guardian_name: str
    phone: Optional[str]
    village: str
    union: str
    upazila: str
    district: str

    @property
    def full_name(self) -> str:
        """Canonical full name without prefixes."""
        return f"{self.given_name} {self.surname_or_title}"


@dataclass
class Household:
    """Ground-truth household record."""

    household_id: str
    village: str
    union: str
    upazila: str
    district: str
    head_person_id: str
    n_members: int
    household_phone: Optional[str]


class PopulationGenerator:
    """Deterministic generator for synthetic clean ground-truth populations."""

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.seed: int = int(config.get("seed", 42))
        self.rng = np.random.default_rng(self.seed)

        ref_date_str = config.get("reference_date", "2026-01-01")
        self.reference_year: int = datetime.fromisoformat(ref_date_str).year

        # Name sampling setup
        ns_cfg = config.get("name_sampling", {})
        self.zipf_exponent: float = float(ns_cfg.get("zipf_exponent", 1.1))
        self.zipf_offset: float = float(ns_cfg.get("zipf_offset", 3.0))
        self.hindu_share: float = float(ns_cfg.get("hindu_share", 0.10))

        # Precompute Zipf-Mandelbrot weights
        self.weights_female_muslim = compute_zipf_mandelbrot_weights(
            len(FEMALE_GIVEN_NAMES_MUSLIM), self.zipf_exponent, self.zipf_offset
        )
        self.weights_male_muslim = compute_zipf_mandelbrot_weights(
            len(MALE_GIVEN_NAMES_MUSLIM), self.zipf_exponent, self.zipf_offset
        )
        self.weights_female_hindu = compute_zipf_mandelbrot_weights(
            len(FEMALE_GIVEN_NAMES_HINDU), self.zipf_exponent, self.zipf_offset
        )
        self.weights_male_hindu = compute_zipf_mandelbrot_weights(
            len(MALE_GIVEN_NAMES_HINDU), self.zipf_exponent, self.zipf_offset
        )

        # Phone ownership setup
        po_cfg = config.get("phone_ownership", {})
        self.household_phone_rate: float = float(po_cfg.get("household_penetration", 0.88))
        self.male_phone_rate: float = float(po_cfg.get("adult_male_individual", 0.60))
        self.female_phone_rate: float = float(po_cfg.get("adult_female_individual", 0.30))
        self.min_phone_age: int = int(po_cfg.get("min_phone_age", 15))

        # Household demographics setup
        hs_cfg = config.get("household_size_dist", {})
        self.hh_sizes: list[int] = list(hs_cfg.get("sizes", [2, 3, 4, 5, 6, 7, 8]))
        raw_weights = np.array(
            hs_cfg.get("weights", [0.10, 0.20, 0.30, 0.22, 0.11, 0.05, 0.02]),
            dtype=np.float64,
        )
        self.hh_size_weights = raw_weights / np.sum(raw_weights)

        head_cfg = config.get("head_gender_dist", {})
        self.male_head_share: float = float(head_cfg.get("male_share", 0.85))

        # Geography flattening
        self.villages = self._flatten_geography(config.get("geography", {}))

        self._person_counter = 0

    def _flatten_geography(
        self, geo_cfg: dict[str, Any]
    ) -> list[tuple[str, str, str, str]]:
        """Flatten nested geographic hierarchy into (district, upazila, union, village) tuples."""
        villages_list: list[tuple[str, str, str, str]] = []
        default_villages = geo_cfg.get(
            "villages_per_union",
            ["Mondal Para", "Dokkhin Para", "Uttar Para", "Majher Char"],
        )

        for district in geo_cfg.get("districts", []):
            d_name = district["name"]
            for upazila in district.get("upazilas", []):
                u_name = upazila["name"]
                for union in upazila.get("unions", []):
                    for v_name in default_villages:
                        villages_list.append((d_name, u_name, union, v_name))

        if not villages_list:
            raise ValueError("No villages defined in geography configuration.")
        return villages_list

    def _generate_phone(self) -> str:
        """Generate a synthetic Bangladeshi mobile phone matching ^01[3-9]\\d{8}$."""
        op_digit = self.rng.integers(3, 10)  # 3 through 9 inclusive
        rest_digits = self.rng.integers(0, 100_000_000)
        return f"01{op_digit}{rest_digits:08d}"

    def _sample_person_name(
        self, sex: str, religion: str
    ) -> tuple[str, str]:
        """Sample canonical given_name and surname_or_title."""
        if religion == "hindu":
            if sex == "F":
                given = sample_name(
                    FEMALE_GIVEN_NAMES_HINDU, self.weights_female_hindu, self.rng
                )
                surname = str(self.rng.choice(SURNAMES_HINDU_FEMALE_TITLES))
            else:
                given = sample_name(
                    MALE_GIVEN_NAMES_HINDU, self.weights_male_hindu, self.rng
                )
                surname = str(self.rng.choice(SURNAMES_HINDU))
        else:
            if sex == "F":
                given = sample_name(
                    FEMALE_GIVEN_NAMES_MUSLIM, self.weights_female_muslim, self.rng
                )
                surname = str(self.rng.choice(SURNAMES_MUSLIM_FEMALE))
            else:
                given = sample_name(
                    MALE_GIVEN_NAMES_MUSLIM, self.weights_male_muslim, self.rng
                )
                surname = str(self.rng.choice(SURNAMES_MUSLIM_MALE))
        return given, surname

    def _sample_distinct_given_name(
        self,
        sex: str,
        religion: str,
        used_given_names: set[str],
        forbidden_names: Optional[set[str]] = None,
        hh_id: str = "",
    ) -> tuple[str, str]:
        """Sample given_name and surname, ensuring given_name is not already in used or forbidden.

        Safeguarded by max 200 attempts, raising RuntimeError on exhaustion.
        """
        forbidden = used_given_names | (forbidden_names or set())
        for _ in range(1, 201):
            given, surname = self._sample_person_name(sex, religion)
            if given not in forbidden:
                used_given_names.add(given)
                return given, surname
        pool_name = f"{religion}_{'female' if sex == 'F' else 'male'}_given_names"
        raise RuntimeError(
            f"Exceeded 200 attempts sampling distinct given name for household {hh_id} "
            f"from pool '{pool_name}'. Forbidden names: {forbidden}"
        )

    def _sample_full_name(self, sex: str, religion: str) -> tuple[str, str]:
        """Generate a canonical given name and full name for an absent or deceased relative."""
        given, surname = self._sample_person_name(sex, religion)
        return given, f"{given} {surname}"

    def _next_person_id(self) -> str:
        self._person_counter += 1
        return f"P_{self._person_counter:07d}"

    def generate(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Generate clean ground-truth persons and households DataFrames."""
        n_households: int = int(self.config.get("n_households", 3000))
        all_persons: list[Person] = []
        all_households: list[Household] = []

        for hh_idx in range(1, n_households + 1):
            hh_id = f"HH_{hh_idx:06d}"

            # Location
            v_idx = int(self.rng.choice(len(self.villages)))
            district, upazila, union, village = self.villages[v_idx]

            # Religion
            religion = "hindu" if self.rng.random() < self.hindu_share else "muslim"

            # Household size
            hh_size_idx = int(self.rng.choice(len(self.hh_sizes), p=self.hh_size_weights))
            hh_size = self.hh_sizes[hh_size_idx]

            # Household phone
            hh_phone = (
                self._generate_phone()
                if self.rng.random() < self.household_phone_rate
                else None
            )

            # Head gender
            is_male_head = self.rng.random() < self.male_head_share

            hh_persons: list[Person] = []

            if is_male_head:
                hh_persons = self._generate_male_headed_household(
                    hh_id=hh_id,
                    hh_size=hh_size,
                    religion=religion,
                    district=district,
                    upazila=upazila,
                    union=union,
                    village=village,
                )
            else:
                hh_persons = self._generate_female_headed_household(
                    hh_id=hh_id,
                    hh_size=hh_size,
                    religion=religion,
                    district=district,
                    upazila=upazila,
                    union=union,
                    village=village,
                )

            head_person = next(p for p in hh_persons if p.role_in_household == "head")

            hh_record = Household(
                household_id=hh_id,
                village=village,
                union=union,
                upazila=upazila,
                district=district,
                head_person_id=head_person.person_id,
                n_members=len(hh_persons),
                household_phone=hh_phone,
            )

            all_households.append(hh_record)
            all_persons.extend(hh_persons)

        # Convert to DataFrames
        persons_df = pd.DataFrame([asdict(p) for p in all_persons])
        households_df = pd.DataFrame([asdict(h) for h in all_households])

        # Enforce column order and data types
        persons_columns = [
            "person_id",
            "household_id",
            "given_name",
            "surname_or_title",
            "sex",
            "religion_group",
            "birth_year",
            "age_at_reference_date",
            "marital_status",
            "role_in_household",
            "father_id",
            "mother_id",
            "spouse_id",
            "father_name",
            "father_given_name",
            "spouse_name",
            "guardian_type",
            "guardian_name",
            "phone",
            "village",
            "union",
            "upazila",
            "district",
        ]
        households_columns = [
            "household_id",
            "village",
            "union",
            "upazila",
            "district",
            "head_person_id",
            "n_members",
            "household_phone",
        ]

        persons_df = persons_df[persons_columns]
        households_df = households_df[households_columns]

        # Explicit typing for deterministic Parquet schema
        int_cols = ["birth_year", "age_at_reference_date"]
        for col in int_cols:
            persons_df[col] = persons_df[col].astype("int32")
        households_df["n_members"] = households_df["n_members"].astype("int32")

        return persons_df, households_df

    def _assign_phone(self, sex: str, age: int) -> Optional[str]:
        """Assign an individual phone number according to age and sex rates."""
        if age < self.min_phone_age:
            return None
        rate = self.male_phone_rate if sex == "M" else self.female_phone_rate
        if self.rng.random() < rate:
            return self._generate_phone()
        return None

    def _generate_male_headed_household(
        self,
        hh_id: str,
        hh_size: int,
        religion: str,
        district: str,
        upazila: str,
        union: str,
        village: str,
    ) -> list[Person]:
        """Generate a male-headed household with spouse, children, and optional extended family."""
        persons: list[Person] = []
        used_given_names: set[str] = set()

        head_age = int(self.rng.integers(28, 66))
        head_birth_year = self.reference_year - head_age

        # Check if an elderly father of the head lives in the household
        # Only feasible if hh_size >= 3 and head_age <= 55 (so father is ~70-85)
        has_elderly_father = False
        elderly_father_person: Optional[Person] = None

        # Number of additional members beyond head and spouse
        extra_count = hh_size - 2

        if extra_count >= 3 and self.rng.random() < 0.20 and head_age <= 55:
            has_elderly_father = True
            ef_age = head_age + int(self.rng.integers(18, 30))
            ef_birth_year = self.reference_year - ef_age
            ef_f_given, ef_father_name = self._sample_full_name("M", religion)
            ef_given, ef_surname = self._sample_distinct_given_name(
                "M", religion, used_given_names, forbidden_names={ef_f_given}, hh_id=hh_id
            )
            ef_id = self._next_person_id()
            _, ef_spouse_name = self._sample_full_name("F", religion)

            elderly_father_person = Person(
                person_id=ef_id,
                household_id=hh_id,
                given_name=ef_given,
                surname_or_title=ef_surname,
                sex="M",
                religion_group=religion,
                birth_year=ef_birth_year,
                age_at_reference_date=ef_age,
                marital_status="widowed",
                role_in_household="parent",
                father_id=None,
                mother_id=None,
                spouse_id=None,
                father_name=ef_father_name,
                father_given_name=ef_f_given,
                spouse_name=ef_spouse_name,
                guardian_type="father",
                guardian_name=ef_father_name,
                phone=self._assign_phone("M", ef_age),
                village=village,
                union=union,
                upazila=upazila,
                district=district,
            )
            extra_count -= 1

        # Check if an elderly mother of the head lives in the household
        elderly_mother_person: Optional[Person] = None
        if (
            not has_elderly_father
            and extra_count >= 2
            and self.rng.random() < 0.25
            and head_age <= 55
        ):
            em_age = head_age + int(self.rng.integers(18, 28))
            em_birth_year = self.reference_year - em_age
            em_given, em_surname = self._sample_distinct_given_name(
                "F", religion, used_given_names, hh_id=hh_id
            )
            em_id = self._next_person_id()
            em_f_given, em_father_name = self._sample_full_name("M", religion)
            _, em_spouse_name = self._sample_full_name("M", religion)

            elderly_mother_person = Person(
                person_id=em_id,
                household_id=hh_id,
                given_name=em_given,
                surname_or_title=em_surname,
                sex="F",
                religion_group=religion,
                birth_year=em_birth_year,
                age_at_reference_date=em_age,
                marital_status="widowed",
                role_in_household="parent",
                father_id=None,
                mother_id=None,
                spouse_id=None,
                father_name=em_father_name,
                father_given_name=em_f_given,
                spouse_name=em_spouse_name,
                guardian_type="husband",
                guardian_name=em_spouse_name,
                phone=self._assign_phone("F", em_age),
                village=village,
                union=union,
                upazila=upazila,
                district=district,
            )
            extra_count -= 1

        # Head's father/mother references
        if elderly_father_person is not None:
            head_father_id = elderly_father_person.person_id
            head_father_name = elderly_father_person.full_name
            head_father_given = elderly_father_person.given_name
        else:
            head_father_id = None
            head_father_given, head_father_name = self._sample_full_name("M", religion)

        if elderly_mother_person is not None:
            head_mother_id = elderly_mother_person.person_id
        else:
            head_mother_id = None

        # 1. Head (Male)
        head_given, head_surname = self._sample_distinct_given_name(
            "M", religion, used_given_names, forbidden_names={head_father_given}, hh_id=hh_id
        )
        head_id = self._next_person_id()

        # 2. Spouse (Female)
        spouse_age = max(18, head_age - int(self.rng.integers(1, 8)))
        spouse_birth_year = self.reference_year - spouse_age
        spouse_given, spouse_surname = self._sample_distinct_given_name(
            "F", religion, used_given_names, hh_id=hh_id
        )
        spouse_id = self._next_person_id()
        spouse_f_given, spouse_father_name = self._sample_full_name("M", religion)

        head_full_name = f"{head_given} {head_surname}"
        spouse_full_name = f"{spouse_given} {spouse_surname}"

        # Build Head person record
        head_person = Person(
            person_id=head_id,
            household_id=hh_id,
            given_name=head_given,
            surname_or_title=head_surname,
            sex="M",
            religion_group=religion,
            birth_year=head_birth_year,
            age_at_reference_date=head_age,
            marital_status="married",
            role_in_household="head",
            father_id=head_father_id,
            mother_id=head_mother_id,
            spouse_id=spouse_id,
            father_name=head_father_name,
            father_given_name=head_father_given,
            spouse_name=spouse_full_name,
            guardian_type="father",
            guardian_name=head_father_name,
            phone=self._assign_phone("M", head_age),
            village=village,
            union=union,
            upazila=upazila,
            district=district,
        )

        # Build Spouse person record
        spouse_person = Person(
            person_id=spouse_id,
            household_id=hh_id,
            given_name=spouse_given,
            surname_or_title=spouse_surname,
            sex="F",
            religion_group=religion,
            birth_year=spouse_birth_year,
            age_at_reference_date=spouse_age,
            marital_status="married",
            role_in_household="spouse",
            father_id=None,
            mother_id=None,
            spouse_id=head_id,
            father_name=spouse_father_name,
            father_given_name=spouse_f_given,
            spouse_name=head_full_name,
            guardian_type="husband",
            guardian_name=head_full_name,
            phone=self._assign_phone("F", spouse_age),
            village=village,
            union=union,
            upazila=upazila,
            district=district,
        )

        persons.append(head_person)
        persons.append(spouse_person)

        if elderly_father_person is not None:
            persons.append(elderly_father_person)
        if elderly_mother_person is not None:
            persons.append(elderly_mother_person)

        # Remaining extra_count are children (or adult child + daughter-in-law)
        max_child_age = min(head_age - 18, spouse_age - 16)
        max_child_age = max(1, max_child_age)

        # Generate child ages in descending order with spacing
        child_ages: list[int] = []
        cur_age = max_child_age
        for _ in range(extra_count):
            cur_age = max(0, cur_age - int(self.rng.integers(1, 5)))
            child_ages.append(cur_age)

        # Check if eldest child can be married son with daughter-in-law
        has_daughter_in_law = False
        if extra_count >= 2 and child_ages[0] >= 20 and self.rng.random() < 0.25:
            has_daughter_in_law = True

        if has_daughter_in_law:
            # Eldest child is adult married son
            son_age = child_ages[0]
            son_birth_year = self.reference_year - son_age
            son_given, son_surname = self._sample_distinct_given_name(
                "M", religion, used_given_names, forbidden_names={head_given}, hh_id=hh_id
            )
            son_id = self._next_person_id()

            # Daughter-in-law
            dil_age = max(18, son_age - int(self.rng.integers(1, 6)))
            dil_birth_year = self.reference_year - dil_age
            dil_given, dil_surname = self._sample_distinct_given_name(
                "F", religion, used_given_names, hh_id=hh_id
            )
            dil_id = self._next_person_id()
            dil_f_given, dil_father_name = self._sample_full_name("M", religion)

            son_full_name = f"{son_given} {son_surname}"
            dil_full_name = f"{dil_given} {dil_surname}"

            son_person = Person(
                person_id=son_id,
                household_id=hh_id,
                given_name=son_given,
                surname_or_title=son_surname,
                sex="M",
                religion_group=religion,
                birth_year=son_birth_year,
                age_at_reference_date=son_age,
                marital_status="married",
                role_in_household="child",
                father_id=head_id,
                mother_id=spouse_id,
                spouse_id=dil_id,
                father_name=head_full_name,
                father_given_name=head_given,
                spouse_name=dil_full_name,
                guardian_type="father",
                guardian_name=head_full_name,
                phone=self._assign_phone("M", son_age),
                village=village,
                union=union,
                upazila=upazila,
                district=district,
            )

            dil_person = Person(
                person_id=dil_id,
                household_id=hh_id,
                given_name=dil_given,
                surname_or_title=dil_surname,
                sex="F",
                religion_group=religion,
                birth_year=dil_birth_year,
                age_at_reference_date=dil_age,
                marital_status="married",
                role_in_household="daughter_in_law",
                father_id=None,
                mother_id=None,
                spouse_id=son_id,
                father_name=dil_father_name,
                father_given_name=dil_f_given,
                spouse_name=son_full_name,
                guardian_type="husband",
                guardian_name=son_full_name,
                phone=self._assign_phone("F", dil_age),
                village=village,
                union=union,
                upazila=upazila,
                district=district,
            )

            persons.append(son_person)
            persons.append(dil_person)

            # Remaining children (start from index 2, since index 0 is son,
            # index 1 was reserved for dil)
            for c_age in child_ages[2:]:
                c_sex = "F" if self.rng.random() < 0.50 else "M"
                c_birth_year = self.reference_year - c_age
                c_given, c_surname = self._sample_distinct_given_name(
                    c_sex, religion, used_given_names, forbidden_names={head_given}, hh_id=hh_id
                )
                c_id = self._next_person_id()

                child_person = Person(
                    person_id=c_id,
                    household_id=hh_id,
                    given_name=c_given,
                    surname_or_title=c_surname,
                    sex=c_sex,
                    religion_group=religion,
                    birth_year=c_birth_year,
                    age_at_reference_date=c_age,
                    marital_status="unmarried",
                    role_in_household="child",
                    father_id=head_id,
                    mother_id=spouse_id,
                    spouse_id=None,
                    father_name=head_full_name,
                    father_given_name=head_given,
                    spouse_name=None,
                    guardian_type="father",
                    guardian_name=head_full_name,
                    phone=self._assign_phone(c_sex, c_age),
                    village=village,
                    union=union,
                    upazila=upazila,
                    district=district,
                )
                persons.append(child_person)
        else:
            # All remaining extra members are unmarried children of head & spouse
            for c_age in child_ages:
                c_sex = "F" if self.rng.random() < 0.50 else "M"
                c_birth_year = self.reference_year - c_age
                c_given, c_surname = self._sample_distinct_given_name(
                    c_sex, religion, used_given_names, forbidden_names={head_given}, hh_id=hh_id
                )
                c_id = self._next_person_id()

                child_person = Person(
                    person_id=c_id,
                    household_id=hh_id,
                    given_name=c_given,
                    surname_or_title=c_surname,
                    sex=c_sex,
                    religion_group=religion,
                    birth_year=c_birth_year,
                    age_at_reference_date=c_age,
                    marital_status="unmarried",
                    role_in_household="child",
                    father_id=head_id,
                    mother_id=spouse_id,
                    spouse_id=None,
                    father_name=head_full_name,
                    father_given_name=head_given,
                    spouse_name=None,
                    guardian_type="father",
                    guardian_name=head_full_name,
                    phone=self._assign_phone(c_sex, c_age),
                    village=village,
                    union=union,
                    upazila=upazila,
                    district=district,
                )
                persons.append(child_person)

        return persons

    def _generate_female_headed_household(
        self,
        hh_id: str,
        hh_size: int,
        religion: str,
        district: str,
        upazila: str,
        union: str,
        village: str,
    ) -> list[Person]:
        """Generate a female-headed household (widowed or separated) and her children."""
        persons: list[Person] = []
        used_given_names: set[str] = set()

        # 1. Female Head (widowed or separated)
        head_age = int(self.rng.integers(34, 71))
        head_birth_year = self.reference_year - head_age

        marital_status = "widowed" if self.rng.random() < 0.75 else "separated"
        husband_given, late_husband_name = self._sample_full_name("M", religion)

        extra_count = hh_size - 1

        # Check if head's elderly father lives in the household
        elderly_father_person: Optional[Person] = None
        if extra_count >= 2 and head_age <= 55 and self.rng.random() < 0.15:
            ef_age = head_age + int(self.rng.integers(18, 30))
            ef_birth_year = self.reference_year - ef_age
            ef_f_given, ef_father_name = self._sample_full_name("M", religion)
            ef_given, ef_surname = self._sample_distinct_given_name(
                "M",
                religion,
                used_given_names,
                forbidden_names={husband_given, ef_f_given},
                hh_id=hh_id,
            )
            ef_id = self._next_person_id()
            _, ef_spouse_name = self._sample_full_name("F", religion)

            elderly_father_person = Person(
                person_id=ef_id,
                household_id=hh_id,
                given_name=ef_given,
                surname_or_title=ef_surname,
                sex="M",
                religion_group=religion,
                birth_year=ef_birth_year,
                age_at_reference_date=ef_age,
                marital_status="widowed",
                role_in_household="parent",
                father_id=None,
                mother_id=None,
                spouse_id=None,
                father_name=ef_father_name,
                father_given_name=ef_f_given,
                spouse_name=ef_spouse_name,
                guardian_type="father",
                guardian_name=ef_father_name,
                phone=self._assign_phone("M", ef_age),
                village=village,
                union=union,
                upazila=upazila,
                district=district,
            )
            extra_count -= 1

        if elderly_father_person is not None:
            head_father_id = elderly_father_person.person_id
            head_father_name = elderly_father_person.full_name
            head_father_given = elderly_father_person.given_name
        else:
            head_father_id = None
            head_father_given, head_father_name = self._sample_full_name("M", religion)

        head_given, head_surname = self._sample_distinct_given_name(
            "F", religion, used_given_names, hh_id=hh_id
        )
        head_id = self._next_person_id()

        head_person = Person(
            person_id=head_id,
            household_id=hh_id,
            given_name=head_given,
            surname_or_title=head_surname,
            sex="F",
            religion_group=religion,
            birth_year=head_birth_year,
            age_at_reference_date=head_age,
            marital_status=marital_status,
            role_in_household="head",
            father_id=head_father_id,
            mother_id=None,
            spouse_id=None,  # Late or absent husband
            father_name=head_father_name,
            father_given_name=head_father_given,
            spouse_name=late_husband_name,
            guardian_type="husband",
            guardian_name=late_husband_name,
            phone=self._assign_phone("F", head_age),
            village=village,
            union=union,
            upazila=upazila,
            district=district,
        )

        persons.append(head_person)
        if elderly_father_person is not None:
            persons.append(elderly_father_person)

        # Children of the female head
        max_child_age = max(1, head_age - 16)
        child_ages: list[int] = []
        cur_age = max_child_age
        for _ in range(extra_count):
            cur_age = max(0, cur_age - int(self.rng.integers(1, 5)))
            child_ages.append(cur_age)

        for c_age in child_ages:
            c_sex = "F" if self.rng.random() < 0.50 else "M"
            c_birth_year = self.reference_year - c_age
            c_given, c_surname = self._sample_distinct_given_name(
                c_sex, religion, used_given_names, forbidden_names={husband_given}, hh_id=hh_id
            )
            c_id = self._next_person_id()

            child_person = Person(
                person_id=c_id,
                household_id=hh_id,
                given_name=c_given,
                surname_or_title=c_surname,
                sex=c_sex,
                religion_group=religion,
                birth_year=c_birth_year,
                age_at_reference_date=c_age,
                marital_status="unmarried",
                role_in_household="child",
                father_id=None,  # Father absent/deceased
                mother_id=head_id,
                spouse_id=None,
                # In female-headed households, children's father_name is identical
                # to head.spouse_name
                father_name=late_husband_name,
                father_given_name=husband_given,
                spouse_name=None,
                guardian_type="father",
                guardian_name=late_husband_name,
                phone=self._assign_phone(c_sex, c_age),
                village=village,
                union=union,
                upazila=upazila,
                district=district,
            )
            persons.append(child_person)

        return persons


def generate_population(
    config_path: str | Path,
    output_dir: str | Path,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Run population generation from config and write parquet, csv, and manifest files.

    Args:
        config_path: Path to configuration YAML.
        output_dir: Directory where outputs will be stored.

    Returns:
        Tuple of (persons_df, households_df, manifest_dict).
    """
    config_path = Path(config_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    gen = PopulationGenerator(config)
    persons_df, households_df = gen.generate()

    # Write Parquet files
    persons_parquet_path = output_dir / "persons.parquet"
    households_parquet_path = output_dir / "households.parquet"
    persons_df.to_parquet(persons_parquet_path, engine="pyarrow", index=False)
    households_df.to_parquet(households_parquet_path, engine="pyarrow", index=False)

    # Write CSV files for easy inspection
    persons_csv_path = output_dir / "persons.csv"
    households_csv_path = output_dir / "households.csv"
    persons_df.to_csv(persons_csv_path, index=False)
    households_df.to_csv(households_csv_path, index=False)

    # Write manifest.json
    manifest: dict[str, Any] = {
        "seed": config.get("seed", 42),
        "package_version": __version__,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "row_counts": {
            "persons": len(persons_df),
            "households": len(households_df),
        },
        "config": config,
    }

    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return persons_df, households_df, manifest
