"""Non-ML baseline record linkage methods."""

from barilink.baselines.exact import run_exact_baseline
from barilink.baselines.phone import run_exact_or_phone_baseline, run_phone_baseline

__all__ = [
    "run_exact_baseline",
    "run_phone_baseline",
    "run_exact_or_phone_baseline",
]

