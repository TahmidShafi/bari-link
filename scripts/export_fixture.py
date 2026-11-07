"""Export offline test fixtures for Vitest suite in web/src/tests/fixtures/

Regenerates:
1. web/src/tests/fixtures/pairs_sample.json (200 real pairs for waterfall testing)
2. web/src/tests/fixtures/raw_eval_fixture.json (full holdout_5 evaluation fixture)
3. web/src/tests/fixtures/pair_labels_100.json (100 real pairs with Splink-derived comparison labels)
"""

import json
from pathlib import Path

import duckdb
from splink import SettingsCreator


def export_test_fixtures(
    web_data_dir: Path = Path("web/public/data"),
    output_dir: Path = Path("web/src/tests/fixtures"),
    truth_dir: Path = Path("data/generated/holdout_5/truth"),
    model_path: Path = Path("results/models/splink_k/model.json"),
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()

    # 1. 200 real pairs fixture for waterfall decomposition test
    pairs_path = web_data_dir / "pairs.parquet"
    if not pairs_path.exists():
        raise FileNotFoundError(f"Missing {pairs_path}. Run export web first.")

    pairs_df = con.read_parquet(str(pairs_path)).limit(200).df()
    pairs_sample = pairs_df.to_dict(orient="records")
    sample_out = output_dir / "pairs_sample.json"
    with open(sample_out, "w", encoding="utf-8") as f:
        json.dump(pairs_sample, f, default=str)
    print(f"Exported {len(pairs_sample)} pairs to {sample_out}")

    # 2. Raw evaluation fixture for raw metrics test
    thresh_path = web_data_dir / "eval" / "threshold_table.parquet"
    labels_path = web_data_dir / "eval" / "record_labels.parquet"
    records_path = web_data_dir / "records.parquet"

    thresh_df = con.read_parquet(str(thresh_path)).filter("variant = 'raw'").df()
    all_pairs_df = con.read_parquet(str(pairs_path)).df()
    labels_df = con.read_parquet(str(labels_path)).df()
    records_df = con.read_parquet(str(records_path)).df()

    doppel_pairs: list[list[str]] = []
    doppel_path = truth_dir / "doppelganger_person_pairs.parquet"
    if doppel_path.exists():
        d_df = con.read_parquet(str(doppel_path)).df()
        doppel_pairs = [
            [str(r["person_id_1"]), str(r["person_id_2"])]
            for _, r in d_df.iterrows()
        ]

    raw_fixture = {
        "threshold_rows": thresh_df.to_dict(orient="records"),
        "record_ids": list(records_df["record_id"].astype(str)),
        "pairs": [
            {
                "u": str(r["record_id_l"]),
                "v": str(r["record_id_r"]),
                "weight": float(r["match_weight"]),
            }
            for _, r in all_pairs_df.iterrows()
        ],
        "record_labels": labels_df.to_dict(orient="records"),
        "doppel_pairs": doppel_pairs,
    }

    raw_out = output_dir / "raw_eval_fixture.json"
    with open(raw_out, "w", encoding="utf-8") as f:
        json.dump(raw_fixture, f, default=str)
    print(f"Exported raw evaluation fixture ({len(thresh_df)} thresholds) to {raw_out}")

    # 3. 100 real pairs with Splink-derived comparison labels
    sc = SettingsCreator.from_path_or_dict(model_path)
    settings_obj = sc.get_settings("duckdb")
    comp_cvv_labels = {}
    for comp in settings_obj.comparisons:
        cvv_map = {}
        for cl in comp.comparison_levels:
            cvv_map[cl.comparison_vector_value] = cl.label_for_charts
        comp_cvv_labels[comp.output_column_name] = cvv_map

    pairs_100_df = con.read_parquet(str(pairs_path)).limit(100).df()
    pairs_100 = []
    for _, row in pairs_100_df.iterrows():
        pair_dict = row.to_dict()
        expected_labels = {}
        for comp_name, cvv_map in comp_cvv_labels.items():
            gamma_key = f"gamma_{comp_name}"
            if gamma_key in pair_dict:
                gamma_val = int(pair_dict[gamma_key])
                expected_labels[comp_name] = cvv_map.get(gamma_val, f"Level {gamma_val}")
        pairs_100.append(
            {
                "pair": {k: (str(v) if not isinstance(v, (int, float)) else v) for k, v in pair_dict.items()},
                "expected_labels": expected_labels,
            }
        )

    labels_100_out = output_dir / "pair_labels_100.json"
    with open(labels_100_out, "w", encoding="utf-8") as f:
        json.dump(pairs_100, f, default=str, indent=2)
    print(f"Exported 100-pair labels fixture to {labels_100_out}")


if __name__ == "__main__":
    export_test_fixtures()
