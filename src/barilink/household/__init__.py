"""Kinship-aware household inference and direct/indirect reach estimation.

Strict segregation: This package processes only model-visible inputs
(clusters.parquet, records.parquet, features.parquet, rosters.parquet).
Zero references to ground-truth files or directories are permitted.
"""

from __future__ import annotations

from barilink.household.evidence import (
    build_household_evidence,
    build_unit_profiles,
)
from barilink.household.golden import (
    build_household_golden_records,
)
from barilink.household.infer import (
    infer_households,
)

__all__ = [
    "build_household_evidence",
    "build_household_golden_records",
    "build_unit_profiles",
    "infer_households",
]

