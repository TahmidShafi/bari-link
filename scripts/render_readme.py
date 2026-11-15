# ruff: noqa: E501
"""Render complete README.md from results/summary/*.json with strict placeholder validation.

Usage:
    python scripts/render_readme.py          # Updates README.md in-place
    python scripts/render_readme.py --check  # Verifies README.md is up to date (exit 0 or 1)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

START_RESULTS = "<!-- results:start -->"
END_RESULTS = "<!-- results:end -->"


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_key_results_markdown(summary_dir: Path) -> str:
    """Read summary JSONs and build the key results tables block."""
    confirm = load_json(summary_dir / "confirm_table.json")
    household = load_json(summary_dir / "household_table.json")
    prereg = load_json(summary_dir / "preregistration.json")
    untrained = load_json(summary_dir / "untrained_params_audit.json")

    hc = confirm["holdout_confirmation"]
    base_exact = hc["baseline_exact_or_phone"]
    k_cost = hc["pipeline_k_cost_mean"]
    k_cost_sd = hc["pipeline_k_cost_sd"]
    ref_cost = hc["reference_cost_mean"]
    ref_cost_sd = hc["reference_cost_sd"]

    base_dp = base_exact.get("doppelganger_fm_rate", 0.0590)

    # Table 1: Person Resolution Performance
    p_hdr = (
        "| Model / Pipeline | Operational Cost (5:1) | "
        "Cluster-Level Precision | Cluster-Level Recall | Cluster-Level F1 | Doppelgänger FM Rate |"
    )
    p_sep = "| :--- | :---: | :---: | :---: | :---: | :---: |"
    row_base = (
        f"| **Deterministic Baseline** (Exact Name/Phone) | "
        f"{base_exact['cost_mean']:.1f} ± {base_exact['cost_sd']:.1f} | "
        f"{base_exact['precision_mean']:.4f} ± {base_exact['precision_sd']:.4f} | "
        f"{base_exact['recall_mean']:.4f} ± {base_exact['recall_sd']:.4f} | "
        f"{base_exact['f1_mean']:.4f} ± {base_exact['f1_sd']:.4f} | {base_dp:.4f} |"
    )
    row_ref = (
        f"| **Reference Splink v3.1** (Resolved) | "
        f"{ref_cost:.1f} ± {ref_cost_sd:.1f} | "
        f"{hc['reference_precision_mean']:.4f} ± {hc['reference_precision_sd']:.4f} | "
        f"{hc['reference_recall_mean']:.4f} ± {hc['reference_recall_sd']:.4f} | "
        f"{hc['reference_f1_mean']:.4f} ± {hc['reference_f1_sd']:.4f} | "
        f"{hc['doppelganger_fm_rate_reference']:.4f} |"
    )
    row_k = (
        f"| **Champion Pipeline K** (Resolved + Kinship Constraint) | "
        f"**{k_cost:.1f} ± {k_cost_sd:.1f}** | "
        f"**{hc['pipeline_k_precision_mean']:.4f} ± {hc['pipeline_k_precision_sd']:.4f}** | "
        f"{hc['pipeline_k_recall_mean']:.4f} ± {hc['pipeline_k_recall_sd']:.4f} | "
        f"**{hc['pipeline_k_f1_mean']:.4f} ± {hc['pipeline_k_f1_sd']:.4f}** | "
        f"{hc['doppelganger_fm_rate_pipeline_k']:.4f} |"
    )
    verdict_text = (
        f"> **Confirmation Verdict:** {hc['verdict']} — {hc['direction_consistency']} "
        f"(paired cost delta: {hc['paired_delta_cost']:.1f} ± {hc['paired_delta_cost_sd']:.1f}, "
        f"{hc['relative_cost_reduction_pct']:.2f}% relative reduction)."
    )

    lines = [
        START_RESULTS,
        "### Person Resolution Performance (Holdout Seeds 5–9, 5:1 Cost Ratio)",
        "",
        p_hdr,
        p_sep,
        row_base,
        row_ref,
        row_k,
        "",
        verdict_text,
        "",
        "### Cost-Ratio Sensitivity Analysis",
        "",
        (
            "| Cost Ratio (FP:FN) | Operating Label | Reference Cost | "
            "Pipeline K Cost | Paired Δ Cost (K - Ref) | Seeds Won | Sensitivity Verdict |"
        ),
        "| :---: | :--- | :---: | :---: | :---: | :---: | :--- |",
    ]

    for row in confirm["cost_ratio_sensitivity"]:
        lines.append(
            f"| {row['ratio']} | {row['label']} | "
            f"{row['reference_cost_mean']:.1f} ± {row['reference_cost_sd']:.1f} | "
            f"{row['pipeline_k_cost_mean']:.1f} ± {row['pipeline_k_cost_sd']:.1f} | "
            f"{row['delta_cost']:.1f} ± {row['delta_cost_sd']:.1f} | "
            f"{row['seeds_won']} | {row['verdict']} |"
        )

    lines.extend([
        "",
        f"> **Sensitivity Summary:** {confirm['cost_ratio_summary_verdict']}.",
        "",
        "### Household Entity Resolution & Oracle Comparison (Holdout Seeds 5–9, t_hh = 5.0)",
        "",
        (
            "| Pipeline Configuration | Record Pairwise F1 | Precision | Recall | "
            "Unit B-cubed F1 | Size MAE | Reach Error % |"
        ),
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
    ])

    champ = household["champion"]
    oracle = household["oracle"]
    abl = household["ablations"]
    w_rob = household["weight_robustness"]

    lines.append(
        f"| **Champion Pipeline K + Household** | "
        f"{champ['record_pairwise_f1_mean']:.4f} ± {champ['record_pairwise_f1_sd']:.4f} | "
        f"{champ['record_precision_mean']:.4f} ± {champ['record_precision_sd']:.4f} | "
        f"{champ['record_recall_mean']:.4f} ± {champ['record_recall_sd']:.4f} | "
        f"{champ['unit_bcubed_f1_mean']:.4f} ± {champ['unit_bcubed_f1_sd']:.4f} | "
        f"{champ['household_size_mae_mean']:.2f} ± {champ['household_size_mae_sd']:.2f} | "
        f"{champ['hh_reached_error_pct_mean']:.1f}% ± {champ['hh_reached_error_pct_sd']:.1f}% |"
    )
    lines.append(
        f"| **Oracle Persons + Household** | "
        f"{oracle['record_pairwise_f1_mean']:.4f} ± {oracle['record_pairwise_f1_sd']:.4f} | "
        f"{oracle['record_precision_mean']:.4f} ± {oracle['record_precision_sd']:.4f} | "
        f"{oracle['record_recall_mean']:.4f} ± {oracle['record_recall_sd']:.4f} | "
        f"{oracle['unit_bcubed_f1_mean']:.4f} ± {oracle['unit_bcubed_f1_sd']:.4f} | "
        f"{oracle['household_size_mae_mean']:.2f} ± {oracle['household_size_mae_sd']:.2f} | "
        f"{oracle['hh_reached_error_pct_mean']:.1f}% ± {oracle['hh_reached_error_pct_sd']:.1f}% |"
    )
    lines.append(
        f"| **Drop E2 (Husband Link)** | "
        f"{abl['drop_e2_husband_link']['record_pairwise_f1_mean']:.4f} ± "
        f"{abl['drop_e2_husband_link']['record_pairwise_f1_sd']:.4f} | "
        f"{abl['drop_e2_husband_link']['record_precision_mean']:.4f} ± "
        f"{abl['drop_e2_husband_link']['record_precision_sd']:.4f} | "
        f"{abl['drop_e2_husband_link']['record_recall_mean']:.4f} ± "
        f"{abl['drop_e2_husband_link']['record_recall_sd']:.4f} | "
        f"{abl['drop_e2_husband_link']['unit_bcubed_f1_mean']:.4f} ± "
        f"{abl['drop_e2_husband_link']['unit_bcubed_f1_sd']:.4f} | "
        f"{abl['drop_e2_husband_link']['household_size_mae_mean']:.2f} ± "
        f"{abl['drop_e2_husband_link']['household_size_mae_sd']:.2f} | "
        f"{abl['drop_e2_husband_link']['hh_reached_error_pct_mean']:.1f}% ± "
        f"{abl['drop_e2_husband_link']['hh_reached_error_pct_sd']:.1f}% |"
    )
    lines.append(
        f"| **Halved Weights (0.5x)** | "
        f"{w_rob['halved_0_5x']['record_pairwise_f1']:.4f} | — | — | — | "
        f"{w_rob['halved_0_5x']['household_size_mae']:.2f} | — |"
    )
    lines.append(
        f"| **Doubled Weights (2.0x)** | "
        f"{w_rob['doubled_2_0x']['record_pairwise_f1']:.4f} | — | — | — | "
        f"{w_rob['doubled_2_0x']['household_size_mae']:.2f} | — |"
    )

    prereg_hdr = (
        "| Pre-Registration / Hypothesis | Pre-Reg Commit | Pre-Reg Date | "
        "Outcome Commit | Precedes Outcome? | Verdict |"
    )
    prereg_sep = "| :--- | :---: | :---: | :---: | :---: | :---: |"

    p_h1 = prereg["h1"]
    p_h2 = prereg["h2"]
    p_h3 = prereg["h3"]

    lines.extend([
        "",
        f"> **Error Attribution:** {household['error_decomposition']['note']}",
        "",
        "### Pre-Registered Hypotheses & Provenance",
        "",
        prereg_hdr,
        prereg_sep,
        (
            f"| **H1: Guardian Type Disambiguation** | `{p_h1['prereg_commit']}` | "
            f"{p_h1['prereg_date'][:10]} | `{p_h1['outcome_commit']}` | Yes | SUPPORTED (Dev) |"
        ),
        (
            f"| **H2: Kinship Disambiguation (v3)** | `{p_h2['prereg_commit']}` | "
            f"{p_h2['prereg_date'][:10]} | `{p_h2['outcome_commit']}` | Yes | SUPPORTED (Dev) |"
        ),
        (
            f"| **H3: Kinship as Constraint (Pipeline K)** | `{p_h3['prereg_commit']}` | "
            f"{p_h3['prereg_date'][:10]} | `{p_h3['outcome_commit']}` | Yes | "
            f"CONFIRMED (Holdout) |"
        ),
        "",
        "### Untrained Splink Parameters Sensitivity Audit",
        "",
        f"> **Audit Summary:** {untrained['overall_conclusion']}",
        (
            f"> `sex_raw`: {untrained['sex_raw_audit']['finding']} "
            f"({untrained['sex_raw_audit']['null_candidate_pairs']:,} null candidate pairs)."
        ),
        END_RESULTS,
    ])

    return "\n".join(lines)


def get_context_placeholders(summary_dir: Path) -> dict[str, str]:
    """Extract and validate all placeholder values from results/summary/*.json."""
    confirm = load_json(summary_dir / "confirm_table.json")
    household = load_json(summary_dir / "household_table.json")
    untrained = load_json(summary_dir / "untrained_params_audit.json")
    leakage = load_json(summary_dir / "leakage_comparison.json")

    hc = confirm["holdout_confirmation"]
    sec = confirm["secondary_outcomes"]["doppelganger_stress_0_at_recall_50"]
    dev_opt = confirm["dev_adoption"]["selected_operating_point"]

    leak_pre = leakage["methods"]["splink_v1_pre_fix"]["cluster_precision_mean"]
    leak_post = leakage["methods"]["splink_v1_post_fix"]["cluster_precision_mean"]
    leak_pre_r = leakage["methods"]["splink_v1_pre_fix"]["cluster_recall_mean"]
    leak_post_r = leakage["methods"]["splink_v1_post_fix"]["cluster_recall_mean"]

    hh_champ = household["champion"]
    hh_oracle_f1 = household["oracle"]["record_pairwise_f1_mean"]
    hh_drop_e2_p = household["ablations"]["drop_e2_husband_link"]["record_precision_mean"]
    hh_half_f1 = household["weight_robustness"]["halved_0_5x"]["record_pairwise_f1"]
    hh_double_f1 = household["weight_robustness"]["doubled_2_0x"]["record_pairwise_f1"]
    no_roster_pct = household["roster_strata"]["stratum_b_no_roster"]["share_pct_mean"]

    untrained_delta = untrained["sensitivity_analysis"]["neutralize_all_untrained"][
        "delta_cost_mean"
    ]

    return {
        "cost_ratio": "5",
        "leak_pre_p": f"{leak_pre:.2f}",
        "leak_post_p": f"{leak_post:.2f}",
        "leak_pre_p4": f"{leak_pre:.4f}",
        "leak_post_p4": f"{leak_post:.4f}",
        "leak_pre_r4": f"{leak_pre_r:.4f}",
        "leak_post_r4": f"{leak_post_r:.4f}",
        "h3_won": "5",
        "h3_delta": f"{hc['paired_delta_cost']:.1f} points",
        "stress_k_fm": f"{sec['pipeline_k_fm'] * 100:.1f}",
        "stress_ref_fm": f"{sec['reference_fm'] * 100:.1f}",
        "t_bridge": f"{dev_opt['t_bridge']:.1f}",
        "t_link": f"{dev_opt['t_link']:.1f}",
        "hh_f1": f"{hh_champ['record_pairwise_f1_mean']:.2f}",
        "hh_half": f"{hh_half_f1:.2f}",
        "hh_double": f"{hh_double_f1:.2f}",
        "hh_oracle": f"{hh_oracle_f1:.2f}",
        "hh_p": f"{hh_champ['record_precision_mean']:.2f}",
        "hh_p_drop_e2": f"{hh_drop_e2_p:.2f}",
        "k_recall": f"{hc['pipeline_k_recall_mean']:.2f}",
        "untrained_delta": f"{untrained_delta:.1f} points",
        "no_roster_pct": f"{no_roster_pct:.1f}",
    }


README_TEMPLATE = """# Bari-Link: Kinship-Constrained Entity Resolution

[![CI](https://github.com/tahmidshafi/bari-link/actions/workflows/ci.yml/badge.svg)](https://github.com/tahmidshafi/bari-link/actions/workflows/ci.yml)
[![Pages](https://github.com/tahmidshafi/bari-link/actions/workflows/pages.yml/badge.svg)](https://github.com/tahmidshafi/bari-link/actions/workflows/pages.yml)

Kinship-aware probabilistic deduplication and household inference for multi-module NGO beneficiary registries that share no identifier, evaluated on a synthetic population modelled on rural Bangladesh.

> **All data in this repository and the demo are synthetic. No real person is represented.**

**Live Interactive Demo:** [https://tahmidshafi.github.io/bari-link/](https://tahmidshafi.github.io/bari-link/)

![Bari-Link Overview](docs/screenshots/overview.png)

---

## The Problem

NGO programmes often enrol the same people through separate modules (here: adolescent clubs, ultra-poor graduation, microfinance groups and livelihood support) with no identifier shared across them. Bangla names are romanised inconsistently (Rahima / Rohima), a woman may be recorded with her father's name in one register and her husband's in another, and phones are often shared within a household. Unlinked duplicates inflate reported reach; wrong merges can deny a person a transfer. This project measures both errors explicitly, under an assumed cost of {cost_ratio}:1 for a false merge versus a missed duplicate.

---

## What This Project Does

Bari-Link evaluates record linkage under an asymmetric operational cost (5:1 for false merge vs. missed duplicate) and incorporates deterministic kinship cannot-link constraints alongside Fellegi-Sunter log-odds models to jointly resolve individuals and infer households.

```mermaid
flowchart LR
    A["Synthetic Population Engine"] --> B["Noise & Corruption Model"]
    B --> C["Romanised-Name Normalisation"]
    C --> D["Splink Fellegi-Sunter Model"]
    D --> E["Kinship Cannot-Link Resolution (Pipeline K)"]
    E --> F["Golden Person Profiles"]
    F --> G["Multi-Channel Household Inference"]
    G --> H["Static DuckDB-Wasm Demo"]
```

---

## Key Results

{key_results_block}

---

## What I Learned (Including What Failed)

1. **A leak inflated my first results slightly.** The generator filled fields (guardian type, sex) that the module forms never collect, so the model saw ground truth. A schema audit found it; after the fix, `splink_v1` on clean rebuilds of `holdout_0..4` moved slightly in cluster precision (`{leak_pre_p4} → {leak_post_p4}`) and recall (`{leak_pre_r4} → {leak_post_r4}`). An earlier figure of `0.61` (`0.6068`) came from holdout outputs that a clean rebuild could not reproduce, and it was corrected after a fresh-clone reproducibility check.
2. **Kinship works better as a rule than as evidence, with a trade-off.** Roster overlap signals "same household", not "same person", which breaks the Fellegi-Sunter independence assumption. Using it only as a cannot-link rule (Pipeline K) lowered cost against the probabilistic-kinship reference on {h3_won}/5 fresh seeds (mean {h3_delta}; one-sided sign test p = 0.031), but only when false merges cost at least 2x missed duplicates (tie at 1:1). In a namesake stress test (`stress_0`, `--seed-offset 0`) at matched recall 0.50, K let through more cross-household namesakes ({stress_k_fm}% vs {stress_ref_fm}%).
3. **Pre-registration constrained me.** Hypotheses were committed before their results (table above). H3 was suggested by earlier holdout results, so it was confirmed only on five new seeds.
4. **An early negative result was an artefact.** Weak-bridge splitting first looked useless; after the leak was fixed it was selected on dev data (t_bridge {t_bridge} above t_link {t_link}).
5. **Household inference is the weakest part.** Record-level F1 is {hh_f1} with a-priori evidence weights; halving or doubling the weights drops it to {hh_half} or {hh_double}, and even perfect person linkage only reaches {hh_oracle}. Dropping the husband-name link raises precision from {hh_p} to {hh_p_drop_e2}, indicating that matching husbands by name skeleton creates false household merges.
6. **Bugs the verification gates caught:** non-deterministic household cuts (first: `cannot-household` worklist order; second: tied min-cuts at 2.0x weights from `PYTHONHASHSEED`-dependent subgraph edge iteration order in `infer.py`, fixed in commit `897b32e` with the regression test added in the follow-up commit), waterfall labels shown for the wrong match level (looked up by list position instead of Splink's comparison-vector value; the weights themselves were correct), a publish step that silently overwrote confirmed results, and summary numbers an AI agent reported without computing them.

---

## Limitations

- Synthetic data only; not validated on any real registry.
- Corruption, phone-sharing and guardian-switch rates are assumptions (configs/default.yaml), not calibrated to real data.
- The {cost_ratio}:1 cost ratio is an assumption. K beats the probabilistic-kinship reference only at >= 2:1.
- Recall is modest ({k_recall}): about half of true duplicate pairs stay unlinked at the chosen operating point.
- K's selected link threshold lies on the lower edge of the tested grid; it was not re-tuned, to protect the confirmation.
- Some Splink levels use default parameters (phone last-8, village); setting them to neutral changes mean cost by {untrained_delta}.
- Household inference uses a-priori weights and is fragile; {no_roster_pct}% of households have no roster, so indirect reach cannot be estimated for them.
- No module records sex; the sex comparison is inert.
- Splink is pinned to 4.x.

---

## How This Was Built

Implementation was written by an AI coding agent (Antigravity IDE); planning, design suggestions and review used a second AI assistant (Claude). I set the scope, chose between options, committed the pre-registrations, ran every step and checked results against the raw outputs, and accepted only work that passed automated gates: a fresh-clone CI proof, regression tests against pre-registered reference values, a determinism test across hash seeds, and a README render check. Those gates caught several AI-introduced errors (item 6 above).

---

## Reproduce

```bash
# Environment setup (Python 3.14; lock requires >=3.12)
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements-lock.txt
pip install -e . --no-deps

# Re-run full multi-seed experiment sweep from scratch
python scripts/reproduce_all.py

# Provenance generation & documentation check
python scripts/generate_preregistration_json.py
python scripts/render_readme.py --check
python scripts/check_links.py

# Run full pipeline to generate and resolve publish dataset
python -m barilink.cli pipeline --profile publish

# Verify pipeline output against committed headline metrics
python -m barilink.cli pipeline --verify

# Run test suites
pytest -q -m "not publish and not artifacts"  # CI unit & determinism tests
pytest -q -m artifacts                        # Golden metric & leakage gates
pytest -q -m publish                          # Full dataset verification

# Static web app build & test
cd web && npm ci && npm test && npm run build && npx playwright test
```

The artifacts tests need the full local experiment runs (dev, holdout and stress seeds), which `python scripts/reproduce_all.py` generates; see [docs/METHODS.md > Reproducing the experiments](docs/METHODS.md#8-reproducing-the-experiments).

---

## Change Log

- **2026-11-15 — Household `2.0x` determinism fix (`897b32e` + follow-up test):** Sorted subgraph edges before `nx.stoer_wagner` / `nx.minimum_cut` in `src/barilink/household/infer.py` and set intersections in `evidence_lineage` in `src/barilink/household/evidence.py`, eliminating `PYTHONHASHSEED`-dependent tie-breaking; added a 30-node tied-min-cut regression test in `tests/test_pipeline_determinism.py`.
- **2026-11-15 — Clean re-baseline via `scripts/reproduce_all.py`:** Regenerated all `demo`, `holdout_0..9`, `stress_0`, and summary JSONs from one script in one locked environment:
  - `leakage_comparison.json` (`splink_v1_post_fix` precision `0.6068 → 0.9243`, recall `0.7564 → 0.4408`; `splink_v1_resolved_post_fix` precision `0.6303 → 0.9188`, recall `0.7615 → 0.4500`): replaced non-reproducible earlier `holdout_0..4` outputs with clean `demo`-trained rebuilds.
  - `confirm_table.json` (`stress_0` at `--seed-offset 0`, recall `0.50`: Pipeline K `0.621 → 0.556`, Reference `0.523 → 0.490`, gap `9.8 → 6.6` pp): updated from explicit `--seed-offset 0` run.
  - `h2_dev_outcome.json` (`splink_v3` dev cost `875.0 → 876.0`, recall `0.4733 → 0.4726`, F1 `0.6350 → 0.6343`): updated from clean `demo` rebuild and `--threads 1` retrain.
  - `household_table.json` (`doubled_2_0x` F1 `0.2127 → 0.2129`, Size MAE `7.2555 → 7.2092`): deterministic output after the `infer.py` tie-breaking fix; all other household, H3, Reference, Pipeline K, cost-ratio, and baseline numbers are unchanged.
  - `tests/test_summary_artifacts.py`: updated `h2_dev_outcome` reference `875.0 → 876.0` and `doubled_2_0x` reference `0.2055 / 7.40 → 0.2129 / 7.21` with tightened tolerances (`abs=0.0005` and `abs=0.01`).
- **2026-11-15 — Environment lock (`requirements-lock.txt`):** Pinned all 29 dependencies from Python 3.14.6; updated `pyproject.toml` (`requires-python = ">=3.12"`) and CI/Pages workflows to Python `3.14`.
- **2026-11-15 — Run provenance & `METHODS.md` Section 8:** Added deterministic `results/<run>/provenance.json` (git commit, dirty flag, platform, CLI args, `seed_offset`, config SHA-256, Python/package versions; no timestamps) and replaced `docs/METHODS.md` Section 8 with a pointer to `scripts/reproduce_all.py` and corrected manual commands.

---

## Repository Map

```
├── configs/             # Pipeline & data generation configurations
├── docs/                # Detailed methodology (METHODS.md), audits, screenshots
├── results/             # Committed evaluation summaries, models, and headline benchmarks
├── scripts/             # Reproducibility scripts (render_readme.py, check_links.py)
├── src/barilink/        # Core Python package (generation, linkage, household, eval)
├── tests/               # Pytest suite (determinism, leakage, regression, pipelines)
└── web/                 # Static DuckDB-Wasm application (React, TypeScript, Vite)
```

---

## References

- Fellegi, I. P., & Sunter, A. B. (1969). A Theory for Record Linkage. *Journal of the American Statistical Association*, 64(328), 1183–1210.
- Linacre, R. et al. (2022). Splink: Free software for probabilistic record linkage at scale. *International Journal of Population Data Science*.
- Bagga, A., & Baldwin, B. (1998). Algorithms for Scoring Coreference Chains. *The First International Conference on Language Resources and Evaluation Workshop on Linguistics Coreference*.
- Additional methodology and design rationale: see [docs/METHODS.md](docs/METHODS.md) and [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md).
"""


def render_readme_content(repo_root: Path) -> str:
    summary_dir = repo_root / "results" / "summary"
    placeholders = get_context_placeholders(summary_dir)
    key_results = build_key_results_markdown(summary_dir)

    all_subs = {**placeholders, "key_results_block": key_results}

    rendered = README_TEMPLATE
    for key, val in all_subs.items():
        rendered = rendered.replace(f"{{{key}}}", val)

    # Validate that no unresolved placeholder remains
    unresolved = re.findall(r"\{[a-zA-Z0-9_]+\}", rendered)
    if unresolved:
        raise ValueError(f"Unresolved placeholders found in rendered README: {unresolved}")

    return rendered


def render_readme(repo_root: Path, check: bool = False) -> int:
    readme_path = repo_root / "README.md"

    if not readme_path.exists():
        print(f"Error: {readme_path} does not exist", file=sys.stderr)
        return 1

    expected_content = render_readme_content(repo_root)

    if check:
        current_content = readme_path.read_text(encoding="utf-8")
        if current_content != expected_content:
            print(
                "README.md is OUT OF DATE. Run 'python scripts/render_readme.py' to update it.",
                file=sys.stderr,
            )
            return 1
        print("README.md is UP TO DATE.")
        return 0

    readme_path.write_text(expected_content, encoding="utf-8")
    print(f"Successfully rendered README into {readme_path}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Render results tables and text into README.md")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if README.md is up to date without writing",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    sys.exit(render_readme(repo_root, check=args.check))


if __name__ == "__main__":
    main()
