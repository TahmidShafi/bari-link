"""Feature normalisation and transformation pipeline for bari-link.

Prepares raw registry records and household rosters for probabilistic linkage in Splink.
Reads only model-visible inputs from registry/ and writes features.parquet.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional, Sequence

import pandas as pd

# Honorific prefixes and title words stripped from start of names
HONORIFIC_PREFIXES: frozenset[str] = frozenset(
    {"md", "mohammad", "mohd", "mst", "most", "mosammat", "late"}
)

# Trailing female titles extracted to title_token
FEMALE_TITLES: dict[str, str] = {
    "khatun": "khatun",
    "khatoon": "khatun",
    "begum": "begum",
    "akter": "akter",
    "bibi": "bibi",
    "rani": "rani",
    "bala": "bala",
}

# Multi-character replacements applied before single-character replacements
MULTI_CHAR_REPLACEMENTS: Sequence[tuple[str, str]] = [
    (r"\brehman\b", "rahman"),
    (r"\bmuhammad\b", "mohammad"),
    (r"\bmohammed\b", "mohammad"),
    ("oo", "u"),
    ("ee", "i"),
    ("ph", "f"),
    ("kh", "k"),
    ("sh", "s"),
]

# Single-character replacements applied after multi-character replacements
SINGLE_CHAR_REPLACEMENTS: Sequence[tuple[str, str]] = [
    ("o", "a"),
    ("e", "i"),
    ("z", "j"),
    ("v", "b"),
]


def clean_text_basic(val: Any) -> str:
    """Basic string cleanup: lowercase, strip punctuation, remove honorific prefixes."""
    if val is None or pd.isna(val):
        return ""
    text = str(val).strip().lower()
    # Replace punctuation and hyphens with spaces
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = text.split()

    # Strip leading honorific prefixes iteratively
    while tokens and tokens[0] in HONORIFIC_PREFIXES:
        tokens.pop(0)

    return " ".join(tokens)


def extract_title_token(clean_name: str) -> tuple[str, Optional[str]]:
    """Extract trailing female title token and return (trimmed_name, title_token)."""
    if not clean_name:
        return "", None

    tokens = clean_name.split()
    if not tokens:
        return "", None

    last_token = tokens[-1]
    if last_token in FEMALE_TITLES:
        canonical_title = FEMALE_TITLES[last_token]
        trimmed_name = " ".join(tokens[:-1])
        return trimmed_name, canonical_title

    return clean_name, None


def canonicalise_name(clean_str: str) -> str:
    """Apply canonicalisation rules in strict order: multi-char, single-char, remove spaces."""
    if not clean_str:
        return ""

    text = clean_str.lower()

    # 1. Multi-character replacements
    for pattern, replacement in MULTI_CHAR_REPLACEMENTS:
        if pattern.startswith(r"\b"):
            text = re.sub(pattern, replacement, text)
        else:
            text = text.replace(pattern, replacement)

    # 2. Single-character replacements
    for pattern, replacement in SINGLE_CHAR_REPLACEMENTS:
        text = text.replace(pattern, replacement)

    # 3. Remove spaces and hyphens
    text = re.sub(r"[\s\-]+", "", text)
    return text


def compute_skeleton(canon_str: Optional[str]) -> Optional[str]:
    """Compute consonant skeleton: keep 1st letter, drop vowels, collapse dupes."""
    if canon_str is None or pd.isna(canon_str):
        return None
    text = str(canon_str).strip()
    if not text:
        return None

    # Keep first letter
    first_char = text[0]
    out_chars = [first_char]

    vowels = {"a", "e", "i", "o", "u"}
    for ch in text[1:]:
        if ch in vowels:
            continue
        if ch == out_chars[-1]:
            continue
        out_chars.append(ch)

    return "".join(out_chars)


def compute_given_first_skel(name_clean: Optional[str]) -> Optional[str]:
    """Compute skeleton of the first token of name_clean."""
    if name_clean is None or pd.isna(name_clean):
        return None
    tokens = str(name_clean).split()
    if not tokens:
        return None
    first_canon = canonicalise_name(tokens[0])
    return compute_skeleton(first_canon)


def compute_name_tokens_sorted(name_clean: Optional[str]) -> Optional[str]:
    """Sort canonical tokens alphabetically and concatenate without spaces (Amendment 4)."""
    if name_clean is None or pd.isna(name_clean):
        return None
    tokens = str(name_clean).split()
    if not tokens:
        return None
    canon_tokens = [canonicalise_name(t) for t in tokens if t]
    canon_tokens.sort()
    return "".join(canon_tokens) if canon_tokens else None


def normalise_phone_11(val: Any) -> tuple[Optional[str], Optional[str]]:
    """Normalise Bangladeshi phone number to 11 digits (01XXXXXXXXX) and extract last 8 digits."""
    if val is None or pd.isna(val):
        return None, None
    digits = re.sub(r"\D", "", str(val))
    if digits.startswith("880"):
        digits = digits[2:]
    elif digits.startswith("1") and len(digits) == 10:
        digits = "0" + digits

    if len(digits) == 11 and digits.startswith("01"):
        return digits, digits[-8:]
    return None, None


def canonicalise_village(val: Any) -> Optional[str]:
    """Clean and canonicalise village name, removing internal spaces."""
    if val is None or pd.isna(val):
        return None
    clean = clean_text_basic(val)
    if not clean:
        return None
    canon = canonicalise_name(clean)
    return canon if canon else None


def build_features(
    records_df: pd.DataFrame,
    rosters_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Build feature table for Splink from raw records and rosters."""
    features = pd.DataFrame()
    features["record_id"] = records_df["record_id"].astype(str)

    # Clean text and extract title
    raw_names = records_df.get("full_name_raw", pd.Series("", index=records_df.index))
    cleaned_names = [clean_text_basic(n) for n in raw_names]
    name_and_titles = [extract_title_token(n) for n in cleaned_names]

    name_clean_series = [nt[0] for nt in name_and_titles]
    title_series = [nt[1] for nt in name_and_titles]

    features["name_clean"] = name_clean_series
    features["title_token"] = title_series
    features["name_canon"] = [canonicalise_name(n) if n else None for n in name_clean_series]
    features["name_skeleton"] = [compute_skeleton(c) for c in features["name_canon"]]
    features["given_first_skel"] = [compute_given_first_skel(n) for n in name_clean_series]
    features["name_tokens_sorted"] = [compute_name_tokens_sorted(n) for n in name_clean_series]

    # Guardian name
    raw_guardians = records_df.get("guardian_name_raw", pd.Series("", index=records_df.index))
    guard_clean = [clean_text_basic(g) for g in raw_guardians]
    features["guardian_clean"] = guard_clean
    features["guardian_canon"] = [canonicalise_name(g) if g else None for g in guard_clean]
    features["guardian_skeleton"] = [compute_skeleton(c) for c in features["guardian_canon"]]

    # Phone
    phone_s = records_df.get("phone_raw", pd.Series(None, index=records_df.index))
    phones = [normalise_phone_11(p) for p in phone_s]
    features["phone_norm"] = [p[0] for p in phones]
    features["phone_last8"] = [p[1] for p in phones]

    # Birth year estimated
    enrolment_dates = pd.to_datetime(records_df["enrolment_date"], errors="coerce")
    enrolment_years = enrolment_dates.dt.year
    raw_ages = pd.to_numeric(records_df.get("age_raw"), errors="coerce")
    birth_years = (enrolment_years - raw_ages.round()).astype("Int64")
    features["birth_year_est"] = birth_years

    # Village canon
    raw_villages = records_df.get("village_raw", pd.Series(None, index=records_df.index))
    features["village_canon"] = [canonicalise_village(v) for v in raw_villages]

    # Preserved raw metadata fields
    features["union_raw"] = records_df.get("union_raw", pd.Series(None, index=records_df.index))
    features["sex_raw"] = records_df.get("sex_raw", pd.Series(None, index=records_df.index))
    features["source_module"] = records_df.get(
        "source_module", pd.Series(None, index=records_df.index)
    )
    features["enrolment_date"] = records_df.get(
        "enrolment_date", pd.Series(None, index=records_df.index)
    )

    # Kinship: roster_skels (Amendment 1)
    if rosters_df is not None and not rosters_df.empty:
        # Compute member skeleton
        m_names = [clean_text_basic(m) for m in rosters_df["member_name_raw"]]
        m_canons = [canonicalise_name(m) for m in m_names]
        m_skels = [compute_skeleton(c) for c in m_canons]

        roster_work = pd.DataFrame(
            {
                "record_id": rosters_df["record_id"].astype(str),
                "skel": m_skels,
            }
        ).dropna(subset=["skel"])

        # Group by record_id to list of unique skeletons
        grouped = roster_work.groupby("record_id")["skel"].apply(lambda s: sorted(set(s))).to_dict()
        features["roster_skels"] = features["record_id"].map(grouped)
    else:
        features["roster_skels"] = None

    return features


def export_features(
    run_name: str,
    base_data_dir: str = "data/generated",
) -> pd.DataFrame:
    """Read registry records and rosters, compute features, and write features.parquet."""
    reg_dir = Path(base_data_dir) / run_name / "registry"
    records_path = reg_dir / "records.parquet"
    rosters_path = reg_dir / "rosters.parquet"
    out_path = reg_dir / "features.parquet"

    if not records_path.exists():
        raise FileNotFoundError(f"Records parquet not found at {records_path}")

    records_df = pd.read_parquet(records_path)
    rosters_df = pd.read_parquet(rosters_path) if rosters_path.exists() else None

    features_df = build_features(records_df, rosters_df)
    features_df.to_parquet(out_path, engine="pyarrow", index=False)
    return features_df
