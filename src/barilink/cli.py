"""Command line interface for bari-link."""

import argparse
import sys
from pathlib import Path
from typing import Sequence

import pandas as pd

from barilink.corrupt.registry import export_registries
from barilink.corrupt.transliteration import get_rule_counts
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

    persons_df, households_df, _ = generate_population(config_path, output_dir)

    n_households = len(households_df)
    n_persons = len(persons_df)
    mean_hh_size = n_persons / n_households if n_households > 0 else 0.0

    print("\n" + "=" * 65)
    print("BARI-LINK POPULATION GENERATION SUMMARY")
    print("=" * 65)
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

    print("\n" + "=" * 65)
    print(f"Outputs written to: {output_dir.resolve()}")
    print(f"  - persons.parquet    ({persons_df.shape[0]} rows)")
    print(f"  - households.parquet ({households_df.shape[0]} rows)")
    print("  - persons.csv")
    print("  - households.csv")
    print("  - manifest.json")
    print("=" * 65)

    return 0


def _print_corruption_summary(
    registry_tables: dict[str, pd.DataFrame],
    truth_tables: dict[str, pd.DataFrame],
    run_name: str,
    base_dir: Path,
) -> None:
    """Print the required Phase 2 summary metrics."""
    records_df = registry_tables["records"]
    truth_df = truth_tables["record_truth"]
    true_pairs_df = truth_tables["true_pairs"]
    doppel_df = truth_tables["doppelganger_pairs"]
    corr_log_df = truth_tables["corruption_log"]

    total_records = len(records_df)
    total_unique_persons = truth_df["person_id"].nunique()
    total_inflation = (
        ((total_records - total_unique_persons) / total_unique_persons) * 100.0
        if total_unique_persons > 0
        else 0.0
    )

    print("\n" + "=" * 75)
    print("BARI-LINK REGISTRY ENROLMENT & CORRUPTION SUMMARY")
    print("=" * 75)

    # 1. Reach per module and overall
    print("\n--- Module Enrolment & Registry Reach ---")
    print(f"{'Module Name':<22} {'Records':>9} {'Unique Persons':>16} {'Inflation %':>13}")
    print("-" * 64)
    modules = ["club_formation", "upg_enrolment", "microfinance_group", "livelihood_support"]
    for m in modules:
        m_rec = len(records_df[records_df["source_module"] == m])
        m_per = truth_df[truth_df["source_module"] == m]["person_id"].nunique()
        m_inf = ((m_rec - m_per) / m_per) * 100.0 if m_per > 0 else 0.0
        print(f"{m:<22} {m_rec:>9,d} {m_per:>16,d} {m_inf:>12.2f}%")
    print("-" * 64)
    print(
        f"{'OVERALL TOTAL':<22} {total_records:>9,d} "
        f"{total_unique_persons:>16,d} {total_inflation:>12.2f}%"
    )

    # 2. Persons with > 1 record and true pairs
    person_counts = truth_df["person_id"].value_counts()
    multi_record_persons = int((person_counts > 1).sum())
    total_true_pairs = len(true_pairs_df)
    within_pairs = int((true_pairs_df["is_same_module"]).sum()) if total_true_pairs > 0 else 0
    cross_pairs = int((~true_pairs_df["is_same_module"]).sum()) if total_true_pairs > 0 else 0

    print("\n--- True Duplicate Linkage Ground Truth ---")
    print(f"Persons with >1 record:          {multi_record_persons:,d}")
    print(f"Total True Matching Pairs:       {total_true_pairs:,d}")
    print(f"  - Within-module true pairs:    {within_pairs:,d}")
    print(f"  - Cross-module true pairs:     {cross_pairs:,d}")

    # 3. Doppelgangers
    n_doppel = len(doppel_df)
    n_injected = int(doppel_df["is_injected"].sum()) if n_doppel > 0 else 0
    n_natural = n_doppel - n_injected
    print("\n--- Hard Negatives (Doppelganger Pairs) ---")
    print(
        f"Total Doppelganger Pairs:        {n_doppel:,d} "
        f"({n_natural:,d} natural, {n_injected:,d} injected)"
    )

    # 4. Transliteration Leakage Guard Ratios
    n_shared, n_gen, rule_ratio = get_rule_counts()
    trans_events = corr_log_df[corr_log_df["corruption_type"].str.startswith("transliteration")]
    n_trans = len(trans_events)
    n_gen_events = int((trans_events["is_generator_only"]).sum()) if n_trans > 0 else 0
    event_ratio = (n_gen_events / n_trans) if n_trans > 0 else 0.0

    print("\n--- Normalisation Leakage Guard (Transliteration Rules) ---")
    print(
        f"Rule count ratio (generator-only): {n_gen}/{n_shared + n_gen} "
        f"({rule_ratio:.1%}, target >= 40.0%)"
    )
    print(
        f"Event share ratio (generator-only): {n_gen_events:,d}/{n_trans:,d} "
        f"({event_ratio:.1%}, target >= 30.0%)"
    )

    # 5. Corruption Frequency Table
    print("\n--- Corruption Frequency (% of Records per Module) ---")
    # Merge source_module onto corruption_log via record_id
    rec_mod_map = records_df.set_index("record_id")["source_module"].to_dict()
    corr_with_mod = corr_log_df.copy()
    corr_with_mod["source_module"] = corr_with_mod["record_id"].map(rec_mod_map)

    types = sorted(corr_with_mod["corruption_type"].unique())
    header = f"{'Corruption Type':<32}" + "".join(f"{m[:10]:>11}" for m in modules)
    print(header)
    print("-" * len(header))
    for c_type in types:
        row_str = f"{c_type:<32}"
        for m in modules:
            m_total = len(records_df[records_df["source_module"] == m])
            c_count = len(
                corr_with_mod[
                    (corr_with_mod["corruption_type"] == c_type)
                    & (corr_with_mod["source_module"] == m)
                ]
            )
            pct = (c_count / m_total * 100.0) if m_total > 0 else 0.0
            row_str += f"{pct:>10.1f}%"
        print(row_str)

    # 6. Five Example Clusters (Persons with >= 3 records)
    print("\n--- Example Clusters (5 Random Persons with >= 3 Records) ---")
    persons_3plus = person_counts[person_counts >= 3].index.tolist()
    if len(persons_3plus) > 0:
        sample_size = min(5, len(persons_3plus))
        # Deterministic sample from candidates
        sample_persons = sorted(persons_3plus)[:sample_size]
        for idx, p_id in enumerate(sample_persons, start=1):
            p_truth = truth_df[truth_df["person_id"] == p_id].iloc[0]
            p_recs = records_df[
                records_df["record_id"].isin(
                    truth_df[truth_df["person_id"] == p_id]["record_id"]
                )
            ]
            print(f"\nCluster {idx}: Person {p_id}")
            print(
                f"  Clean: {p_truth['clean_full_name']} | "
                f"Guardian: {p_truth['clean_guardian_name']} ({p_truth['clean_guardian_type']}) | "
                f"Phone: {p_truth['clean_phone']} | Village: {p_truth['clean_village']}"
            )
            for _, r in p_recs.iterrows():
                print(
                    f"    [{r['record_id']} | {r['source_module']:<18} | {r['enrolment_date']}]: "
                    f"Name: '{r['full_name_raw']}' | "
                    f"Guardian: '{r['guardian_name_raw']}' ({r['guardian_type_raw']}) | "
                    f"Age: {r['age_raw']} | Phone: '{r['phone_raw']}' | "
                    f"Village: '{r['village_raw']}'"
                )
    else:
        print("No persons with >= 3 records found in current run.")

    print("\n" + "=" * 75)
    print(f"Registry data exported to: {base_dir.resolve()}")
    print("  Model-Visible Files (data/generated/<run>/registry/):")
    print("    - records.parquet, rosters.parquet")
    print("    - club_formation.csv, upg_enrolment.csv")
    print("    - microfinance_group.csv, livelihood_support.csv")
    print("  Evaluation Files (data/generated/<run>/truth/):")
    print("    - record_truth.parquet, true_pairs.parquet")
    print("    - corruption_log.parquet, doppelganger_pairs.parquet")
    print("=" * 75)


def run_corrupt(config_path: str, run_name: str, base_output_dir: str = "data/generated") -> int:
    """Run registry sampling and corruption on clean population."""
    print("Running record corruption and registry generation...")
    print(f"Config: {config_path}")
    print(f"Run: {run_name}")

    base_dir = Path(base_output_dir) / run_name
    registry_tables, truth_tables = export_registries(config_path, run_name, base_output_dir)
    _print_corruption_summary(registry_tables, truth_tables, run_name, base_dir)
    return 0


def run_build(config_path: str, run_name: str, base_output_dir: str = "data/generated") -> int:
    """Run full pipeline end-to-end: generate clean population then corrupt."""
    print("=" * 75)
    print("BARI-LINK BUILD: FULL GENERATE + CORRUPT PIPELINE")
    print("=" * 75)
    run_generate(config_path, run_name, base_output_dir)
    print("\n")
    run_corrupt(config_path, run_name, base_output_dir)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog="barilink",
        description="bari-link: Kinship-aware probabilistic deduplication registry tools",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. generate
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

    # 2. corrupt
    corr_parser = subparsers.add_parser("corrupt", help="Sample and corrupt enrolment registries")
    corr_parser.add_argument(
        "--config",
        "-c",
        type=str,
        default="configs/default.yaml",
        help="Path to configuration YAML file",
    )
    corr_parser.add_argument(
        "--run-name",
        "-r",
        type=str,
        default="demo",
        help="Run identifier / output subfolder name",
    )
    corr_parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="data/generated",
        help="Base directory for generated outputs",
    )

    # 3. build (generate + corrupt)
    build_parser = subparsers.add_parser("build", help="Run full pipeline: generate then corrupt")
    build_parser.add_argument(
        "--config",
        "-c",
        type=str,
        default="configs/default.yaml",
        help="Path to configuration YAML file",
    )
    build_parser.add_argument(
        "--run-name",
        "-r",
        type=str,
        default="demo",
        help="Run identifier / output subfolder name",
    )
    build_parser.add_argument(
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
    elif args.command == "corrupt":
        return run_corrupt(
            config_path=args.config,
            run_name=args.run_name,
            base_output_dir=args.output_dir,
        )
    elif args.command == "build":
        return run_build(
            config_path=args.config,
            run_name=args.run_name,
            base_output_dir=args.output_dir,
        )

    return 1


if __name__ == "__main__":
    sys.exit(main())
