"""Transliteration variant engine for Bangladeshi romanised names.

Rule-based romanisation drift applied per token.
Strictly partitioned into SHARED_RULES and GENERATOR_ONLY_RULES to prevent
normalisation leakage in downstream linkage models.
"""

import re
from dataclasses import dataclass
from typing import Final, Optional

import numpy as np


@dataclass(frozen=True)
class TransliterationRule:
    """A single transliteration variant rule."""

    rule_id: str
    description: str
    pattern: str  # Regex or substring
    replacement: str  # Alternative spelling
    is_generator_only: bool
    is_regex: bool = False
    is_compound: bool = False


# ==============================================================================
# Shared Rules (eligible for future normalisation module import)
# ==============================================================================
SHARED_RULES: Final[list[TransliterationRule]] = [
    TransliterationRule(
        rule_id="R_SHARED_SH_S",
        description="sh <-> s alternation (e.g. Shahida <-> Sahida)",
        pattern=r"(?i)\bsh",
        replacement="s",
        is_generator_only=False,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_SHARED_S_SH",
        description="s <-> sh alternation (e.g. Salma <-> Shalma)",
        pattern=r"(?i)\bs(?=[aeiou])",
        replacement="sh",
        is_generator_only=False,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_SHARED_KH_K",
        description="kh <-> k alternation (e.g. Kashem <-> Khashem)",
        pattern=r"(?i)\bkh",
        replacement="k",
        is_generator_only=False,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_SHARED_PH_F",
        description="ph <-> f alternation (e.g. Faruk <-> Pharuk)",
        pattern=r"(?i)\bf",
        replacement="ph",
        is_generator_only=False,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_SHARED_J_Z",
        description="j <-> z alternation (e.g. Jannat <-> Zannat)",
        pattern=r"(?i)\bj",
        replacement="z",
        is_generator_only=False,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_SHARED_V_B",
        description="v <-> b alternation (e.g. Parvin <-> Parbin)",
        pattern=r"(?i)v",
        replacement="b",
        is_generator_only=False,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_SHARED_EE_I",
        description="i <-> ee alternation (e.g. Rina <-> Reena)",
        pattern=r"(?i)i",
        replacement="ee",
        is_generator_only=False,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_SHARED_U_OO",
        description="u <-> oo alternation (e.g. Khatun <-> Khatoon)",
        pattern=r"(?i)u",
        replacement="oo",
        is_generator_only=False,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_SHARED_E_I",
        description="e <-> i alternation (e.g. Fatema <-> Fatima)",
        pattern=r"(?i)e",
        replacement="i",
        is_generator_only=False,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_SHARED_RAHMAN",
        description="Rahman <-> Rehman alternation",
        pattern=r"(?i)\bRahman\b",
        replacement="Rehman",
        is_generator_only=False,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_SHARED_MOHAMMAD_MUHAMMAD",
        description="Mohammad <-> Muhammad alternation",
        pattern=r"(?i)\bMohammad\b",
        replacement="Muhammad",
        is_generator_only=False,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_SHARED_MOHAMMAD_MOHAMMED",
        description="Mohammad <-> Mohammed alternation",
        pattern=r"(?i)\bMohammad\b",
        replacement="Mohammed",
        is_generator_only=False,
        is_regex=True,
    ),
]

# ==============================================================================
# Generator-Only Rules (strictly hidden from the normaliser, >= 40% of rules)
# ==============================================================================
GENERATOR_ONLY_RULES: Final[list[TransliterationRule]] = [
    TransliterationRule(
        rule_id="R_GEN_A_O",
        description="a <-> o vowel shift (e.g. Rahima <-> Rohima, Salma <-> Solma)",
        pattern=r"(?i)a",
        replacement="o",
        is_generator_only=True,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_GEN_O_A",
        description="o <-> a vowel shift (e.g. Rokeya <-> Rakeya)",
        pattern=r"(?i)o",
        replacement="a",
        is_generator_only=True,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_GEN_U_O",
        description="u <-> o vowel shift (e.g. Kulsum <-> Kolsum)",
        pattern=r"(?i)u",
        replacement="o",
        is_generator_only=True,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_GEN_UDDIN_UDDEEN",
        description="Uddin <-> Uddeen alternation",
        pattern=r"(?i)\bUddin\b",
        replacement="Uddeen",
        is_generator_only=True,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_GEN_UDDIN_UDIN",
        description="Uddin <-> Udin alternation",
        pattern=r"(?i)\bUddin\b",
        replacement="Udin",
        is_generator_only=True,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_GEN_ALI_OLI",
        description="Ali <-> Oli alternation",
        pattern=r"(?i)\bAli\b",
        replacement="Oli",
        is_generator_only=True,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_GEN_MIA_MIAH",
        description="Mia <-> Miah alternation",
        pattern=r"(?i)\bMia\b",
        replacement="Miah",
        is_generator_only=True,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_GEN_CHOWDHURY_CHOUDHURY",
        description="Chowdhury <-> Choudhury alternation",
        pattern=r"(?i)\bChowdhury\b",
        replacement="Choudhury",
        is_generator_only=True,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_GEN_HOSSAIN_HUSSAIN",
        description="Hossain <-> Hussain alternation",
        pattern=r"(?i)\bHossain\b",
        replacement="Hussain",
        is_generator_only=True,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_GEN_SHEIKH_SHEIK",
        description="Sheikh <-> Sheik alternation",
        pattern=r"(?i)\bSheikh\b",
        replacement="Sheik",
        is_generator_only=True,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_GEN_ALAM_ALEM",
        description="Alam <-> Alem alternation",
        pattern=r"(?i)\bAlam\b",
        replacement="Alem",
        is_generator_only=True,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_GEN_COMPOUND_KARIM_JOIN",
        description="Abdul Karim -> Abdulkarim / Abdul-Karim join",
        pattern=r"(?i)\bAbdul Karim\b",
        replacement="Abdulkarim",
        is_generator_only=True,
        is_compound=True,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_GEN_COMPOUND_KASHEM_JOIN",
        description="Abul Kashem -> Abulkashem / Abul-Kashem join",
        pattern=r"(?i)\bAbul Kashem\b",
        replacement="Abulkashem",
        is_generator_only=True,
        is_compound=True,
        is_regex=True,
    ),
    TransliterationRule(
        rule_id="R_GEN_COMPOUND_ISLAM_JOIN",
        description="Nurul Islam -> Nurulislam / Nurul-Islam join",
        pattern=r"(?i)\bNurul Islam\b",
        replacement="Nurulislam",
        is_generator_only=True,
        is_compound=True,
        is_regex=True,
    ),
]

ALL_RULES: Final[list[TransliterationRule]] = SHARED_RULES + GENERATOR_ONLY_RULES


def get_rule_counts() -> tuple[int, int, float]:
    """Return (shared_count, generator_only_count, generator_only_ratio)."""
    n_shared = len(SHARED_RULES)
    n_gen = len(GENERATOR_ONLY_RULES)
    total = n_shared + n_gen
    ratio = n_gen / total if total > 0 else 0.0
    return n_shared, n_gen, ratio


def apply_transliteration_variant(
    text: str, rng: np.random.Generator
) -> tuple[str, Optional[TransliterationRule]]:
    """Apply a single random matching transliteration rule to text.

    Returns:
        (transformed_text, applied_rule_or_None)
    """
    if not text:
        return text, None

    applicable_rules: list[tuple[TransliterationRule, str]] = []

    for rule in ALL_RULES:
        if rule.is_regex:
            if re.search(rule.pattern, text):
                # If compound join, also optionally test hyphenation variant
                if rule.is_compound and rng.random() < 0.50:
                    hyphen_rep = (
                        rule.replacement.replace("karim", "-Karim")
                        .replace("kashem", "-Kashem")
                        .replace("islam", "-Islam")
                    )
                    new_val = re.sub(rule.pattern, hyphen_rep, text, count=1)
                else:
                    new_val = re.sub(rule.pattern, rule.replacement, text, count=1)
                if new_val != text:
                    applicable_rules.append((rule, new_val))
        else:
            if rule.pattern in text:
                new_val = text.replace(rule.pattern, rule.replacement, 1)
                if new_val != text:
                    applicable_rules.append((rule, new_val))

    if not applicable_rules:
        return text, None

    idx = int(rng.choice(len(applicable_rules)))
    rule, new_text = applicable_rules[idx]
    return new_text, rule
