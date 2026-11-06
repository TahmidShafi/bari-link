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
    """Print and persist the required Phase 2 summary metrics."""
    records_df = registry_tables["records"]
    truth_df = truth_tables["record_truth"]
    true_pairs_df = truth_tables["true_pairs"]
    doppel_df = truth_tables["doppelganger_pairs"]
    doppel_person_df = truth_tables.get("doppelganger_person_pairs", pd.DataFrame())
    audit_df = truth_tables.get("audit_stats", pd.DataFrame())
    corr_log_df = truth_tables["corruption_log"]

    summary_lines: list[str] = []

    def emit(s: str = "") -> None:
        print(s)
        summary_lines.append(s)

    total_records = len(records_df)
    total_unique_persons = truth_df["person_id"].nunique()
    total_inflation = (
        ((total_records - total_unique_persons) / total_unique_persons) * 100.0
        if total_unique_persons > 0
        else 0.0
    )

    emit("\n" + "=" * 78)
    emit("BARI-LINK REGISTRY ENROLMENT & CORRUPTION SUMMARY")
    emit("=" * 78)

    # 1. Enrolment Base Audit
    emit("\n--- Enrolment Base Audit (Target vs Realised Share of Eligible Pool) ---")
    emit(
        f"{'Module Name':<20} {'Eligible Pool':>14} {'Enrolled (Uniq)':>16} "
        f"{'Target %':>10} {'Realised %':>12} {'Overlap (UPG)':>14} {'Male Quota':>12}"
    )
    emit("-" * 102)
    modules = ["club_formation", "upg_enrolment", "microfinance_group", "livelihood_support"]
    if not audit_df.empty:
        audit_map = audit_df.set_index("module").to_dict(orient="index")
        for m in modules:
            row = audit_map.get(m, {})
            pool = int(row.get("eligible_pool_size", 0))
            enrolled = int(row.get("enrolled_unique", 0))
            t_share = float(row.get("target_share", 0.0)) * 100.0
            r_share = float(row.get("realised_share", 0.0)) * 100.0
            cond = int(row.get("conditional_overlap_count", 0))
            m_quota = row.get("male_quota", 0)
            m_str = f"{int(m_quota):,d}" if m_quota > 0 else "-"
            emit(
                f"{m:<20} {pool:>14,d} {enrolled:>16,d} {t_share:>9.1f}% "
                f"{r_share:>11.1f}% {cond:>14,d} {m_str:>12}"
            )
    emit("-" * 102)

    # 2. Module Enrolment & Registry Reach
    emit("\n--- Module Enrolment & Registry Reach ---")
    emit(f"{'Module Name':<22} {'Records':>9} {'Unique Persons':>16} {'Inflation %':>13}")
    emit("-" * 64)
    for m in modules:
        m_rec = len(records_df[records_df["source_module"] == m])
        m_per = truth_df[truth_df["source_module"] == m]["person_id"].nunique()
        m_inf = ((m_rec - m_per) / m_per) * 100.0 if m_per > 0 else 0.0
        emit(f"{m:<22} {m_rec:>9,d} {m_per:>16,d} {m_inf:>12.2f}%")
    emit("-" * 64)
    emit(
        f"{'OVERALL TOTAL':<22} {total_records:>9,d} "
        f"{total_unique_persons:>16,d} {total_inflation:>12.2f}%"
    )

    # 3. Persons with > 1 record and true pairs
    person_counts = truth_df["person_id"].value_counts()
    multi_record_persons = int((person_counts > 1).sum())
    total_true_pairs = len(true_pairs_df)
    within_pairs = int((true_pairs_df["is_same_module"]).sum()) if total_true_pairs > 0 else 0
    cross_pairs = int((~true_pairs_df["is_same_module"]).sum()) if total_true_pairs > 0 else 0

    emit("\n--- True Duplicate Linkage Ground Truth ---")
    emit(f"Persons with >1 record:          {multi_record_persons:,d}")
    emit(f"Total True Matching Pairs:       {total_true_pairs:,d}")
    emit(f"  - Within-module true pairs:    {within_pairs:,d}")
    emit(f"  - Cross-module true pairs:     {cross_pairs:,d}")

    # 4. Doppelgangers Audit (distinct households)
    n_person_pairs = len(doppel_person_df) if not doppel_person_df.empty else 0
    n_inj_person = (
        int(doppel_person_df["is_injected"].sum()) if n_person_pairs > 0 else 0
    )
    n_nat_person = n_person_pairs - n_inj_person
    n_record_pairs = len(doppel_df)

    emit("\n--- Hard Negatives (Doppelganger Audit across Distinct Households) ---")
    emit(
        f"Person pairs: {n_person_pairs:,d} total "
        f"({n_nat_person:,d} natural, {n_inj_person:,d} injected; min_target: 50)"
    )
    emit(f"Record pairs: {n_record_pairs:,d} total pairs across registries")

    if not doppel_person_df.empty:
        emit("\nSide-by-Side Doppelganger Examples (up to 3):")
        sample_pairs = doppel_person_df.head(3)
        for ex_idx, (_, row) in enumerate(sample_pairs.iterrows(), start=1):
            p1_id = row["person_id_1"]
            p2_id = row["person_id_2"]
            hh1_id = row.get("household_id_1", "-")
            hh2_id = row.get("household_id_2", "-")
            inj_tag = " [INJECTED]" if row.get("is_injected", False) else " [NATURAL]"
            emit(
                f"\nExample {ex_idx}{inj_tag}: "
                f"Person {p1_id} (HH: {hh1_id}) vs Person {p2_id} (HH: {hh2_id})"
            )
            emit(
                f"  Shared: Village='{row['canonical_village']}' | "
                f"Given='{row['canonical_given_name']}' | "
                f"Guardian='{row['canonical_guardian_name']}'"
            )
            # Display person 1 records
            p1_rec_ids = truth_df[truth_df["person_id"] == p1_id]["record_id"]
            p1_recs = records_df[records_df["record_id"].isin(p1_rec_ids)]
            for _, r in p1_recs.iterrows():
                r_meta = f"[{r['record_id']} | {r['source_module']:<18} | {r['enrolment_date']}]"
                hdr = f"    [{p1_id}] {r_meta}: "
                body = (
                    f"Name: '{r['full_name_raw']}' | Guardian: '{r['guardian_name_raw']}' "
                    f"({r['guardian_type_raw']}) | Age: {r['age_raw']} | "
                    f"Phone: '{r['phone_raw']}' | Village: '{r['village_raw']}'"
                )
                emit(hdr + body)
            # Display person 2 records
            p2_rec_ids = truth_df[truth_df["person_id"] == p2_id]["record_id"]
            p2_recs = records_df[records_df["record_id"].isin(p2_rec_ids)]
            for _, r in p2_recs.iterrows():
                r_meta = f"[{r['record_id']} | {r['source_module']:<18} | {r['enrolment_date']}]"
                hdr = f"    [{p2_id}] {r_meta}: "
                body = (
                    f"Name: '{r['full_name_raw']}' | Guardian: '{r['guardian_name_raw']}' "
                    f"({r['guardian_type_raw']}) | Age: {r['age_raw']} | "
                    f"Phone: '{r['phone_raw']}' | Village: '{r['village_raw']}'"
                )
                emit(hdr + body)

    # 5. Post-Fix Name Frequency Shares
    persons_pq = base_dir / "persons.parquet"
    if persons_pq.exists():
        p_df = pd.read_parquet(persons_pq)
        f_names = p_df[p_df["sex"] == "F"]["given_name"].value_counts()
        m_names = p_df[p_df["sex"] == "M"]["given_name"].value_counts()
        f_total = len(p_df[p_df["sex"] == "F"])
        m_total = len(p_df[p_df["sex"] == "M"])

        f_top1 = (f_names.iloc[0] / f_total * 100.0) if f_total > 0 else 0.0
        f_top10 = (f_names.head(10).sum() / f_total * 100.0) if f_total > 0 else 0.0
        m_top1 = (m_names.iloc[0] / m_total * 100.0) if m_total > 0 else 0.0
        m_top10 = (m_names.head(10).sum() / m_total * 100.0) if m_total > 0 else 0.0

        emit("\n--- Post-Fix Name Frequency Shares (Zipf-Mandelbrot Preservation) ---")
        emit(
            f"Female Given Names: Top-1 share = {f_top1:.2f}% (target < 12.0%), "
            f"Top-10 share = {f_top10:.2f}% (target > 30.0%)"
        )
        emit(
            f"Male Given Names:   Top-1 share = {m_top1:.2f}% (target < 12.0%), "
            f"Top-10 share = {m_top10:.2f}% (target > 30.0%)"
        )

    # 6. Transliteration Leakage Guard Ratios
    n_shared, n_gen, rule_ratio = get_rule_counts()
    trans_events = corr_log_df[corr_log_df["corruption_type"].str.startswith("transliteration")]
    n_trans = len(trans_events)
    n_gen_events = int((trans_events["is_generator_only"]).sum()) if n_trans > 0 else 0
    event_ratio = (n_gen_events / n_trans) if n_trans > 0 else 0.0

    emit("\n--- Normalisation Leakage Guard (Transliteration Rules) ---")
    emit(
        f"Rule count ratio (generator-only): {n_gen}/{n_shared + n_gen} "
        f"({rule_ratio:.1%}, target >= 40.0%)"
    )
    emit(
        f"Event share ratio (generator-only): {n_gen_events:,d}/{n_trans:,d} "
        f"({event_ratio:.1%}, target >= 30.0%)"
    )

    # 7. Corruption Frequency Table
    emit("\n--- Corruption Frequency (% of Records per Module) ---")
    rec_mod_map = records_df.set_index("record_id")["source_module"].to_dict()
    corr_with_mod = corr_log_df.copy()
    corr_with_mod["source_module"] = corr_with_mod["record_id"].map(rec_mod_map)

    types = sorted(corr_with_mod["corruption_type"].unique())
    header = f"{'Corruption Type':<32}" + "".join(f"{m[:10]:>11}" for m in modules)
    emit(header)
    emit("-" * len(header))
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
        emit(row_str)

    # 8. Five Example Clusters (Persons with >= 3 records)
    emit("\n--- Example Clusters (5 Random Persons with >= 3 Records) ---")
    persons_3plus = person_counts[person_counts >= 3].index.tolist()
    if len(persons_3plus) > 0:
        sample_size = min(5, len(persons_3plus))
        sample_persons = sorted(persons_3plus)[:sample_size]
        for idx, p_id in enumerate(sample_persons, start=1):
            p_truth = truth_df[truth_df["person_id"] == p_id].iloc[0]
            p_recs = records_df[
                records_df["record_id"].isin(
                    truth_df[truth_df["person_id"] == p_id]["record_id"]
                )
            ]
            emit(f"\nCluster {idx}: Person {p_id}")
            emit(
                f"  Clean: {p_truth['clean_full_name']} | "
                f"Guardian: {p_truth['clean_guardian_name']} ({p_truth['clean_guardian_type']}) | "
                f"Phone: {p_truth['clean_phone']} | Village: {p_truth['clean_village']}"
            )
            for _, r in p_recs.iterrows():
                emit(
                    f"    [{r['record_id']} | {r['source_module']:<18} | {r['enrolment_date']}]: "
                    f"Name: '{r['full_name_raw']}' | "
                    f"Guardian: '{r['guardian_name_raw']}' ({r['guardian_type_raw']}) | "
                    f"Age: {r['age_raw']} | Phone: '{r['phone_raw']}' | "
                    f"Village: '{r['village_raw']}'"
                )
    else:
        emit("No persons with >= 3 records found in current run.")

    emit("\n" + "=" * 78)
    emit(f"Registry data exported to: {base_dir.resolve()}")
    emit("  Model-Visible Files (data/generated/<run>/registry/):")
    emit("    - records.parquet, rosters.parquet")
    emit("    - club_formation.csv, upg_enrolment.csv")
    emit("    - microfinance_group.csv, livelihood_support.csv")
    emit("  Evaluation Files (data/generated/<run>/truth/):")
    emit("    - record_truth.parquet, true_pairs.parquet")
    emit("    - corruption_log.parquet, doppelganger_pairs.parquet")
    emit("    - doppelganger_person_pairs.parquet, audit_stats.parquet")
    emit("=" * 78)

    # Persist summary to disk
    summary_path = base_dir / "summary.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines) + "\n")
    print(f"Summary persisted to: {summary_path.resolve()}")


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
