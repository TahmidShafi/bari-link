"""Field-level probabilistic corruption models for rural administrative records.

Simulates field survey noise including transliteration, prefix drift,
title drift, Damerau-Levenshtein typos, age heaping, guardian switching,
phone mutations, location drift, and missingness.
"""

from dataclasses import dataclass
from typing import Any, Final, Optional

import numpy as np

from barilink.corrupt.transliteration import apply_transliteration_variant
from barilink.generate.name_pools import (
    FEMALE_PREFIXES,
    MALE_PREFIXES,
    SURNAMES_MUSLIM_FEMALE,
)

# QWERTY adjacent key map for Damerau-Levenshtein substitutions and insertions
QWERTY_ADJACENT: Final[dict[str, list[str]]] = {
    "a": ["q", "w", "s", "z"],
    "b": ["v", "g", "h", "n"],
    "c": ["x", "d", "f", "v"],
    "d": ["s", "e", "r", "f", "c", "x"],
    "e": ["w", "s", "d", "r"],
    "f": ["d", "r", "t", "g", "v", "c"],
    "g": ["f", "t", "y", "h", "b", "v"],
    "h": ["g", "y", "u", "j", "n", "b"],
    "i": ["u", "j", "k", "o"],
    "j": ["h", "u", "i", "k", "m", "n"],
    "k": ["j", "i", "o", "l", "m"],
    "l": ["k", "o", "p"],
    "m": ["n", "j", "k"],
    "n": ["b", "h", "j", "m"],
    "o": ["i", "k", "l", "p"],
    "p": ["o", "l"],
    "q": ["w", "a"],
    "r": ["e", "d", "f", "t"],
    "s": ["a", "w", "e", "d", "x", "z"],
    "t": ["r", "f", "g", "y"],
    "u": ["y", "h", "j", "i"],
    "v": ["c", "f", "g", "b"],
    "w": ["q", "a", "s", "e"],
    "x": ["z", "s", "d", "c"],
    "y": ["t", "g", "h", "u"],
    "z": ["a", "s", "x"],
}


@dataclass
class CorruptionEvent:
    """Audit record for a single applied corruption."""

    record_id: str
    field: str
    corruption_type: str
    rule_id: Optional[str]
    is_generator_only: bool
    before: str
    after: str


class FieldCorruptor:
    """Probabilistic corruption engine configured per module."""

    def __init__(self, config: dict[str, Any], rng: np.random.Generator) -> None:
        self.config = config
        self.rng = rng

        corrupt_cfg = config.get("corruption", {})
        self.base_rates = corrupt_cfg.get("rates", {})
        self.missingness_cfg = config.get("missingness", {})

        # Track audit events
        self.events: list[CorruptionEvent] = []

    def _effective_rate(self, rate_key: str, intensity: float) -> float:
        """Calculate module-specific effective corruption rate."""
        base = float(self.base_rates.get(rate_key, 0.0))
        return min(1.0, base * intensity)

    def log_event(
        self,
        record_id: str,
        field: str,
        corruption_type: str,
        before: Any,
        after: Any,
        rule_id: Optional[str] = None,
        is_generator_only: bool = False,
    ) -> None:
        """Record an applied corruption event into the audit trail."""
        self.events.append(
            CorruptionEvent(
                record_id=record_id,
                field=field,
                corruption_type=corruption_type,
                rule_id=rule_id,
                is_generator_only=is_generator_only,
                before=str(before) if before is not None else "",
                after=str(after) if after is not None else "",
            )
        )

    # --------------------------------------------------------------------------
    # a) Transliteration
    # --------------------------------------------------------------------------
    def corrupt_transliteration(
        self, text: str, record_id: str, field_name: str, intensity: float
    ) -> str:
        """Apply transliteration drift with rule tracking."""
        rate = self._effective_rate("transliteration", intensity)
        if self.rng.random() >= rate:
            return text

        new_text, rule = apply_transliteration_variant(text, self.rng)
        if rule is not None and new_text != text:
            corr_type = (
                "transliteration_generator_only"
                if rule.is_generator_only
                else "transliteration_shared"
            )
            self.log_event(
                record_id=record_id,
                field=field_name,
                corruption_type=corr_type,
                before=text,
                after=new_text,
                rule_id=rule.rule_id,
                is_generator_only=rule.is_generator_only,
            )
            return new_text
        return text

    # --------------------------------------------------------------------------
    # b) Prefix Drift
    # --------------------------------------------------------------------------
    def corrupt_prefix(
        self, name: str, sex: str, record_id: str, field_name: str, intensity: float
    ) -> str:
        """Add, drop, or alternate honorific prefixes (Md., Mst., etc.)."""
        rate = self._effective_rate("prefix_drift", intensity)
        if self.rng.random() >= rate:
            return name

        prefixes = FEMALE_PREFIXES if sex == "F" else MALE_PREFIXES
        chosen_prefix = str(self.rng.choice(prefixes))

        # Check if already starts with a prefix
        for p in prefixes:
            if name.startswith(p + " "):
                # Drop or alternate
                if self.rng.random() < 0.50:
                    new_name = name[len(p) + 1 :]
                    self.log_event(record_id, field_name, "prefix_drop", name, new_name)
                    return new_name
                else:
                    alt_prefix = str(self.rng.choice([x for x in prefixes if x != p]))
                    new_name = alt_prefix + " " + name[len(p) + 1 :]
                    self.log_event(record_id, field_name, "prefix_alternate", name, new_name)
                    return new_name

        # Prepend prefix
        new_name = f"{chosen_prefix} {name}"
        self.log_event(record_id, field_name, "prefix_add", name, new_name)
        return new_name

    # --------------------------------------------------------------------------
    # c) Female Title Drift
    # --------------------------------------------------------------------------
    def corrupt_female_title(
        self, name: str, sex: str, record_id: str, field_name: str, intensity: float
    ) -> str:
        """Swap or drop common female titles (Khatun, Begum, Akter)."""
        if sex != "F":
            return name

        rate = self._effective_rate("female_title_drift", intensity)
        if self.rng.random() >= rate:
            return name

        tokens = name.split()
        if len(tokens) <= 1:
            return name

        last_token = tokens[-1]
        if last_token in SURNAMES_MUSLIM_FEMALE:
            # 50% drop, 50% swap with another title
            if self.rng.random() < 0.50:
                new_name = " ".join(tokens[:-1])
                self.log_event(record_id, field_name, "female_title_drop", name, new_name)
                return new_name
            else:
                alternatives = [t for t in SURNAMES_MUSLIM_FEMALE if t != last_token]
                new_title = str(self.rng.choice(alternatives))
                new_name = " ".join(tokens[:-1] + [new_title])
                self.log_event(record_id, field_name, "female_title_swap", name, new_name)
                return new_name

        return name

    # --------------------------------------------------------------------------
    # d) Damerau-Levenshtein Typos
    # --------------------------------------------------------------------------
    def corrupt_typos(
        self, text: str, record_id: str, field_name: str, intensity: float
    ) -> str:
        """Inject 1-2 QWERTY-adjacent substitutions, insertions, deletions, or transpositions."""
        if len(text) < 3:
            return text

        rate = self._effective_rate("typo_damerau_levenshtein", intensity)
        if self.rng.random() >= rate:
            return text

        chars = list(text)
        n_edits = 1 if self.rng.random() < 0.75 else 2

        for _ in range(n_edits):
            if len(chars) < 3:
                break
            op = self.rng.choice(["sub", "ins", "del", "trans"])
            pos = int(self.rng.integers(0, len(chars)))
            ch = chars[pos].lower()

            if op == "sub" and ch in QWERTY_ADJACENT:
                adj = self.rng.choice(QWERTY_ADJACENT[ch])
                chars[pos] = adj.upper() if chars[pos].isupper() else adj
            elif op == "ins" and ch in QWERTY_ADJACENT:
                adj = self.rng.choice(QWERTY_ADJACENT[ch])
                chars.insert(pos + 1, adj)
            elif op == "del" and len(chars) > 3 and not chars[pos].isspace():
                chars.pop(pos)
            elif op == "trans" and pos < len(chars) - 1:
                chars[pos], chars[pos + 1] = chars[pos + 1], chars[pos]

        new_text = "".join(chars)
        if new_text != text:
            self.log_event(
                record_id, field_name, "typo_damerau_levenshtein", text, new_text
            )
            return new_text
        return text

    # --------------------------------------------------------------------------
    # e) Field Errors: Title to Front
    # --------------------------------------------------------------------------
    def corrupt_title_to_front(
        self, name: str, record_id: str, field_name: str, intensity: float
    ) -> str:
        """Move surname/title to front (e.g. Abdul Karim Mia -> Mia Abdul Karim)."""
        rate = self._effective_rate("field_title_to_front", intensity)
        if self.rng.random() >= rate:
            return name

        tokens = name.split()
        if len(tokens) >= 2:
            new_name = f"{tokens[-1]} {' '.join(tokens[:-1])}"
            self.log_event(record_id, field_name, "field_title_to_front", name, new_name)
            return new_name
        return name

    # --------------------------------------------------------------------------
    # f) Age Heaping and Jitter
    # --------------------------------------------------------------------------
    def corrupt_age(
        self, clean_age: int, record_id: str, intensity: float
    ) -> int:
        """Apply age heaping (multiples of 5 increasing with age) and small jitter +/- 1-3."""
        base_heap = float(self.base_rates.get("age_heaping_base", 0.25))
        # Probability increases with age
        heap_prob = min(0.65, (base_heap + 0.006 * max(0, clean_age - 20))) * intensity
        heap_prob = min(1.0, heap_prob)

        corrupted = clean_age
        heaped = False

        if self.rng.random() < heap_prob:
            # Round to nearest 5
            corrupted = int(round(clean_age / 5.0) * 5)
            heaped = True
            self.log_event(record_id, "age", "age_heaping", clean_age, corrupted)

        jitter_rate = self._effective_rate("age_jitter", intensity)
        if not heaped and self.rng.random() < jitter_rate:
            delta = int(self.rng.choice([-3, -2, -1, 1, 2, 3]))
            corrupted = max(0, clean_age + delta)
            self.log_event(record_id, "age", "age_jitter", clean_age, corrupted)

        return corrupted

    # --------------------------------------------------------------------------
    # g) Guardian Switch and Widow Late Prefix
    # --------------------------------------------------------------------------
    def corrupt_guardian(
        self,
        guardian_name: str,
        guardian_type: str,
        father_name: str,
        marital_status: str,
        sex: str,
        record_id: str,
        intensity: float,
    ) -> tuple[str, str]:
        """Switch guardian to father for ever-married women, and add 'Late' for widows."""
        curr_name = guardian_name
        curr_type = guardian_type

        # Guardian switch for ever-married women only
        is_ever_married_woman = (
            sex == "F" and marital_status in {"married", "widowed", "separated"}
        )
        if is_ever_married_woman and curr_type == "husband":
            switch_rate = self._effective_rate("guardian_switch_ever_married", intensity)
            if self.rng.random() < switch_rate:
                curr_name = father_name
                curr_type = "father"
                self.log_event(
                    record_id,
                    "guardian_name",
                    "guardian_switch",
                    guardian_name,
                    father_name,
                )

        # Widow 'Late' prefix if guardian is husband
        if marital_status == "widowed" and curr_type == "husband":
            widow_rate = self._effective_rate("widow_late_prefix", intensity)
            if self.rng.random() < widow_rate and not curr_name.startswith("Late "):
                new_gname = f"Late {curr_name}"
                self.log_event(
                    record_id,
                    "guardian_name",
                    "widow_late_prefix",
                    curr_name,
                    new_gname,
                )
                curr_name = new_gname

        return curr_name, curr_type

    # --------------------------------------------------------------------------
    # h) Phone Corruption
    # --------------------------------------------------------------------------
    def corrupt_phone(
        self,
        phone: Optional[str],
        household_phone: Optional[str],
        record_id: str,
        intensity: float,
    ) -> Optional[str]:
        """Corrupt phone number: shared HH phone, new SIM, digit typo, transposition, formatting."""
        # Normalize pandas NaN / float to None or clean string
        is_nan_phone = isinstance(phone, float) and np.isnan(phone)
        if phone is None or is_nan_phone or not str(phone).strip():
            curr_phone = None
        else:
            curr_phone = str(phone).strip()

        is_nan_hh = isinstance(household_phone, float) and np.isnan(household_phone)
        if household_phone is None or is_nan_hh or not str(household_phone).strip():
            hh_phone = None
        else:
            hh_phone = str(household_phone).strip()

        # Missing phone
        if self.rng.random() < self._effective_rate("phone_missing", intensity):
            if curr_phone is not None:
                self.log_event(record_id, "phone", "phone_missing", curr_phone, None)
            return None

        # Replaced with household phone (if different)
        share_rate = self._effective_rate("phone_shared_household", intensity)
        if hh_phone and curr_phone != hh_phone and self.rng.random() < share_rate:
            self.log_event(
                record_id, "phone", "phone_shared_household", curr_phone, hh_phone
            )
            curr_phone = hh_phone

        # New SIM (fresh valid number)
        if self.rng.random() < self._effective_rate("phone_new_sim", intensity):
            op = self.rng.integers(3, 10)
            rest = self.rng.integers(0, 100_000_000)
            new_sim = f"01{op}{rest:08d}"
            self.log_event(record_id, "phone", "phone_new_sim", curr_phone, new_sim)
            curr_phone = new_sim

        if not curr_phone or not isinstance(curr_phone, str):
            return None

        # One-digit typo
        if self.rng.random() < self._effective_rate("phone_digit_typo", intensity):
            p_list = list(curr_phone)
            # Pick a digit position to mutate
            pos = int(self.rng.integers(2, len(p_list)))
            new_digit = str(self.rng.integers(0, 10))
            if new_digit != p_list[pos]:
                before_val = "".join(p_list)
                p_list[pos] = new_digit
                curr_phone = "".join(p_list)
                self.log_event(record_id, "phone", "phone_digit_typo", before_val, curr_phone)

        # Adjacent digit transposition
        if self.rng.random() < self._effective_rate("phone_adjacent_transposition", intensity):
            p_list = list(curr_phone)
            if len(p_list) >= 4:
                pos = int(self.rng.integers(2, len(p_list) - 1))
                if p_list[pos] != p_list[pos + 1]:
                    before_val = "".join(p_list)
                    p_list[pos], p_list[pos + 1] = p_list[pos + 1], p_list[pos]
                    curr_phone = "".join(p_list)
                    self.log_event(
                        record_id, "phone", "phone_adjacent_transposition", before_val, curr_phone
                    )

        # Formatting variant
        if self.rng.random() < self._effective_rate("phone_format_variant", intensity):
            before_val = curr_phone
            fmt = self.rng.choice(["plus_880", "880", "dash", "drop_zero"])
            if fmt == "plus_880" and not curr_phone.startswith("+880"):
                curr_phone = f"+880 {curr_phone[1:]}"
            elif fmt == "880" and not curr_phone.startswith("880"):
                curr_phone = f"880{curr_phone[1:]}"
            elif fmt == "dash" and len(curr_phone) == 11 and "-" not in curr_phone:
                curr_phone = f"{curr_phone[:3]}-{curr_phone[3:7]}-{curr_phone[7:]}"
            elif fmt == "drop_zero" and curr_phone.startswith("0"):
                curr_phone = curr_phone[1:]
            if curr_phone != before_val:
                self.log_event(record_id, "phone", "phone_format_variant", before_val, curr_phone)

        return curr_phone

    # --------------------------------------------------------------------------
    # i) Location Drift
    # --------------------------------------------------------------------------
    def corrupt_location(
        self,
        village: str,
        union: str,
        upazila: str,
        district: str,
        record_id: str,
        intensity: float,
    ) -> tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """Apply village spelling variants and occasional missing administrative tokens."""
        curr_village: Optional[str] = village
        curr_union: Optional[str] = union
        curr_upazila: Optional[str] = upazila
        curr_district: Optional[str] = district

        # Village variants
        if self.rng.random() < self._effective_rate("location_village_drift", intensity):
            before_v = curr_village
            if "Para" in curr_village:
                variants = [
                    curr_village.replace(" ", ""),  # "Uttarpara"
                    curr_village.replace("a", "o"),  # "Uttor Poro"
                    curr_village.replace("Para", "para"),
                ]
                curr_village = str(self.rng.choice(variants))
            elif "Char" in curr_village:
                variants = [
                    curr_village.replace(" ", ""),
                    curr_village.replace("Char", "char"),
                ]
                curr_village = str(self.rng.choice(variants))
            if curr_village != before_v:
                self.log_event(
                    record_id, "village", "location_village_drift", before_v, curr_village
                )

        # Missing administrative divisions
        missing_rate = self._effective_rate("location_missing_admin", intensity)
        if self.rng.random() < missing_rate:
            self.log_event(record_id, "upazila", "missingness", curr_upazila, None)
            curr_upazila = None
        if self.rng.random() < (missing_rate * 0.70):
            self.log_event(record_id, "district", "missingness", curr_district, None)
            curr_district = None

        return curr_village, curr_union, curr_upazila, curr_district

    # --------------------------------------------------------------------------
    # j) Configured Missingness
    # --------------------------------------------------------------------------
    def apply_missingness(
        self, module_name: str, field: str, value: Any, record_id: str
    ) -> Any:
        """Apply configured per-module x per-field missingness.

        Structurally uncollected fields are None and not processed here.
        """
        if value is None:
            return None

        mod_cfg = self.missingness_cfg.get(module_name, {})
        rate = float(mod_cfg.get(field, 0.0))
        if rate > 0 and self.rng.random() < rate:
            self.log_event(record_id, field, "missingness", value, None)
            return None
        return value
