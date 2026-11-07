"""Blocking diagnostic analysis: candidates, pair completeness, and reduction ratio."""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd


def compute_blocking_diagnostics(
    run_name: str = "holdout_0",
    method: str = "splink_v1",
    base_data_dir: str = "data/generated",
    base_results_dir: str = "results",
    write_md: bool = True,
) -> pd.DataFrame:
    """Compute marginal and cumulative blocking diagnostics for Splink rules on a given run."""
    run_dir = Path(base_data_dir) / run_name
    feat_path = run_dir / "registry" / "features.parquet"
    truth_path = run_dir / "truth" / "true_pairs.parquet"

    if not feat_path.exists():
        raise FileNotFoundError(f"Features parquet not found at {feat_path}")
    if not truth_path.exists():
        raise FileNotFoundError(f"True pairs parquet not found at {truth_path}")

    con = duckdb.connect()
    con.execute(f"CREATE TABLE features AS SELECT * FROM read_parquet('{feat_path.as_posix()}')")
    con.execute(f"CREATE TABLE true_pairs AS SELECT * FROM read_parquet('{truth_path.as_posix()}')")

    n_records = con.execute("SELECT COUNT(*) FROM features").fetchone()[0]
    total_possible = (n_records * (n_records - 1)) // 2
    total_true = con.execute("SELECT COUNT(*) FROM true_pairs").fetchone()[0]

    rules = [
        (
            "Rule 1: given_first_skel + village_canon",
            "(l.given_first_skel = r.given_first_skel) AND (l.village_canon = r.village_canon) "
            "AND l.given_first_skel IS NOT NULL AND l.village_canon IS NOT NULL",
        ),
        (
            "Rule 2: phone_norm",
            "l.phone_norm = r.phone_norm AND l.phone_norm IS NOT NULL",
        ),
        (
            "Rule 3: guardian_skeleton + village_canon",
            "(l.guardian_skeleton = r.guardian_skeleton) AND (l.village_canon = r.village_canon) "
            "AND l.guardian_skeleton IS NOT NULL AND l.village_canon IS NOT NULL",
        ),
        (
            "Rule 4: name_skeleton + union_raw",
            "(l.name_skeleton = r.name_skeleton) AND (l.union_raw = r.union_raw) "
            "AND l.name_skeleton IS NOT NULL AND l.union_raw IS NOT NULL",
        ),
        (
            "Rule 5: given_first_skel + birth_year_est",
            "(l.given_first_skel = r.given_first_skel) AND (l.birth_year_est = r.birth_year_est) "
            "AND l.given_first_skel IS NOT NULL AND l.birth_year_est IS NOT NULL",
        ),
    ]

    cum_sql_parts = []
    results = []

    for name, sql_cond in rules:
        q_rule = (
            "SELECT l.record_id AS r1, r.record_id AS r2 "
            f"FROM features l JOIN features r ON ({sql_cond}) "
            "WHERE l.record_id < r.record_id"
        )
        con.execute(f"CREATE OR REPLACE TEMP TABLE rule_pairs AS {q_rule}")
        rule_count = con.execute("SELECT COUNT(*) FROM rule_pairs").fetchone()[0]
        rule_true = con.execute("""
            SELECT COUNT(*) FROM rule_pairs rp
            JOIN true_pairs tp ON (rp.r1 = LEAST(tp.record_id_1, tp.record_id_2)
                               AND rp.r2 = GREATEST(tp.record_id_1, tp.record_id_2))
        """).fetchone()[0]

        cum_sql_parts.append(f"({sql_cond})")
        cum_cond = " OR ".join(cum_sql_parts)
        q_cum = (
            "SELECT l.record_id AS r1, r.record_id AS r2 "
            f"FROM features l JOIN features r ON ({cum_cond}) "
            "WHERE l.record_id < r.record_id"
        )
        con.execute(f"CREATE OR REPLACE TEMP TABLE cum_pairs AS {q_cum}")
        cum_count = con.execute("SELECT COUNT(*) FROM cum_pairs").fetchone()[0]
        cum_true = con.execute("""
            SELECT COUNT(*) FROM cum_pairs cp
            JOIN true_pairs tp ON (cp.r1 = LEAST(tp.record_id_1, tp.record_id_2)
                               AND cp.r2 = GREATEST(tp.record_id_1, tp.record_id_2))
        """).fetchone()[0]

        red_ratio = (1.0 - (cum_count / total_possible)) * 100.0 if total_possible > 0 else 0.0
        completeness = (cum_true / total_true) * 100.0 if total_true > 0 else 0.0
        rule_comp = (rule_true / total_true) * 100.0 if total_true > 0 else 0.0

        results.append(
            {
                "rule": name,
                "marginal_candidates": rule_count,
                "marginal_true": rule_true,
                "marginal_completeness": rule_comp,
                "cumulative_candidates": cum_count,
                "cumulative_true": cum_true,
                "reduction_ratio": red_ratio,
                "pair_completeness": completeness,
            }
        )

    con.close()
    df = pd.DataFrame(results)

    if write_md:
        out_dir = Path(base_results_dir) / run_name / method
        out_dir.mkdir(parents=True, exist_ok=True)
        md_path = out_dir / "blocking.md"

        cum_cand_final = df.iloc[-1]["cumulative_candidates"]
        cum_true_final = df.iloc[-1]["cumulative_true"]
        red_ratio_final = df.iloc[-1]["reduction_ratio"]
        comp_final = df.iloc[-1]["pair_completeness"]

        header_cols = [
            "Blocking Rule",
            "Marginal Candidates",
            "Marginal True Pairs",
            "Marginal Pair Completeness (%)",
            "Cumulative Candidates",
            "Cumulative True Pairs",
            "Cumulative Reduction Ratio (%)",
            "Cumulative Pair Completeness (%)",
        ]

        lines = [
            f"# Blocking Diagnostics: `{method}` on `{run_name}`",
            "",
            "## Overview",
            f"- **Total Records ($N$)**: {n_records:,}",
            f"- **Total Possible Pairs ($N(N-1)/2$)**: {total_possible:,}",
            f"- **Total True Match Pairs**: {total_true:,}",
            f"- **Total Candidate Pairs Generated**: {cum_cand_final:,}",
            f"- **Total True Pairs Captured**: {cum_true_final:,}",
            f"- **Cumulative Reduction Ratio**: {red_ratio_final:.2f}%",
            f"- **Cumulative Pair Completeness (Recall Ceiling)**: {comp_final:.2f}%",
            "",
            "---",
            "",
            "## Blocking Rule Performance",
            "",
            "| " + " | ".join(header_cols) + " |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]

        for _, r in df.iterrows():
            row_items = [
                f"**{r['rule']}**",
                f"{r['marginal_candidates']:,}",
                f"{r['marginal_true']:,}",
                f"{r['marginal_completeness']:.2f}%",
                f"{r['cumulative_candidates']:,}",
                f"{r['cumulative_true']:,}",
                f"{r['reduction_ratio']:.2f}%",
                f"{r['pair_completeness']:.2f}%",
            ]
            lines.append("| " + " | ".join(row_items) + " |")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    return df
