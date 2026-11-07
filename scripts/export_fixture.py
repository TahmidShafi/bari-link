"""Export offline test fixtures for Vitest suite in web/src/tests/fixtures/

Regenerates:
1. web/src/tests/fixtures/pairs_sample.json (200 real pairs for waterfall testing)
2. web/src/tests/fixtures/raw_eval_fixture.json (full holdout_5 evaluation fixture)
"""

import json
from pathlib import Path

import duckdb


def export_test_fixtures(
    web_data_dir: Path = Path("web/public/data"),
    output_dir: Path = Path("web/src/tests/fixtures"),
    truth_dir: Path = Path("data/generated/holdout_5/truth"),
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


if __name__ == "__main__":
    export_test_fixtures()
