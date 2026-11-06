"""Command line interface for bari-link."""

import argparse
import sys
from pathlib import Path
from typing import Sequence

import pandas as pd

from barilink.generate.population import generate_population


def _print_name_shares(df: pd.DataFrame, sex: str, label: str) -> None:
    """Print top-1 and top-10 name frequencies and percentage shares for a given sex."""
    sub_df = df[df["sex"] == sex]
    total_count = len(sub_df)
    if total_count == 0:
        print(f"No {label.lower()} persons found.")
        return

    name_counts = sub_df["given_name"].value_counts()
    top_1_name = name_counts.index[0]
    top_1_count = name_counts.iloc[0]
    top_1_share = (top_1_count / total_count) * 100.0

    top_10 = name_counts.head(10)
    top_10_count = top_10.sum()
    top_10_share = (top_10_count / total_count) * 100.0

    print(f"\n--- Top {label} Given Names (Total: {total_count:,}) ---")
    print(f"Top-1 Name:  '{top_1_name}' with {top_1_count:,} ({top_1_share:.2f}%)")
    print(f"Top-10 Combined Share: {top_10_count:,} ({top_10_share:.2f}%)")
    print("Top 10 Breakdown:")
    for rank, (name, count) in enumerate(top_10.items(), start=1):
        share = (count / total_count) * 100.0
        print(f"  {rank:2d}. {name:<16} : {count:5,d} ({share:5.2f}%)")


def run_generate(config_path: str, run_name: str, base_output_dir: str = "data/generated") -> int:
    """Run clean population generation and print summary statistics."""
    output_dir = Path(base_output_dir) / run_name
    print("Generating synthetic population...")
    print(f"Config: {config_path}")
    print(f"Output directory: {output_dir.resolve()}")

    persons_df, households_df, manifest = generate_population(config_path, output_dir)

    n_households = len(households_df)
    n_persons = len(persons_df)
    mean_hh_size = n_persons / n_households if n_households > 0 else 0.0

    print("\n" + "=" * 60)
    print("BARI-LINK POPULATION GENERATION SUMMARY")
    print("=" * 60)
    print(f"Households generated: {n_households:,}")
    print(f"Persons generated:    {n_persons:,}")
    print(f"Mean household size:  {mean_hh_size:.2f} members")

    # Marital status counts
    print("\n--- Breakdown by Marital Status ---")
    marital_counts = persons_df["marital_status"].value_counts()
    for status, count in marital_counts.items():
        share = (count / n_persons) * 100.0
        print(f"  {status:<12}: {count:6,d} ({share:5.2f}%)")

    # Name frequencies
    _print_name_shares(persons_df, sex="F", label="Female")
    _print_name_shares(persons_df, sex="M", label="Male")

    print("\n" + "=" * 60)
    print(f"Outputs written to: {output_dir.resolve()}")
    print(f"  - persons.parquet    ({persons_df.shape[0]} rows)")
    print(f"  - households.parquet ({households_df.shape[0]} rows)")
    print("  - persons.csv")
    print("  - households.csv")
    print("  - manifest.json")
    print("=" * 60)

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog="barilink",
        description="bari-link: Kinship-aware probabilistic deduplication registry tools",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen_parser = subparsers.add_parser("generate", help="Generate clean ground-truth population")
    gen_parser.add_argument(
        "--config",
        "-c",
        type=str,
        default="configs/default.yaml",
        help="Path to configuration YAML file",
    )
    gen_parser.add_argument(
        "--run-name",
        "-r",
        type=str,
        default="demo",
        help="Run identifier / output subfolder name",
    )
    gen_parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="data/generated",
        help="Base directory for generated outputs",
    )

    args = parser.parse_args(argv)

    if args.command == "generate":
        return run_generate(
            config_path=args.config,
            run_name=args.run_name,
            base_output_dir=args.output_dir,
        )

    return 1


if __name__ == "__main__":
    sys.exit(main())
