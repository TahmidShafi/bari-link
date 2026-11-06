"""Diagnostics and chart generation for Splink 4 models.

Strictly reads only model-visible files and trained model artifacts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
from splink import DuckDBAPI, Linker


def export_model_diagnostics(
    model_json_path: str | Path,
    output_charts_dir: str | Path,
    features_df: Optional[pd.DataFrame] = None,
) -> tuple[Path, Path]:
    """Generate and save match weights and m/u parameter charts as HTML."""
    model_p = Path(model_json_path)
    if not model_p.exists():
        raise FileNotFoundError(f"Trained model JSON not found at {model_p}")

    out_dir = Path(output_charts_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    db_api = DuckDBAPI()
    if features_df is None:
        # Create minimal dummy dataframe for Linker inspection
        features_df = pd.DataFrame([{
            "record_id": "dummy_0",
            "name_clean": "a",
            "name_canon": "a",
            "name_skeleton": "a",
            "given_first_skel": "a",
            "name_tokens_sorted": "a",
            "title_token": "khatun",
            "guardian_clean": "b",
            "guardian_canon": "b",
            "guardian_skeleton": "b",
            "phone_norm": "01700000000",
            "phone_last8": "00000000",
            "birth_year_est": 1990,
            "village_canon": "c",
            "union_raw": "u",
            "sex_raw": "F",
            "source_module": "m",
            "enrolment_date": "2024-01-01",
            "roster_skels": ["a"],
        }])

    linker = Linker(features_df, str(model_p), db_api)

    # 1. Match weights chart
    weights_path = out_dir / "match_weights.html"
    c_weights = linker.visualisations.match_weights_chart()
    c_weights.save(str(weights_path))

    # 2. M and U parameters chart
    mu_path = out_dir / "m_u_parameters.html"
    c_mu = linker.visualisations.m_u_parameters_chart()
    c_mu.save(str(mu_path))

    return weights_path, mu_path
