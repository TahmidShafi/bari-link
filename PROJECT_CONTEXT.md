# Project Context: bari-link

[![CI](https://github.com/USER/bari-link/actions/workflows/ci.yml/badge.svg)](https://github.com/USER/bari-link/actions/workflows/ci.yml)

## 1. Executive Summary & Goal
`bari-link` is a portfolio project designed to perform **kinship-aware probabilistic deduplication** of NGO beneficiary registries in rural Bangladesh where no universal national identification numbers (NID) are available. 

In low-resource humanitarian and social safety net programs, beneficiaries frequently enroll across multiple specialized program modules (e.g., maternal nutrition vouchers, agricultural micro-subsidies, flood relief cash transfers). Each module maintains an independent registry with no common foreign key. Registries are heavily distorted by phonetic name spelling variations, honorific title insertions/deletions, missing or inaccurate birthdates, and shared mobile phones.

The core objective of `bari-link` is to **jointly resolve individuals AND households ("bari" / khana)** across fragmented enrolment modules by leveraging familial context—specifically paternal and spousal names and co-resident household-member overlap—as strong linkage evidence.

---

## 2. Planned End-to-End Pipeline
The project follows a modular, reproducible 6-stage pipeline:

```
[1. Generate]  Clean ground-truth synthetic population with kinship & geographic hierarchy
      │
[2. Corrupt]   Simulate realistic field survey noise (phonetic, prefixes, missing tokens)
      │
[3. Link]      Probabilistic record linkage via Splink (DuckDB backend, Fellegi-Sunter, EM)
      │
[4. Cluster]   Graph clustering (Union-Find + weak-bridge splitting / cut-edge pruning)
      │
[5. Golden]    Attribute fusion & canonical survivorship rules
      │
[6. Demo]      Interactive static browser application via DuckDB-Wasm on GitHub Pages
```

1. **Generate**: Synthesize a clean, fully known ground-truth rural Bangladeshi population structured into realistic households, preserving generational age gaps, gender distributions, kinship relationships, phone ownership patterns, and Zipf-Mandelbrot name frequencies.
2. **Corrupt**: Inject survey-level noise reflecting real-world administrative conditions:
   - Phonetic drift and transliteration inconsistencies (e.g., `Rahim` vs `Rohim`, `Khatun` vs `Khatoon`).
   - Prefix variations (e.g., adding/omitting `Md.`, `Mohammad`, `Mst.`, `Mosammat`).
   - Incomplete birth dates, estimated ages, and digitized typos.
   - Shared household mobile numbers versus personal mobile numbers.
3. **Link**: Probabilistic record linkage using [Splink](https://github.com/moj-analytical-services/splink) on an in-process DuckDB engine:
   - Fellegi-Sunter mathematical framework with Expectation-Maximization (EM) estimation of $m$ and $u$ probabilities.
   - Custom blocking rules balancing recall with pairwise comparison volume.
   - Kinship-feature integration: leveraging father's/husband's name comparisons and co-resident candidate matching.
4. **Cluster**: Graph entity resolution:
   - Construct an affinity graph where edges represent linkage probabilities above decision thresholds.
   - Run connected components (Union-Find) with weak-bridge / min-cut edge splitting to avoid transitive chaining of distinct entities.
5. **Golden Record**: Survivorship and entity consolidation:
   - Synthesize canonical entity profiles using rule-based survivorship (e.g., most complete records, most recent observation, canonical name selection).
6. **Static Web Demo**:
   - Zero-cost interactive deployment compiled to DuckDB-Wasm running entirely client-side in the browser on GitHub Pages.

### 2.1 Reproducing the Pipeline
All frozen pipeline stages can be executed and verified with single CLI commands:

```bash
# 1. Run the full publication pipeline (builds holdout_5, runs frozen Splink K, resolution, golden records, household inference, evaluation, and web export)
python -m barilink.cli pipeline --run-name holdout_5 --profile publish

# 2. Verify deterministic reproduction against committed reference metrics (asserts metrics within ±0.005 absolute tolerance)
python -m barilink.cli pipeline --verify

# 3. Fast CI smoke-test pipeline (uses configs/ci.yaml, 500 households, seed offset 9000)
python -m barilink.cli pipeline --profile ci

# 4. Standalone export of web data assets to web/public/data/
python -m barilink.cli export web --run-name holdout_5

# 5. Run test suite
pytest -q -m "not publish and not artifacts"  # Fast CI test suite (pure unit/tmp_path, zero external data)
pytest -q -m artifacts                       # Recorded experiment tests (requires local generated data/results)
pytest -q -m publish                         # Full publication pipeline data contract verification

# 6. Verify CI isolation in a clean temporary clone (workflow: commit locally -> run prove_ci.py -> push)
python scripts/prove_ci.py

# 7. Regenerate Vitest offline test fixtures from exported web data
python scripts/export_fixture.py

# 8. Web Application: install, lint, test, build, E2E smoke tests, and performance audit
npm ci --prefix web
npm run lint --prefix web
npm test --prefix web
npm run build --prefix web
npm run test:e2e --prefix web
npm run perf --prefix web  # Or node web/scripts/measure_perf.cjs
```

---

## 3. Inviolable Hard Rules
All contributors and automated agents working on `bari-link` must adhere to these five strict constraints across all pipeline stages:

1. **Synthetic Data Only**: Under no circumstances should real personal data, PII, or actual NGO/voter records be used or committed. All data is synthetically generated.
2. **Deterministic Reproducibility**: Given an integer seed, the entire pipeline must produce 100% byte-identical outputs across environments. No hidden random state or unseeded RNGs.
3. **No Ground-Truth Leakage**: Ground-truth identifiers (`person_id`, `household_id`) must NEVER be exposed to or used by feature engineering, blocking, or linkage models. They are strictly reserved for the downstream evaluation module to assess precision, recall, and F-beta metrics.
4. **Precision Over Recall (Asymmetric Loss)**: In humanitarian cash and voucher delivery, a false merge (merging two distinct vulnerable individuals into one, thereby denying assistance to one) is substantially more harmful than a missed duplicate (issuing redundant assistance). The linkage and clustering thresholds must prioritize high precision.
5. **Zero-Cost Stack**: Built entirely on zero-cost, open-source technology: Python 3.11+, DuckDB, Splink, PyArrow, GitHub Actions for CI, and GitHub Pages for web demonstration.

---

## 4. Decisions Log
This section records all architectural, demographic, and technical design decisions made throughout the project lifecycle.

### Log Entry 001: 2026-11-06 — Phase 1 Population Generator Architecture
- **Decision 1.1: Geographic Hierarchy**:
  Modeled a 4-tier geographic hierarchy: `district` > `upazila` > `union` > `village`. Configured 2 districts (`Kurigram` and `Gaibandha`), 3 upazilas each, 3 unions each, and 4 villages per union (72 total village communities). These northern riparian/char districts represent canonical operational zones for major poverty alleviation programs in Bangladesh.
- **Decision 1.2: Separation of Honorific Prefixes**:
  In Bangladeshi naming conventions, prefixes such as `Md.` / `Mohammad` (male) and `Mst.` / `Mosammat` (female) are honorific markers rather than intrinsic given names. In `name_pools.py`, these prefixes are isolated in distinct arrays and excluded from the clean ground-truth `given_name`. They will be dynamically injected during the subsequent corruption stage to simulate field survey variability. Full name is strictly defined as `given_name + " " + surname_or_title` (canonical, no prefix).
- **Decision 1.3: Zipf-Mandelbrot Name Distribution**:
  Modeled given name sampling via a power-law Zipf-Mandelbrot distribution where $P(k) \propto (k + q)^{-s}$, using assumed parameters $s = 1.1$ (`zipf_exponent`) and $q = 3.0$ (`zipf_offset`). These parameters are assumed rather than calibrated to published census name-frequency data, providing a controlled curve where the top-1 female name covers $< 12\%$ and the top-10 female names cover $> 30\%$ of the population. The pools were expanded to at least 100 canonical female and 100 canonical male Muslim given names, plus a 10% configurable Hindu minority pool.
- **Decision 1.4: Kinship, Marital Status, and Guardian Representation**:
  - `marital_status` values are strictly modeled as `{"married", "unmarried", "widowed", "separated"}`.
  - Individuals under age 15 are strictly `unmarried` and cannot have a `spouse_id`.
  - Female household heads are either `widowed` or `separated`.
  - Guardian rule: Every ever-married woman (`married`, `widowed`, `separated`) has `guardian_type="husband"` and `guardian_name=spouse_name` (late or absent husband). Unmarried women and all men have `guardian_type="father"` and `guardian_name=father_name`.
  - Every ever-married woman stores BOTH `father_name` and `spouse_name` in her record (the corruption step will later simulate survey-level guardian switching).
  - Referential integrity & name consistency:
    - If the father lives in the household, `father_name` strictly equals his full name (`given_name + " " + surname_or_title`).
    - If the head's elderly father lives in the household, the head's `father_id` points to him.
    - In female-headed households, the head's children have `father_id = null`, and their `father_name` strictly equals the head's `spouse_name` (ensuring sibling consistency for an absent/deceased father).
    - `mother_id` stores the resident mother's `person_id` (or `null`), subject to referential integrity.
- **Decision 1.5: Household Size Distribution**:
  Household sizes range from 2 to 8 members. The probability weights are assumed (target mean ~4.3) rather than claimed to be calibrated to BBS census data.
- **Decision 1.6: Mobile Phone Ownership**:
  Bangladeshi mobile phone numbers adhere strictly to the 11-digit regex `^01[3-9]\d{8}$`. Households have an 88% penetration rate (`household_phone`). Individual ownership is restricted to persons $\ge 15$ years old, with assumed penetration rates (60% adult male, 30% adult female).
- **Decision 1.7: Packaging and Output Formats**:
  - Used `src/` layout with `pyproject.toml` and standard virtual environment support.
  - Dual-output persistence: Apache Parquet (Snappy-compressed) for production performance and byte-identical reproducibility checks; CSV mirrors for rapid human inspection.

### Log Entry 002: 2026-11-06 — Phase 2 Enrolment Registries & Corruption Model
- **Decision 2.1: Enrolment Module Schemas**:
  Modeled four distinct administrative enrolment modules with heterogeneous MIS schemas:
  - `club_formation`: adolescent/young women (female, age 10-24 at enrolment). Collects `member_name`, `age`, `guardian`, `village`.
  - `upg_enrolment` (Ultra-Poor Graduation): household-level, primary participant (adult female 18-60) + full household roster in `rosters.parquet`. Collects `participant_name`, `age`, `guardian_name`, `guardian_type`, `phone`, full location.
  - `microfinance_group`: microcredit borrowers (mostly female 18-60) with `group_id`. Collects `borrower_name`, `husband_or_father`, `phone`, `village`, `union`, `group_id`.
  - `livelihood_support`: income-generation grants (adults 18-60, both sexes) + short roster (head plus up to 3 members). Collects `recipient_name`, `age`, `father_name`, `phone`, full location.
  A single harmonised table `records.parquet` provides a common schema across all modules; uncollected fields are structurally null.
- **Decision 2.2: Normalisation Leakage Guard (Transliteration Rule Partitioning)**:
  To prevent target leakage into the downstream record-linkage normalisation module (Phase 3), transliteration rules are strictly split:
  - `SHARED_RULES` (46.2% of rules): standard transliteration alternations (`sh`<->`s`, `kh`<->`k`, `ph`<->`f`, `j`<->`z`, `v`<->`b`, `ee`<->`i`, `oo`<->`u`, `e`<->`i`, `Rahman`<->`Rehman`, `Mohammad`<->`Muhammad`).
  - `GENERATOR_ONLY_RULES` (53.8% of rules, target $\ge 40\%$): generator-private rules including `a`<->`o`, `u`<->`o`, `Uddin`<->`Uddeen`<->`Udin`, `Ali`<->`Oli`, `Mia`<->`Miah`, `Chowdhury`<->`Choudhury`, `Hossain`<->`Hussain`, compound name joining/splitting (`Abdul Karim`<->`Abdulkarim`).
  - Tested: Generator-only rules must account for $\ge 30\%$ of all transliteration events logged in `truth/corruption_log.parquet` (empirically observed: ~51%).
- **Decision 2.3: Corruption Rates Assumption**:
  All corruption rates in `configs/default.yaml` (transliteration: 0.22, prefix drift: 0.35, title drift: 0.12, typos: 0.08, guardian switch: 0.18, age heaping base: 0.25, age jitter: 0.20, phone missing: 0.15, phone shared: 0.20, phone typo: 0.06, transposition: 0.05, format variants: 0.30, location village drift: 0.15, missing admin: 0.08) are explicitly **assumed, not empirically calibrated**.
- **Decision 2.4: Guardian Switch Restriction**:
  In accordance with rural field practices, guardian switching (recording father's name instead of husband's name) is strictly restricted to ever-married women (`marital_status in {"married", "widowed", "separated"}`). Widows whose guardian is their late husband are also subject to a "Late " prefix insertion rate. Unmarried women and men are never subjected to guardian switching.
- **Decision 2.5: Age Heaping and No Birth Year Output**:
  Field survey programs collect reported age at enrolment, not birth date. Recorded age is subjected to age heaping (rounding to multiples of 5 with probability increasing with age) and small random jitter ($\pm 1$–$3$ years). Corrupted birth year is strictly omitted from registry tables.
- **Decision 2.6: Hard Negatives (Doppelgangers)**:
  To test the linkage model's vulnerability to false merges (Hard Rule 4: precision over recall), we identify and enroll distinct individuals sharing canonical `(given_name, guardian_name, village)`. Configured with `min_pairs: 50`. If natural occurrences in the clean population are insufficient, cousin households are generated via the Phase 1 generator logic and marked with `is_injected = True` in `truth/doppelganger_pairs.parquet`.
- **Decision 2.7: Strict Truth Segregation & Opaque Record IDs**:
  - Model-visible outputs in `data/generated/<run>/registry/` contain zero ground-truth identifiers or canonical names.
  - Every record is assigned an opaque 10-character hex `record_id` redrawn on collision, with Spearman rank correlation with `person_id` verified to satisfy $|\rho| < 0.05$.
  - All evaluation keys, pairwise ground-truth matches, doppelgangers, and corruption logs are segregated in `data/generated/<run>/truth/`.

### Log Entry 003: 2026-11-06 — Phase 2 Audit Alignments & Hard Negative Refinements
- **Decision 3.1: Household Given-Name Uniqueness & Father-Son Differentiation**:
  - Enforced nominal uniqueness within each household ("bari"): no two co-resident members may share a `given_name`.
  - Enforced that a son's `given_name` must differ from his father's `given_name` (both when the father is resident and when the father is absent or deceased, as in female-headed households).
  - Rejection resampling deterministically draws names with a maximum of 200 attempts before raising a descriptive `RuntimeError`. Rejection resampling approximately preserves the Zipf-Mandelbrot rank distribution across households.
  - Added clean column `father_given_name` to `persons.parquet` (evaluation truth only), populated from resident father records or sampled absent father names. Used directly (never via string splitting) for kinship rules, and added to the registry leakage-guard blacklist.
- **Decision 3.2: Eligibility Evaluated at Enrolment Date**:
  - Enrolment eligibility is evaluated at each beneficiary's sampled enrolment date (`enrolment year - birth_year`), rather than using `age_at_reference_date`. The eligible pool for audit equals the population eligible at their drawn date.
- **Decision 3.3: Enrolment Base Sizing & Integrated Conditional Overlap**:
  - `target_share` strictly represents the fraction of the defined eligible pool for each module.
  - Conditional cross-module overlaps (`UPG -> microfinance`, `UPG -> livelihood`) are a priority subset of the target rather than added on top: UPG-conditional candidates are enrolled first, and general eligible candidates top up to `round(target_share * eligible_pool)`. Realised shares are verified within $\pm 2$ percentage points of `target_share`.
  - Microfinance pool: eligible pool = women aged 18–60 at enrolment date (`target_count_female = round(target_share * pool)`). Male borrowers are a separate quota: `round(target_count_female * male_share / (1 - male_share))` where `male_share = 0.08`, drawn from men aged 18–60. Realised share test applies to the female pool; male quota is reported separately.
- **Decision 3.4: Cross-Household Doppelgangers (Hard Negatives)**:
  - Doppelgangers are strictly defined as distinct individuals living in *different* households (`person_id_1 != person_id_2` AND `household_id_1 != household_id_2`) who share canonical `(given_name, guardian_name, village)`. Co-residents sharing a name/guardian are excluded as family members.
  - Person pairs and record pairs are reported separately (one person pair produces $K_1 \times K_2$ record pairs). If natural person pairs $< 50$, injection creates cousin households in the same village and marks them `is_injected = True`.
- **Decision 3.5: Persistent Summary Reporting**:
  - Complete CLI summary output (including Enrolment Base Audit, Doppelganger Audit with 3 side-by-side examples, Post-Fix Name Frequency Shares, Corruption Frequency Table, and 5 multi-record clusters) is persisted to `data/generated/<run>/summary.txt`.
- **Decision 3.6: Test Output Isolation**:
  - All test suites write transient outputs strictly to pytest's `tmp_path`, preserving `data/generated/demo` for explicit CLI runs.

### Log Entry 004: 2026-11-06 — Phase 3 Evaluation Harness & Non-ML Baselines
- **Decision 4.1: Two-Level Pairwise Evaluation Framework**:
  - Formulated two distinct pairwise evaluation levels:
    - **Cluster-Level (Headline)**: Every pair of records $(r_i, r_j)$ co-occurring within the same predicted connected-component cluster counts as a predicted entity match. All primary metrics ($TP, FP, FN, P, R, F_1$), asymmetric cost, $t_{\text{cost}}$, and $t_{\text{p99}}$ operate on cluster-level pairs.
    - **Edge-Level (Diagnostic)**: Only scored candidate edges with $p \ge t$ are counted, reported as `edge_precision`, `edge_recall`, and `edge_f1` to evaluate pairwise classifier discrimination prior to graph closure.
  - The recall and false negative denominator is strictly fixed to ALL ground-truth pairs in `truth/true_pairs.parquet` (including pairs omitted by candidate blocking).
- **Decision 4.2: Asymmetric Cost Model & Monotonic Operational Thresholds**:
  - Cost function: $\text{expected\_cost}(t) = c_{\text{fm}} \cdot FP_{\text{cluster}}(t) + c_{\text{md}} \cdot FN_{\text{cluster}}(t)$ with weights $c_{\text{fm}} = 5.0$ and $c_{\text{md}} = 1.0$. These parameters are explicitly **assumed, not empirically calibrated**, reflecting the core humanitarian premise (Hard Rule 4) that false merges (denial of aid to distinct individuals) cause 5x greater harm than missed duplicates (issuing redundant aid).
  - $t_{\text{cost}}$ selects $\operatorname{argmin}_t \text{expected\_cost}(t)$ (ties broken towards higher thresholds).
  - $t_{\text{p99}}$ enforces a monotonic suffix constraint: the lowest threshold $t$ where cluster precision $\ge 0.99$ at $t$ and at every threshold above $t$. If precision never reaches 0.99, $t_{\text{p99}} = \text{null}$ with a recorded explanation in `metrics.json` and `report.md`.
- **Decision 4.3: Incremental Disjoint Set Union (DSU) Sweep**:
  - Candidate pairs are sorted once by probability descending.
  - As decision threshold decreases from $0.99$ to $0.01$ (in 0.01 decrements), components are joined incrementally via `UnionFind` with path compression.
  - Each component root maintains component size, a `Counter` of `person_id -> record count`, and sum of squared counts. When merging root $A$ and root $B$, new cluster pairs ($|A| \cdot |B|$) and new true positive matches ($\sum_p A[p] \cdot B[p]$) are accumulated in $O(1)$ and smaller counters are merged into larger counters in $O(\min(|A|, |B|))$.
  - Computes exact B-cubed $F_1$, false-merge clusters, minority false-merged records, doppelganger false-merge rate, and deduplicated reach across all 99 thresholds in $< 0.5$ seconds without re-clustering.
- **Decision 4.4: Development vs. Holdout Protocol**:
  - Separation between exploration and testing:
    - Development run (`demo`, seed 42): used for threshold selection (`evaluate --mode select`), generating `results/<method>/selected_thresholds.json`.
    - Holdout run (`holdout`, seed 1042 via `--seed-offset 1000`): used for frozen reporting (`evaluate --mode report`). `report` mode strictly requires `selected_thresholds.json` and prohibits re-tuning.
  - `manifest.json` tracks `"role": "dev" | "holdout"`. `select` mode raises a descriptive error if invoked on a holdout run.
  - `report` mode logs the dev source run name and the cryptographic SHA-256 hash of `selected_thresholds.json` directly into `metrics.json` and `report.md`.
- **Decision 4.5: Non-ML Baseline Deduplication Performance**:
  - Benchmarked three non-ML baselines over a standardized blocking filter (same cleaned village OR same normalized 11-digit mobile phone):
    - `exact`: Exact match on normalized `full_name`, `guardian_name`, and `village`. On holdout: Precision = 97.69%, Recall = 8.65%, B-cubed F1 = 0.8756, Doppelganger FM Rate = 3.37%, Reach Error = +28.67%.
    - `phone`: Match on identical 11-digit mobile phone. On holdout: Precision = 81.55%, Recall = 9.33%, B-cubed F1 = 0.8748, Doppelganger FM Rate = 0.00%, Reach Error = +27.68%.
    - `exact_or_phone`: Union baseline. On holdout: Precision = 87.50%, Recall = 17.15%, B-cubed F1 = 0.8865, Doppelganger FM Rate = 3.37%, Reach Error = +24.77%.
  - Persisted comparison results to `results/holdout/baseline_comparison.md`. The high reach errors (+24.77% to +28.67%) confirm that non-ML heuristics miss $> 82\%$ of duplicate beneficiaries, necessitating Phase 4 probabilistic record linkage.
- **Decision 4.6: Truth Directory Security Scan**:
  - Implemented an AST-based static analysis test verifying that only `barilink.evaluate`, `barilink.generate`, and `barilink.corrupt` ever reference the `truth/` directory as a path component, ignoring comments and docstrings.

### Log Entry 005: 2026-11-06 — Phase 4 Normalisation & Splink Probabilistic Record Linkage
- **Decision 5.1: Strict Normalisation & Canonicalisation Order**:
  - Implemented `barilink.link.normalise` to engineer features strictly from model-visible files (`records.parquet`, `rosters.parquet`) writing to `features.parquet`.
  - Strip honorific prefixes (`md`, `mohammad`, `mohd`, `mst`, `most`, `mosammat`, `late`).
  - Extracted trailing female titles (`khatun`, `khatoon`, `begum`, `akter`, `bibi`, `rani`, `bala`) into canonical classes (`khatoon` -> `khatun`), stripping them from `name_clean`.
  - Canonicalisation executed in strict hierarchical order:
    1. Multi-character substitutions first (`oo->u`, `ee->i`, `ph->f`, `kh->k`, `sh->s`, `rehman->rahman`, `muhammad/mohammed->mohammad`).
    2. Single-character substitutions second (`o->a`, `e->i`, `z->j`, `v->b`).
    3. Removal of whitespace and hyphens.
  - This sequence guarantees `"Khatoon"` resolves to `"katun"` rather than `"khataan"`. `"Rohima"` and `"Rahima"` resolve to `"rahima"`, while `"Kolsum"` and `"Kulsum"` remain distinct (`"kalsum"` != `"kulsum"`), respecting generator-private rules.
  - Tokens sorted alphabetically (`name_tokens_sorted`) provide token transposition invariance (`"Mia Abdul Karim"` == `"Abdul Karim Mia"`).
- **Decision 5.2: Kinship Comparison Redesign (No Double Counting)**:
  - Replaced legacy scalar kin names with `roster_skels`: an array of consonant skeletons of household roster members ONLY from `rosters.parquet`. Set to `NULL` for records without rosters, and strictly omits the beneficiary's own guardian to prevent double-counting guardian evidence.
  - Formulated 5 null-safe comparison levels in DuckDB SQL:
    a) Both rosters null (`roster_skels_l IS NULL AND roster_skels_r IS NULL`, marked `is_null_level = True`)
    b) Roster intersection size $\ge 2$
    c) Cross-household guardian match: `list_contains(roster_skels_l, guardian_skeleton_r) OR list_contains(roster_skels_r, guardian_skeleton_l)`
    d) Roster intersection size $\ge 1$
    e) Else level
- **Decision 5.3: Splink 4 Probabilistic Model & Blocking Rules**:
  - Configured 9 Fellegi-Sunter comparisons in DuckDB: `given_name`, `guardian_name`, `kinship`, `phone`, `birth_year`, `village`, `union`, `sex`, and `title_token`.
  - Established 5 prediction blocking rules:
    1. `given_first_skel + village_canon`
    2. `phone_norm`
    3. `guardian_skeleton + village_canon`
    4. `name_skeleton + union_raw`
    5. `given_first_skel + birth_year_est`
  - Scored candidates counted via `splink.blocking_analysis.cumulative_comparisons_to_be_scored_from_blocking_rules_data` (49,984 candidate pairs on `demo`, 45,507 on `holdout`).
- **Decision 5.4: Unsupervised Fellegi-Sunter Training & Dev/Holdout Separation**:
  - Model trained on `demo` only, using deterministic rule (`phone_norm` & `name_skeleton`, recall 0.60) for prior probability, random sampling ($2 \times 10^6$ pairs) for $u$-probabilities, and two Expectation-Maximisation sessions (Session A: `phone_norm`; Session B: `name_skeleton + village_canon`).
  - Saved model to `results/models/splink_v1/model.json`.
  - Holdout predictions load the saved model without retraining. Both `demo` and `holdout` evaluate at frozen operational threshold $t_{\text{cost}} = 0.99$.
- **Decision 5.5: Benchmarking & Error Analysis**:
  - Implemented `no_link` baseline (empty predictions; cluster precision 1.0, recall 0.0, reach error +32.03%).
  - On unseen holdout data, `splink_v1` achieves Cluster Precision = 90.17%, Cluster Recall = 53.10% (>3x gain over best baseline `exact_or_phone` at 17.15%), B-cubed F1 = 0.9319, Doppelganger False-Merge Rate = 1.12%, Deduplicated Reach Error = +12.77% (down from +24.77%), and expected operational cost 1,114.0 (down from 1,397.0).
  - Diagnostic charts exported to `results/holdout/splink_v1/charts/` (`match_weights.html`, `m_u_parameters.html`).
  - Error analysis report persisted to `results/holdout/splink_v1/error_analysis.md`, attributing false merges and blocking failures across 161 unblocked true pairs (11.31%).

### Log Entry 007: 2026-11-07 — Phase 5 Entity Resolution, Kinship Golden Records & Clerical Review
- **Decision 7.1: Unshifted Min-Cut Capacity & Multi-Edge Bias Prevention**:
  - In Step 2 (cannot-link constraint enforcement), edge capacity in the component subgraph is defined strictly as $c(e) = w(e)$ without additive constant shifts ($c(e) > 0$ is guaranteed since all edges have $w \ge t_{\text{link}} \ge 2.0$).
  - An additive shift $C > 0$ ($c(e) = w(e) + C$) would penalize an $s$-$t$ cut with $k$ edges by $k \cdot C$, biassing the min-cut toward cutting a single strong edge ($W + C$) rather than multiple weak edges ($\sum w_i + k \cdot C$). With unshifted capacity, min-cut reliably cuts weak parallel chains separating incompatible records (verified via 4-node unit test cutting two weight 3.0 edges instead of a weight 12.0 edge).
- **Decision 7.2: 4-Step Graph Entity Resolution & Dev Grid Parameter Sweep**:
  - Implemented the deterministic 4-step resolution pipeline:
    1. *Step 1*: Connected components on edges with $w \ge t_{\text{link}}$, evaluated in sorted node order.
    2. *Step 2*: Cannot-link constraints (sex conflict, estimated birth year gap > 10 years, and oracle clerical splits) severed iteratively via minimum $s$-$t$ cut with unshifted capacity.
    3. *Step 3*: Weak bridge pruning using `nx.bridges` on components with $\ge 3$ records where bridge weight $w < t_{\text{bridge}}$, cutting the weakest bridge first and iterating until all remaining bridges meet or exceed $t_{\text{bridge}}$.
    4. *Step 4*: Deterministic SHA-256 hashed cluster identifiers based on sorted member lists.
  - Performed a 2D parameter grid sweep on `demo` over $t_{\text{link}} \in [2.0, 9.0]$ (step 0.5) and $t_{\text{bridge}} \in [t_{\text{link}}, 16]$ (integer steps) to minimize asymmetric operational cost (5:1 false merge to missed duplicate penalty).
  - Optimum on `demo` selected $t_{\text{link}} = 9.0, t_{\text{bridge}} = 9.0$ (min cost 892.0, cluster precision 96.57%, recall 45.44%, F1 0.6180, doppelganger false-merge rate 0.0%). The global minimum landed on the $t_{\text{bridge}} = t_{\text{link}}$ baseline, where cannot-link constraint cuts alone (3 cuts) optimize cost, with $t_{\text{bridge}} = 10.0$ close behind (cost 893.0, precision 97.31%, 17 bridge cuts).
- **Decision 7.3: Multi-Seed Holdout Evaluation with Frozen Thresholds**:
  - Evaluated `splink_v1_resolved` in report mode across all 5 independent holdout seeds (`holdout_0` .. `holdout_4`) using frozen thresholds $t_{\text{link}} = 9.0, t_{\text{bridge}} = 9.0$.
  - Relative to raw `splink_v1`, entity resolution improved Cluster Precision to $0.9484 \pm 0.0067$ (up from $0.9404 \pm 0.0081$) and Cluster F1 to $0.6320 \pm 0.0107$ (up from $0.6303 \pm 0.0105$), maintaining pair completeness at $89.04\%$ and pooled doppelganger false-merge rate at $1.89\%$ [Wilson 95% CI: $0.92\%, 3.85\%$].
  - Precomputed UI threshold clusterings for `holdout_0` across all $t_{\text{link}}$ values, exported to `resolved_by_threshold.parquet`.
- **Decision 7.4: Kinship Golden Records Survivorship & Disambiguation**:
  - Built canonical golden records per resolved cluster with complete JSON lineage and attribute provenance.
  - Resolved female beneficiary guardian switches across modules (e.g. unmarried beneficiary reporting father $\to$ married beneficiary reporting husband) by persisting `father_name` and `husband_name` into distinct dedicated columns, rather than overwriting a generic `guardian_name`.
  - Selected median estimated birth year to protect against single-module age heaping and recall bias.
  - Evaluated against majority ground-truth identity on `holdout_0`: Title-free canonical name accuracy = 78.62%, Title accuracy = 81.04%, Birth year mean error = 0.71 years (median error = 0.0 years), Phone accuracy among clusters with phone = 48.94% (matches person's own phone) and 80.60% (matches person's own OR household phone), cluster impurity rate = 0.57%.
- **Decision 7.5: Budgeted Clerical Review & Active Learning Monotonicity**:
  - Constructed an uncertainty-ranked review queue prioritising cut edges first, followed by boundary candidate pairs sorted by ascending distance $|w - t_{\text{link}}|$ within a $\pm 6.0$ window.
  - Simulated active clerical review across budgets $K \in \{0, 50, 100, 250, 500\}$ pairs per 10k records, dynamically injecting oracle must-link ($w = 1000.0$) and cannot-link constraints.
  - On `holdout_0`, expected operational cost decreased strictly monotonically from 951.0 down to 778.0, while Cluster F1 rose from 0.6194 to 0.6809. At $K = 500$, review confirmed 201 true merges and severed 39 false merges.
- **Decision 7.6: Structural Limitation of Bridge Detection**:
  - Documented algorithmic limitation: `nx.bridges` finds single-edge cuts (bridges). If two dense cliques are erroneously joined by 2 or more weak parallel edges, neither edge is mathematically a bridge. Consequently, weak-bridge splitting cannot sever multi-edge spurious connections; they rely entirely on hard cannot-link constraints (sex or birth year conflicts) or escalation to clerical review.

### Log Entry 008: 2026-11-07 — Phase 6 Pre-Registration H1: Model v2 Guardian Disambiguation & Dev Error Diagnosis
- **DEV Error Diagnosis on `demo` (at $t_{\text{cost}} = 9.25$)**:
  - Evaluated 49,984 candidate pairs (1,263 candidate true pairs). Observed 708 missed candidate true pairs (56.1% FN at candidate level) and 23 false merges.
  - Missed true candidate pairs breakdown:
    - *Guardian type combination*: `both null` (396, 55.93%) and `null/known` (308, 43.50%) account for 99.4% of missed true candidates, as only UPG collected guardian type.
    - *True guardian switch*: 245 pairs (34.60%) had true guardian switch events.
    - *Module pair*: Livelihood Support vs Microfinance Group (270, 38.14%), Microfinance Group vs UPG Enrolment (229, 32.34%), Livelihood Support vs UPG Enrolment (75, 10.59%).
    - *Null count across pair*: Centered at 8–9 null fields (47.3% have 8–9 nulls out of 20 fields).
    - *Most damaging Bayes factors*: `kinship` (364, 51.41%) and `guardian_name` (137, 19.35%) most severely depressed match weights below $t_{\text{cost}}$.
  - False merges breakdown (23 pairs): 100% occurred within the same household (20 Sibling pairs [87.0%], 3 Parent-Child pairs [13.0%]), driven by shared kinship rosters (100%), union (100%), village (100%), and parental names (95.7%).
- **Pre-Registration Hypothesis H1 & Decision Rule**:
  > H1: Missed duplicates are concentrated in pairs whose guardian fields refer to different relationships (father vs husband, or unknown). A guardian comparison that separates "names differ, guardian types differ or unknown" from "names differ, same guardian type" will raise dev recall at fixed precision. Decision rule: adopt v2 if dev expected cost at its own t_cost is lower than v1's by >= 2%; otherwise keep v1 and report H1 as not supported.
  - Unresolved reference baseline: $C_{\text{v1}} = 960.0$ at $w = 9.25$.
  - Adoption cost threshold: $0.98 \times 960.0 = 940.8$.
  - If `splink_v2` achieves dev expected cost $\le 940.8$, adopt v2; otherwise keep v1. If adopted, evaluate `splink_v2_resolved` against `splink_v1_resolved` separately.
- **Outcome of Hypothesis H1**:
  - `splink_v2` trained exactly as pre-registered on `demo`. On the match-weight grid, `splink_v2` selected optimal threshold $t_{\text{cost}} = 9.25$ ($p \approx 0.998360$, $t_{\text{p99}} = 17.25$).
  - Dev expected operational cost: **$C_{\text{v2}} = 937.0$** (Cluster Precision = 0.9508, Cluster Recall = 0.4614, Cluster F1 = 0.6213).
  - Relative to $C_{\text{v1}} = 960.0$, expected cost decreased by **$2.40\%$** (23.0 cost points), beating the $2\%$ pre-registered threshold ($937.0 \le 940.8$).
  - **Verdict**: **Hypothesis H1 is SUPPORTED**. Model `splink_v2` is **ADOPTED** as the baseline for Model v3.

### Log Entry 008a: 2026-11-07 — Phase 6 Ground-Truth Leakage Audit & Metric Re-baselining
- **Leakage Finding & Root Cause**:
  - Pre-implementation schema audit discovered ground-truth attribute leakage into `registry/records.parquet`:
    1. `guardian_type_raw` was populated with `"father"` for all 2,179 `livelihood_support` records, despite `livelihood_support.csv` having only a `father_name` column and no guardian type field.
    2. `sex_raw` was populated across all 4,798 records, despite no raw module CSV collecting beneficiary sex.
  - **Status of Pre-Fix Metrics**: All pre-fix Splink metrics (from Phase 4, Phase 4b, and Phase 5) are **invalid** because models were trained and evaluated on leaked features not present in real administrative survey schemas.
- **Remediation**:
  - Updated `src/barilink/corrupt/registry.py` to enforce that `final_guardian_type` is non-null ONLY for `upg_enrolment`, and `final_sex` is `None` for all records. Added `test_harmonised_columns_match_module_schema` to lock this schema contract permanently. Rebuilt `demo` and all holdouts `holdout_0` .. `holdout_4`.
- **Before / After 5-Seed Holdout Comparison**:

| Method | Status | Cluster Precision (mean ± sd) | Cluster Recall (mean ± sd) | Cluster F1 (mean ± sd) | Doppelganger FM Rate [Wilson 95% CI] | Reach Error % (mean ± sd) | Review Pairs / 10k | Operational Thresholds |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `splink_v1` | Pre-Fix (Leaked) | 0.9404 ± 0.0081 | 0.4741 ± 0.0122 | 0.6303 ± 0.0105 | 1.89% [0.92%, 3.85%] | +14.85% ± 0.69% | 2,031.1 | $w=9.00$ ($p=0.998051$) |
| `splink_v1` | Post-Fix (Clean) | 0.6068 ± 0.0421 | 0.7564 ± 0.0106 | 0.6728 ± 0.0266 | 16.76% [13.30%, 20.90%] | -1.22% ± 0.87% | 6,919.2 | $w=9.25$ ($p=0.998360$) |
| `splink_v1_resolved` | Pre-Fix (Leaked) | 0.9484 ± 0.0067 | 0.4740 ± 0.0123 | 0.6320 ± 0.0107 | 1.89% [0.92%, 3.85%] | +14.97% ± 0.69% | 0.0 (placeholder) | $t_{\text{link}}=9.0, t_{\text{bridge}}=9.0$ |
| `splink_v1_resolved` | Post-Fix (Clean) | 0.6303 ± 0.0327 | 0.7615 ± 0.0090 | 0.6893 ± 0.0197 | 16.22% [12.81%, 20.32%] | -1.32% ± 0.80% | 4,326.4 | $t_{\text{link}}=8.5, t_{\text{bridge}}=10.0$ |

- **Reversal of Phase 5 Bridge-Splitting Finding**:
  - In Phase 5 on leaked data, grid sweep selected $t_{\text{bridge}} = t_{\text{link}} = 9.0$, leading to the conclusion that weak-bridge splitting did not improve cost.
  - On clean data, this finding **reversed**: dev grid search selected $t_{\text{link}} = 8.5, t_{\text{bridge}} = 10.0$ (strictly interior, $t_{\text{bridge}} > t_{\text{link}}$), cutting 23 weak bridges and lowering expected operational cost from 963.0 (no-bridge baseline) to 961.0.
- **Inert Sex Constraint Note**:
  - Because no module schema collects sex, `sex_raw` is null everywhere in `records.parquet`. Consequently, the sex cannot-link constraint in resolution is currently **inert** (it never fires). This is intentional and documented; fixing survey module schemas to collect sex is out of scope for H1/H2.

### Log Entry 008b: 2026-11-07 — Phase 6 Pre-Registration H2: Model v3 Household vs Individual Kinship Disambiguation
- **Pre-Registration Hypothesis H2 & Decision Rule**:
  > H2: Roster overlap identifies households, not persons, and the current kinship null rule penalises pairs where only one record has a roster. Model v3 changes ONLY the kinship comparison of the model adopted after testing H1:
  >  (i) roster entries matching the record's own name_canon are removed from that record's roster arrays;
  >  (ii) a new FIRST kinship level 'listed_as_other_member': l.name_skeleton is in r.roster_skels or r.name_skeleton is in l.roster_skels;
  >  (iii) the null level applies when EITHER roster is null (unless level ii or the guardian cross-check fires);
  >  (iv) the remaining levels are unchanged.
  > Decision rule: adopt v3 if its dev expected cost at its own t_cost is at least 2% lower than the model adopted after H1. Secondary outcome (reported, not decisive): the number of dev false merges between same-household persons.
- **Deterministic Resolution Constraint**:
  - In entity resolution, pairs where `listed_as_other_member` fires become a deterministic **cannot-link constraint** (applied only for v3 and its resolved variant `splink_v3_resolved`). If record A's name skeleton is listed as an other member in record B's roster (or vice versa), they are proven to be distinct co-residents of the same household and cannot be merged.
- **Outcome of Hypothesis H2**:
  - `splink_v3` trained on top of `splink_v2` on `demo` with self-filtered roster arrays and kinship v3 levels. On the match-weight grid, `splink_v3` selected optimal threshold $t_{\text{cost}} = 8.00$ ($p \approx 0.996109$, $t_{\text{p99}} = 20.00$).
  - Dev expected operational cost: **$C_{\text{v3}} = 875.0$** (Cluster Precision = 0.9642, Cluster Recall = 0.4733, Cluster F1 = 0.6350).
  - Relative to $C_{\text{adopted}} = C_{\text{v2}} = 937.0$, expected cost decreased by **$6.62\%$** (62.0 cost points), substantially exceeding the $2\%$ pre-registered threshold ($875.0 \le 918.26$).
  - **Secondary Outcome**: False merges between same-household persons dropped from 29 (in v2) to **20** (in v3), with total false merges falling from 30 to 21.
  - **Verdict**: **Hypothesis H2 is SUPPORTED**. Model `splink_v3` is **ADOPTED** as the primary champion model.

### Log Entry 008c: 2026-11-07 — Phase 6 Model v3 Resolution, Systematic Ablations, and Doppelganger Stress Test
- **Resolution Parameter Selection for Champion Model (`splink_v3_resolved`)**:
  - Swept the 2D resolution grid on `demo` over $t_{\text{link}} \in [2.0, 14.0]$ (step 0.5) and $t_{\text{bridge}} \in [t_{\text{link}}, 16]$ (integer steps) with deterministic `listed_as_other_member` cannot-link cuts.
  - Selected optimal thresholds: $t_{\text{link}} = 6.5, t_{\text{bridge}} = 8.0$ (strictly interior, not on boundary).
  - Dev expected operational cost decreased from 875.0 (unresolved `splink_v3`) to **830.0** (min cost, Cluster Precision = 96.53%, Recall = 50.84%, F1 = 0.6661, Doppelganger FM rate = 0.0%).
- **Multi-Seed Holdout Ablations (5 Independent Seeds: `holdout_0` .. `holdout_4`)**:
  - Evaluated all 5 ablation variants plus `splink_v3_resolved` at frozen dev-selected thresholds:
    1. `splink_v1` ($w=9.25, p=0.9984$): Precision = $0.6068 \pm 0.0421$, Recall = $0.7564 \pm 0.0106$, F1 = $0.6728 \pm 0.0266$, Doppelganger FM Rate = $16.76\%$ [$13.30\%, 20.90\%$].
    2. `splink_v2` ($w=9.25, p=0.9984$): Precision = $0.9144 \pm 0.0197$, Recall = $0.4923 \pm 0.0180$, F1 = $0.6397 \pm 0.0127$, Doppelganger FM Rate = $1.35\%$ [$0.58\%, 3.12\%$].
    3. `splink_v3` ($w=8.00, p=0.9961$): Precision = $0.9439 \pm 0.0050$, Recall = $0.5107 \pm 0.0159$, F1 = $0.6627 \pm 0.0126$, Doppelganger FM Rate = $1.89\%$ [$0.92\%, 3.85\%$].
    4. `splink_v3_no_tf` ($w=7.75, p=0.9954$): Precision = $0.9381 \pm 0.0071$, Recall = $0.5142 \pm 0.0185$, F1 = $0.6641 \pm 0.0141$, Doppelganger FM Rate = $2.97\%$ [$1.67\%, 5.24\%$].
    5. `splink_v3_no_kinship` ($w=1.25, p=0.7040$): Precision = $0.9424 \pm 0.0084$, Recall = $0.6164 \pm 0.0186$, F1 = $0.7452 \pm 0.0125$, Doppelganger FM Rate = $1.89\%$ [$0.92\%, 3.85\%$] (on low-density holdouts).
    6. `splink_v3_resolved` ($t_{\text{link}}=6.5, t_{\text{bridge}}=8.0$): Precision = **$0.9500 \pm 0.0071$**, Recall = **$0.5488 \pm 0.0185$**, F1 = **$0.6956 \pm 0.0157$**, Paired $\Delta F_1$ vs v1 = **$+0.0228 \pm 0.0356$** (individual seed deltas: `[-0.0245, -0.0014, +0.0481, +0.0296, +0.0622]`).
- **Doppelganger Stress Test on `stress_0` (`min_pairs: 400`)**:
  - Population synthesized with `configs/stress.yaml` creating 559 total doppelganger person pairs (60 natural pairs from demographic name collision, 499 injected hard negative pairs within same village/union).
  - Doppelgangers have near-zero roster overlap (mean 0.43 members, maximum 1 member, only 21/559 pairs with rosters on both records), whereas true co-residents exhibit overlap $\ge 2$.
  - Stress outcomes across methods:
    - Natural pairs: 2/60 (3.3%) merged across all kinship models, rising to 4/60 (6.7%) for `no_kinship`.
    - Injected pairs: `splink_v3` = 302/499 (60.5%), `splink_v3_resolved` = 317/499 (63.5%), whereas `splink_v3_no_kinship` surges to **381/499 (76.4%)** [+15.9 pp].
    - Pooled pairs: `splink_v3` = 304/559 (54.4%), `splink_v3_resolved` = 319/559 (57.1%), whereas `splink_v3_no_kinship` surges to **385/559 (68.9%)** [+14.5 pp].
  - Variants operate at different selected thresholds whose weight scales are not comparable, and only 21/559 doppelganger pairs have rosters on both records, so the stress table alone does not isolate a kinship effect.
- **Reporting Artifacts Generated**:
  - `results/holdout/ablation_table.md`: Systematic ablation across 5 holdout seeds with paired per-seed $\Delta F_1$.
  - `results/stress_0/stress_table.md`: Complete natural vs injected vs pooled doppelganger breakdown with Wilson 95% CIs and generation notes.
  - `results/holdout/baseline_comparison.md`: Multi-seed benchmark comparing baselines, `splink_v1`, `splink_v1_resolved`, `splink_v3`, and `splink_v3_resolved`.

### Log Entry 009: 2026-11-07 — Phase 6b Model v3.1 Self-Roster Filtering Bug Fix & Pre-Registration H3
- **Model v3.1 Bug Fix (Self-Roster Member Collision)**:
  - On `demo`, diagnostic truth check identified 4 true candidate pairs where the v3 level `listed_as_other_member` erroneously fired, resulting in 5 resolution cannot-link constraint cuts separating records belonging to the SAME person.
  - *Root Cause*: Self-entry removal in Model v3 checked exact `name_canon` equality (`member_canon == self_canon`). When a participant was listed in their own household roster as the head with minor phonetic vowel differences (e.g. "Aminul" vs "Aminol", "Ali Hossain" vs "Ali Hussain", "Soloeman" vs "Soleman"), `name_canon` differed, leaving the entry unremoved. However, `name_skeleton` was identical (`amnlslmsk`, `alhsn`, `slmnlm`), causing the `listed_as_other_member` trigger to match the participant's own name in their other record.
  - *Fix (Model v3.1)*: In `src/barilink/link/normalise.py`, removed roster entries whose `name_skeleton` OR `name_canon` equals the record's own.
  - *Dev Evaluation Outcome & Status*:
    - Resolved cannot-link cuts separating the same person fell from 5 to 3.
    - Model v3.1 replaced v3 as a correctness fix (dev cost 830.0 -> 828.0; this difference is not treated as evidence), the H2 verdict is unaffected.
    - Cluster F1 improved to 0.6672.
    - **Model v3.1 is adopted as the champion reference model** replacing v3 for H3.
  - *Diagnosis of 3 Remaining Same-Person Cuts on DEV*:
    1. `comp_f07bebb1` (Cut edge `(25064e95b8, 28c5ce7d81)`, weight 15.65, Person `P_0000517`):
       - *Constraint Type*: Direct `listed_as_other_member` cannot-link cut.
       - *Field Values Responsible*: Synthetic corruption `name_swap` inverted participant and father names in record `28c5ce7d81` (`full_name_raw`: "Abdur Rahman Sheikh", `guardian_name_raw`: "Ayesha Khatun") vs `25064e95b8` (`full_name_raw`: "Mst. Ayesha Khatoon", `guardian_name_raw`: "Mohd. Abdur Rahman Sheikh"). In `25064e95b8`, the roster lists head "Abdur Rahman Sheik" (`abdrhmnsk`), which matches the swapped participant skeleton of `28c5ce7d81`. The constraint correctly severed this link because from the perspective of record `25064e95b8`, Abdur Rahman is a distinct household member (father/head).
    2. `comp_986eb189` (Cut edge `(70a9befd55, 9c79f783be)`, weight 8.63, Person `P_0011760`):
       - *Constraint Type*: Min-cut resolution collateral cut enforcing `listed_as_other_member`.
       - *Field Values Responsible*: Record `70a9befd55` ("Most. Parvin") had a spurious link to co-resident child `fef8003a86` ("Most. Afroza Bibi", guardian "Md. Shah Alam Aloi"). Because `fef8003a86`'s roster contained `'prbnbgm'` ("Parvin Begum"), a valid cannot-link constraint existed between `9c79f783be` ("Parvin Bigum", skeleton `prbnbgm`) and `fef8003a86`. Min-cut resolved this constraint along the 3-node path by severing the weakest edge, which happened to be between the two true Parvin records (`(70a9befd55, 9c79f783be)`, weight 8.63).
    3. `comp_da38ef11` (Cut edge `(92d15009ec, acd36d8726)`, weight 6.72, Person `P_0003358`):
       - *Constraint Type*: Min-cut resolution collateral cut enforcing `listed_as_other_member`.
       - *Field Values Responsible*: Same-household sibling `2ce6ef7afa` ("Salma Bii", skeleton `slmb`) had mutual `listed_as_other_member` cannot-link constraints with `92d15009ec` ("Most. Maleka Khaton", skeleton `mlktn`). Both records had spurious links to `acd36d8726` ("Maleka Khatun", no roster); min-cut severed the weakest edge on the path connecting the conflicting pair, severing edge `(92d15009ec, acd36d8726)` (weight 6.72).
- **Pre-Registration Hypothesis H3 & Decision Rule**:
  > H3 (formed after inspecting holdout_0..4 ablations, therefore confirmed only on fresh holdout_5..9): Kinship evidence should act as deterministic constraints, not as probabilistic Fellegi-Sunter evidence, because roster overlap violates conditional independence (it signals household, not person). Pipeline K = the reference model (v3, or v3.1 if adopted) with the kinship comparison removed, plus resolution with the listed_as_other_member cannot-link constraint (roster arrays still computed for the constraint). Decision rule: adopt K if its dev expected cost (resolved, own selected t_link/t_bridge) is at least 2% lower than the reference model's resolved dev cost. Confirmation: report K vs the reference on holdout_5..9 (seed offsets 1005-1009, never used before), using paired per-seed cost differences and the direction on 5/5 seeds.
- **Reference Model Resolved Dev Cost**:
  - Baseline reference: `splink_v3_1_resolved` dev expected operational cost = **828.0**.
  - Adoption threshold for Pipeline K: $0.98 \times 828.0 = \mathbf{811.44}$.
- **Secondary Outcomes (Reported, Not Decisive)**:
  > Secondary outcomes (reported, not decisive): (a) doppelganger FM at matched recall 0.40/0.50/0.60 on stress_0 for K vs the reference (v3.1). Expectation: K may be WORSE on cross-household doppelgangers, because the listed_as_other_member constraint only acts within households, while probabilistic kinship evidence reduced matched-recall doppelganger FM by about 9 pp on stress_0 (52.4% vs 61.6% at R = 0.50). (b) Same-household false merges on dev for K vs the reference. If K wins on cost but loses on (a), the project reports this as a trade-off and recommends the pipeline by the stated cost ratio, not by the better-looking metric.
- **Fresh Holdouts Generated**:
  - Built `holdout_5` through `holdout_9` (seed offsets 1005–1009) with `--role holdout` and exported features. No model has been evaluated on them.
- **Outcome of Hypothesis H3 on DEV (`demo`)**:
  - `splink_k` trained on `demo` with `guardian_mode="v2"`, no kinship comparison, and evaluated with resolution applying deterministic `listed_as_other_member` cannot-link constraints.
  - On the dev 2D resolution grid, `splink_k_resolved` selected optimal thresholds $t_{\text{link}} = 2.0$, $t_{\text{bridge}} = 4.0$.
  - Dev expected operational cost: **$C_{\text{K, resolved}} = 782.0$** (Cluster Precision = 0.9772, Cluster Recall = 0.5105, Cluster F1 = 0.6707, Doppelganger FM Rate = 0.00%, False-Merge Clusters = 14, Split Persons = 452).
  - Relative to reference model dev cost $C_{\text{v3.1, resolved}} = 828.0$, expected cost decreased by **$5.56\%$** (46.0 cost points), beating the $2\%$ pre-registered threshold ($782.0 \le 811.44$).
  - **Verdict on DEV**: **Hypothesis H3 is SUPPORTED**. Pipeline K is **ADOPTED**.
- **Fresh Holdout Confirmation (`holdout_5` .. `holdout_9`)**:
  - Evaluated on 5 fresh, uninspected holdout seeds (seed offsets 1005–1009) at frozen interior thresholds:
    - Reference (`splink_v3_1_resolved`, $t_{\text{link}}=6.5, t_{\text{bridge}}=8.0$): Holdout Cost = $888.2 \pm 51.2$, Precision = $0.9457 \pm 0.0127$, Recall = $0.5334 \pm 0.0202$, F1 = $0.6819 \pm 0.0174$, Doppelganger FM = $1.58\%$ [$0.73\%, 3.40\%$].
    - Pipeline K (`splink_k_resolved`, $t_{\text{link}}=2.0, t_{\text{bridge}}=4.0$): Holdout Cost = **$812.2 \pm 29.2$**, Precision = **$0.9656 \pm 0.0106$**, Recall = $0.5277 \pm 0.0172$, F1 = $0.6823 \pm 0.0137$, Doppelganger FM = **$1.32\%$** [$0.56\%, 3.04\%$].
    - *Holdout Doppelganger FM*: No detectable difference; CIs overlap.
  - **Precision vs Recall Trade-Off**: K's cost advantage comes from precision (0.966 vs 0.946) at equal recall (F1 difference +0.0004), and the ranking depends on the cost ratio.
  - **Paired Per-Seed Cost Difference**: $\Delta C = C_{\text{K}} - C_{\text{ref}} = \mathbf{-76.0 \pm 27.3}$ cost points (-8.56%).
    - Individual seeds: `holdout_5` (-33.0), `holdout_6` (-74.0), `holdout_7` (-108.0), `holdout_8` (-80.0), `holdout_9` (-85.0).
    - **Direction Consistency**: **5/5 seeds; one-sided sign test p = 0.031 (two-sided 0.0625)** strictly favoured Pipeline K.
  - **Cost Ratio Sensitivity Analysis (`holdout_5` .. `holdout_9` Mean Cost)**:
    - Recomputed from existing threshold tables at each pipeline's frozen operating point (no re-tuning):
      - **1:1 Cost**: Ref = $713.0 \pm 34.7$, K = $704.2 \pm 26.6$, $\Delta = -8.8 \pm 12.4$ (K won on 3/5 seeds).
      - **2:1 Cost**: Ref = $756.8 \pm 35.7$, K = $731.2 \pm 23.1$, $\Delta = -25.6 \pm 13.7$ (K won on 5/5 seeds).
      - **5:1 Cost** (Pre-registered): Ref = $888.2 \pm 51.2$, K = $812.2 \pm 29.2$, $\Delta = -76.0 \pm 27.3$ (K won on 5/5 seeds).
      - **10:1 Cost**: Ref = $1107.2 \pm 93.0$, K = $947.2 \pm 64.5$, $\Delta = -160.0 \pm 56.4$ (K won on 5/5 seeds).
  - **Confirmation Verdict**: **Hypothesis H3 is CONFIRMED**.
- **Secondary Outcomes**:
  - *(a) Doppelganger FM at Matched Recall on `stress_0`*: At $R=0.50$, Pipeline K Pooled FM is 62.1% vs 52.3% for the reference model (+9.8 pp). As predicted, removing probabilistic kinship increases false merges on synthetic cross-household doppelgangers because roster constraints only act within households.
  - *(b) Same-Household False Merges on DEV*: On `demo`, false-merge clusters dropped from 25 to **14** (-44.0%), and same-household false-merge pairs dropped from 24 to **16** (-33.3%).
  - *(c) Hypothesized Mechanism for (b) (not yet confirmed)*: Operating at lower match weights without the distorted kinship conditional independence penalties may allow min-cut resolution to enforce `listed_as_other_member` constraints cleanly without collateral damage.
- **Benchmark Conclusion**:
  - **Pipeline K (`splink_k_resolved`) is preferred under this synthetic benchmark and the assumed 5:1 cost ratio; not validated on real registry data.**
- **Limitations**:
  - *(a) Boundary Threshold*: Pipeline K's selected $t_{\text{link}} = 2.0$ lies on the lower grid boundary, and the optimum may be lower; not re-tuned, to preserve the confirmation protocol.
  - *(b) Holdout Consumption*: `holdout_5..9` are now consumed for linkage decisions, and any further linkage tuning requires new seeds (holdout_10+).

### Log Entry 010: 2026-11-07 — Phase 7 Household Inference, Direct/Indirect Reach & Pre-Registered Confirmation
- **Context & Scope**:
  - Person linkage is frozen (`splink_k_resolved`). Phase 7 infers household clusters and estimates direct and indirect program reach from person clusters without modifying person linkage.
  - Strict segregation enforced: `src/barilink/household` contains only model-visible logic and never imports or inspects ground truth (`test_household_truth_access_forbidden` verified).
- **Architecture & Evidence System (`src/barilink/household/`)**:
  - *Candidate Units*: Person clusters from `splink_k_resolved` (or Oracle persons in evaluation), blocked on `village_canon`.
  - *A-Priori Weights (labelled "assumed, not fitted")*:
    - $E_1$ `listed_member` ($w = 4.0$): A skeleton of cluster A's name appears in a roster attached to cluster B (or vice versa), after v3.1 self-entry filtering.
    - $E_2$ `husband_link` ($w = 4.0$): Cluster A has a `husband_name` whose skeleton matches any name skeleton in cluster B (or vice versa).
    - $E_3$ `father_link` ($w = 2.0$): Cluster A has a `father_name` whose skeleton matches cluster B's name skeleton, birth year of A is $\ge 15$ years after B, A has no `husband_name`, and patrilocal residence holds.
      - *Patrilocal Residence Assumption (labelled "assumed")*: Married women and adult daughters reside patrilocally; therefore $E_3$ fires only if the child cluster is NOT (`inferred_sex == 'F'` AND estimated age $\ge 18$ at reference date 2026). Adult women never receive $E_3$ links to their father.
      - *Model-Visible Sex Inference Rule*: Inferred from name prefixes (`mst/most/mosammat` $\to$ F, `md/mohammad/mohd` $\to$ M) and female title tokens (`khatun/begum/akter/bibi/rani/bala` $\to$ F). Conflicts resolved to `conflict`. Achieves **73.3%** coverage across person clusters.
    - $E_4$ `roster_overlap` ($w = 3.0$): Rosters attached to A and B share $\ge 2$ member skeletons.
    - $E_5$ `shared_phone` ($w = 1.0$): Clusters A and B share $\ge 1$ normalized 11-digit mobile phone.
  - *Inference with Constraints (`infer.py`)*:
    - Candidate edges scored by summing evidence weights. Retain edges with score $\ge t_{\text{hh}}$.
    - `max_household_size` $\le 12$: Oversized components partitioned via Stoer-Wagner min-cut on weakest edges (with sorted bisection for large components).
    - `cannot-household` constraint: Two wives of different men linked by $E_2$ cannot co-reside (co-wives sharing the same husband are permitted); conflicts severed by min-cut.
    - Deterministic IDs: `hh_` + sha256(sorted member cluster IDs).
  - *Golden Household Records (`golden.py`)*:
    - Mode village/union, enrolled members, enrolled modules, pooled phones, and `roster_names_unenrolled` (roster skeletons matching no enrolled member skeleton).
    - `direct_reach` = enrolled member count, `indirect_reach` = `len(roster_names_unenrolled)`, `est_household_size = direct + indirect`. Lineage tracked.
- **DEV Operating Point Selection (`demo`)**:
  - Pre-registered headline selection metric: **Record-level household pairwise F1** on `demo` (ties broken by higher $t_{\text{hh}}$).
  - Grid sweep $t_{\text{hh}} \in \{1.0..8.0\}$:
    - $t_{\text{hh}} = 1.0$: P = 0.1414, R = 0.3699, F1 = 0.2046, Size MAE = 7.47
    - $t_{\text{hh}} = 2.0$: P = 0.1418, R = 0.3697, F1 = 0.2050, Size MAE = 7.47
    - $t_{\text{hh}} = 3.0$: P = 0.1408, R = 0.3682, F1 = 0.2038, Size MAE = 7.48
    - $t_{\text{hh}} = 4.0$: P = 0.1358, R = 0.3570, F1 = 0.1968, Size MAE = 7.50
    - **$t_{\text{hh}} = 5.0$: P = 0.6460, R = 0.3415, F1 = 0.4468, Size MAE = 2.09 (SELECTED $t_{\text{hh}}^* = 5.0$)**
    - $t_{\text{hh}} = 6.0$: P = 0.6426, R = 0.3360, F1 = 0.4412, Size MAE = 2.08
    - $t_{\text{hh}} = 7.0$: P = 0.6805, R = 0.3247, F1 = 0.4397, Size MAE = 2.04
    - $t_{\text{hh}} = 8.0$: P = 0.6322, R = 0.2086, F1 = 0.3137, Size MAE = 1.94
  - *Mechanism*: At $t_{\text{hh}} \le 4.0$, single-channel $E_1$ (weight 4) links any person in the village sharing a common roster name, causing massive chaining. At $t_{\text{hh}} = 5.0$, multi-channel evidence is strictly required (e.g. $E_1 + E_5$ or $E_1 + E_2$), producing a sharp precision jump ($0.14 \to 0.65$) and dropping Size MAE from 7.50 to 2.09.
- **Pre-Registered Holdout Confirmation (`holdout_5` .. `holdout_9`)**:
  - **`holdout_5..9` were used for household inference for the first time with no revisions.**
  - Frozen operating point: $t_{\text{hh}}^* = 5.0$.
  - Evaluation results across 5 seeds (`mean +/- sd`):

| Pipeline / Configuration | Record Pairwise F1 | Record Precision | Record Recall | Unit B-cubed F1 | HH Reached Error % | Household Size MAE |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| Champion Pipeline (splink_k_resolved + Household) | **0.4592 +/- 0.0049** | 0.6848 +/- 0.0147 | 0.3455 +/- 0.0042 | 0.7528 +/- 0.0017 | +59.13% +/- 1.15% | 2.07 +/- 0.06 |
| Oracle Persons + Household Inference | **0.6062 +/- 0.0109** | 0.7147 +/- 0.0210 | 0.5264 +/- 0.0066 | 0.8102 +/- 0.0042 | +38.74% +/- 0.93% | 2.01 +/- 0.08 |
| Ablation: Drop E1 (listed_member, w=0) | 0.3149 +/- 0.0096 | 0.9983 +/- 0.0019 | 0.1869 +/- 0.0067 | 0.7132 +/- 0.0035 | +80.67% +/- 1.34% | 1.69 +/- 0.03 |
| Ablation: Drop E2 (husband_link, w=0) | 0.4760 +/- 0.0077 | 0.9332 +/- 0.0152 | 0.3195 +/- 0.0066 | 0.7556 +/- 0.0028 | +66.62% +/- 0.91% | 1.70 +/- 0.04 |
| Ablation: Drop E3 (father_link, w=0) | 0.4597 +/- 0.0069 | 0.7240 +/- 0.0197 | 0.3369 +/- 0.0046 | 0.7516 +/- 0.0016 | +61.22% +/- 1.21% | 1.99 +/- 0.06 |
| Ablation: Drop E4 (roster_overlap, w=0) | 0.3411 +/- 0.0083 | 0.6555 +/- 0.0118 | 0.2305 +/- 0.0064 | 0.7178 +/- 0.0034 | +69.57% +/- 1.17% | 2.03 +/- 0.06 |
| Ablation: Drop E5 (shared_phone, w=0) | 0.4559 +/- 0.0040 | 0.6847 +/- 0.0146 | 0.3418 +/- 0.0042 | 0.7515 +/- 0.0020 | +59.50% +/- 1.19% | 2.06 +/- 0.06 |
| Weight Robustness: All Weights x0.5 | 0.3069 +/- 0.0086 | 0.9982 +/- 0.0019 | 0.1814 +/- 0.0060 | 0.7105 +/- 0.0033 | +81.52% +/- 1.30% | 1.70 +/- 0.03 |
| Weight Robustness: All Weights x2.0 | 0.2055 +/- 0.0061 | 0.1435 +/- 0.0046 | 0.3619 +/- 0.0120 | 0.6363 +/- 0.0049 | +3.04% +/- 1.87% | 7.40 +/- 0.15 |

- **Error Decomposition (Person Linkage vs Household Inference)**:
  - Total Record Pairwise F1 drop from Oracle to Champion K: **$-0.1470 \pm 0.0104$**.
  - Decomposed by precision and recall:
    - Precision difference: **$-0.0299 \pm 0.0116$** (minimal drop; household edges formed by K are almost as clean as those formed by Oracle).
    - Recall difference: **$-0.1810 \pm 0.0098$** (the dominant driver; when person linkage splits a person across records, household evidence bridges fail to aggregate, fragmenting households).
  - Unit B-cubed F1 drop: $-0.0575 \pm 0.0034$.
  - Household Size MAE Delta: $+0.06 \pm 0.02$ (negligible difference in estimated household size error).
  - *Intrinsic vs Inherited Error*: Oracle persons reach only F1 0.61 (0.6062 +/- 0.0109) and +38.74% +/- 0.93% households-reached error, so most household error is intrinsic to household inference. Inherited person-linkage error accounts for about 0.15 F1 (-0.1470 +/- 0.0104, predominantly lost recall).
- **Ablation Findings & Consumption of Holdouts**:
  - Dropping E2 (`husband_link`) raises F1 (0.459 -> 0.476; precision 0.68 -> 0.93), indicating husband-name skeleton matching causes false household merges.
  - Dropping E3 (`father_link`) has no measurable effect (F1 0.4597 +/- 0.0069 vs 0.4592 +/- 0.0049).
  - *Protocol Constraint*: Do not re-tune; holdout_5..9 are consumed for household decisions.
- **Graph Partitioning & Max-Size Split Behavior**:
  - At $t_{\text{hh}} = 5.0$, the max-size split fired on only 2 components across all 5 seeds in `holdout_5..9`: `holdout_5` had 1 component of size 15 (cut weight 6.0), and `holdout_9` had 1 component of size 13 (cut weight 7.0), while `holdout_6`, `holdout_7`, and `holdout_8` had 0 oversize components.
  - Both components ($\le 25$ nodes) were partitioned via exact Stoer-Wagner min-cut.
  - *Heuristic Note*: The sorted-bisection fallback (which splits components $> 25$ nodes by arbitrary node index) is a heuristic, not a min-cut.
- **Administrative Stratification (Indirect Reach & Coverage)**:
  - Stratum (a) (Households with $\ge 1$ attached roster, **65.5%** of predicted households):
    - Indirect Reach Error: **$+13.71\% \pm 1.59\%$** (Oracle: $+16.51\% \pm 1.76\%$).
    - Household Size MAE: **$1.35 \pm 0.09$** (Oracle: $1.36 \pm 0.12$).
  - Stratum (b) (Households with no roster, **34.5%** of predicted households):
    - Indirect reach estimator is **structurally zero** because no roster was collected for any member.
    - Coverage: accurately documented that 34.5% of households lack roster data and cannot estimate indirect reach without imputation.
- **Weight Robustness Analysis**:
  - Scaling weights by $0.5\times$ causes F1 to collapse to $0.3069$ (under-merging due to insufficient multi-channel accumulation).
  - Scaling weights by $2.0\times$ causes F1 to collapse to $0.2055$ (single-channel edges exceed threshold, causing over-merging with Size MAE ballooning to 7.40).
  - Results are highly sensitive to the a-priori weights (F1 0.46 -> 0.31 at x0.5, 0.21 at x2). The operating point depends on the threshold sitting just above the E1 weight, so single-channel E1 links are excluded and multi-channel links are kept. This is a fragility, not a robustness result.
- **Future Work**:
  - Corroborate E1 with roster age_raw (+/- 5 years vs unit birth_year) and relation_raw consistency (e.g. spouse <-> inferred sex), plus stricter E2 (require E2 + same village + age plausibility).
  - Must be validated on fresh seeds holdout_10..14 under a new pre-registration.
- **Artifacts Generated**:
  - `results/holdout_confirm/household_table.md`: Comprehensive confirmation report.
  - `results/holdout_5/household/household_graph.json`: Complete interactive visualization graph for `holdout_5` (4,136 nodes, 13,237 candidate edges).
  - Per-seed results in `results/<run>/household/`: `household_clusters.parquet`, `household_golden.parquet`, `household_metrics.json`, `household_log.parquet`.

### Log Entry 011: 2026-11-07 — Phase 8 Reproducible Pipeline, Web Export, and CI Architecture
- **Decision 11.1: Single Frozen Publish Specification (`results/publish/publish_spec.json`)**:
  - Committed a single, immutable configuration contract tracking all parameters required for full deterministic reproduction of the champion pipeline on `holdout_5`:
    - Model artifact: `results/models/splink_k/model.json`.
    - Linkage parameters: `guardian_mode = "v2"`, `use_kinship = false`, `kinship_constraint = true`, `roster_self_filter = "v3.1"`, `max_birth_year_gap = 10`.
    - Person resolution thresholds: `t_link = 2.0`, `t_bridge = 4.0` (sourced from `results/splink_k_resolved/selected_thresholds.json`).
    - Household inference thresholds & weights: `t_hh = 5.0`, `max_size = 12`, `patrilocal_residence = true`, weights `E1: 4.0, E2: 4.0, E3: 2.0, E4: 3.0, E5: 1.0` (sourced from `results/household/selected_thresholds.json`).
  - At pipeline initialization, `pipeline.py` strictly validates these settings against `model.json` (asserting zero probabilistic kinship comparisons) and asserts existence of all referenced files. Any parameter mismatch or missing file halts execution immediately.
- **Decision 11.2: Cross-OS Semantic Determinism vs Binary File Hashing**:
  - Rather than comparing fragile bitwise file hashes across operating systems (which diverge due to Apache Arrow/Parquet metadata timestamps, compression dictionary differences, and CPU floating-point rounding), determinism is validated semantically against committed reference metrics (`results/publish/expected_headline.json`).
  - The verification command `python -m barilink.cli pipeline --verify` executes all 8 pipeline stages, recomputes all 14 person and household linkage metrics, and asserts absolute agreement within $\pm 0.005$ ($\pm 1\%$ on integer counts).
  - Cross-check passed: On `holdout_5`, Splink K resolved person linkage cost reproduced exactly at $784.0$ (matching `confirm_table.md`), and household pairwise F1 reproduced at $0.4578$ (matching `household_table.md`).
- **Decision 11.3: Web Data Export Contracts & Zero Ground-Truth Leakage**:
  - The export module (`src/barilink/export/web.py`) outputs 10 static assets into `web/public/data/` for client-side DuckDB-Wasm exploration:
    - Model-visible tables: `records.parquet` (4,841 rows, 0.19 MB), `pairs.parquet` (2,018 rows, 0.09 MB, candidate pairs with weight $\ge -5.0$), `clusters_by_threshold.parquet` (121,025 rows, 0.52 MB), `golden_records.parquet` (4,136 rows, 0.51 MB), `household_golden.parquet` (3,608 rows, 0.55 MB), `household_graph.json` (2.99 MB, 4,136 nodes, 13,237 edges), `model_summary.json` (0.01 MB).
    - Evaluation tables (truth-isolated under `web/public/data/eval/` generated strictly via `src/barilink/evaluate/export_eval.py`): `threshold_table.parquet` (25 rows, 0.01 MB), `record_labels.parquet` (4,841 rows, 0.11 MB), `headline.json` (0.002 MB).
    - Cryptographic manifest (`manifest.json`): schema version 1.0.0, Git commit SHA, dirty flag, file sizes, row counts, and SHA-256 hashes.
  - Zero truth leakage enforcement: AST security scanner forbids `truth` access in `barilink.export`. In `household_golden.parquet`, `household_id` was explicitly renamed to `household_cluster_id` to guarantee that no file outside `eval/` contains `person_id` or `household_id`.
  - Total payload size: **4.96 MB** (comfortably within the 25 MB static asset budget).
- **Decision 11.4: GitHub Actions Workflows & Proof of Isolation**:
  - Configured two GitHub Actions workflows using latest verified action versions (Node 24 runtime):
    - `.github/workflows/ci.yml`: Runs on pull requests and pushes to `main`. Uses Ubuntu 22.04, Python 3.11, pip cache, `actions/checkout@v5`, `actions/setup-python@v6`, `ruff check .`, `pytest -q -m "not publish"` (89 unit/integration tests in ~32s), and `python -m barilink.cli pipeline --profile ci` using `configs/ci.yaml` (500 households, seed offset 9000).
    - `.github/workflows/publish-data.yml`: Runs on manual dispatch and on pushes touching pipeline configurations, models, or core code. Uses `actions/checkout@v5`, `actions/setup-python@v6`, `actions/upload-artifact@v5`. Executes full publication pipeline on `holdout_5`, verifies determinism with `pipeline --verify`, runs `@pytest.mark.publish` tests, and uploads `web/public/data/` as a workflow artifact (`web-data`).
### Log Entry 012: 2026-11-07 — CI Test Suite Isolation, Test Classification, and Local Proof
- **Decision 12.1: Test Suite Classification & Marker Separation (`artifacts`)**:
  - Tests reading local, untracked experiment runs (`data/generated/`, `results/demo`, `results/holdout_*`, `results/stress_*`) were classified and segregated:
    - Pure function-correctness tests (`test_kinship_bug_check_function_correctness`, `test_stress_curves_function_correctness`, `test_confirm_table_function_correctness`, `test_oracle_mode_built_only_in_evaluate`, `test_verify_pipeline_detects_mismatch`) were rewritten to construct isolated synthetic DataFrames/mock metrics in `tmp_path`, passing paths explicitly.
    - Evaluator functions (`confirm.py`, `ablation.py`) were updated with custom output path / dev run parameters and guard checks raising `ValueError` on empty inputs, eliminating runtime warnings (e.g., `Mean of empty slice`).
    - Recorded experiment verification tests (checking historical hypothesis holds across seeds 5..9) were decorated with `@pytest.mark.artifacts`.
    - `pyproject.toml` registers both `publish` and `artifacts` markers. CI workflow executes `pytest -q -m "not publish and not artifacts"`, guaranteeing zero dependencies on untracked disk files.
  - Added AST lint test (`test_no_hardcoded_data_generated_demo_in_src`) enforcing zero `"data/generated/demo"` literals inside `src/`.
- **Decision 12.2: Test Mutation Guard (`tests/conftest.py`)**:
  - Added session start/finish hooks tracking `git ls-files -m` and SHA-256 hashes of all tracked files under `results/`, `configs/`, and `src/`.
  - Session finish fails if any tracked file was modified during the test execution, while gracefully ignoring pre-existing working tree state and skipping outside git clones.
  - Guard behavior verified via dedicated unit test in a throwaway git repository (`test_conftest_git_mutation_guard`).
- **Decision 12.3: CI Proof Script (`scripts/prove_ci.py`)**:
  - Reproduces the exact remote CI runner workflow locally in a clean, isolated temporary git clone.
  - Asserts complete absence of untracked experiment directories (`data/generated/` and `results/holdout_5/`).
  - Creates a fresh virtualenv, installs package with dev dependencies, executes `ruff check .`, `pytest -q -m "not publish and not artifacts"`, `python -m barilink.cli pipeline --profile ci`, and validates zero tracked file mutations via `git diff --exit-code`.
  - Supports `--worktree` flag for verifying candidate working tree changes prior to committing.

### Log Entry 013: 2026-11-07 — Phase 9 Static Web Application, Client-Side DuckDB-Wasm, and GitHub Pages CI
- **Decision 13.1: Zero-Backend In-Browser Architecture**:
  - Built standalone React 18 + TypeScript + Vite web application in `web/` running client-side with `@duckdb/duckdb-wasm` (loaded via same-origin Blob worker from jsDelivr CDN), Observable Plot (SVG precision/recall curves), and d3-force (small household graphs).
  - Configured Vite base path `/bari-link/` (configurable via `VITE_BASE_PATH`) for seamless deployment on GitHub Pages.
  - Hard constraint: Zero backend, zero analytics, zero cookies, zero external network queries except DuckDB-Wasm CDN bundles. Persistent top banner on every page: *"All data are synthetic. No real person is represented."*
  - Strict isolation: ESLint `no-restricted-imports` forbids `src/data/` and `src/workers/` from importing `src/eval/`. AST scan tests ensure zero `"eval"` in data/workers and zero `"data/eval"` outside `src/eval`.
  - Zero hard-coded figures: Overview and Findings render dynamically from DuckDB queries or `eval/headline.json`, enforced by AST `findings_no_hardcoded_numbers.test.ts`.
- **Decision 13.2: Counterfactual Python Export Extensions**:
  - Extended `src/barilink/export/web.py` to export `clusters_by_threshold_noconstraint.parquet` (same predictions and thresholds, but with `listed_as_other_member` disabled).
  - Extended `eval/threshold_table.parquet` with a `variant` column in `{"constraint", "no_constraint", "raw"}` (75 rows total).
  - Extended `eval/headline.json` with 6 machine-readable sections carrying `"source"` paths: `leakage_before_after`, `h1`, `h2`, `h3`, `cost_ratio_sensitivity`, `household`.
- **Decision 13.3: Interactive 4-View Suite & Performance Benchmarks**:
  - **Overview**: Dynamic module counts (4,841 naive registrations), true persons (3,689, +31.2% inflation), threshold slider ($t_{\text{link}} \in [2.0, 14.0]$, default 2.0 marked *"selected on dev data"*), 3-way pipeline mode switch, 6 live metric tiles, Observable Plot P/R curve, and clickable false-merge error inspector.
  - **Pair Explorer**: Prefix search by name or ID, candidate pair drawer sorted by weight, side-by-side administrative fields comparison with TruthChip, and exact Fellegi-Sunter log-odds evidence waterfall (`prior_log2_odds + sum(log2 bf) == match_weight` within $10^{-6}$).
  - **Households**: Search by person or household ID, golden household profile (direct/indirect reach, rosters, lineage), and 1-hop interactive force-directed graph with E1–E5 edge evidence labels.
  - **Findings**: Pure machine-readable display of ground-truth leakage discovery, H1–H3 outcomes, cost-ratio sensitivity (Pipeline K wins when false merges cost $\ge 2\times$ missed duplicates), and household engineering limitations (E2 penalty, weight fragility).
  - **Measured Performance**:
    - First Meaningful Paint (FMP): **115.2 ms** (target < 2,000 ms, 17x faster than budget).
    - Full DuckDB-Wasm Ready: **1,948 ms**.
    - Slider Update Latency (Resolved Mode): **68.8 ms** (target < 100 ms).
    - Production Bundle Size: `index.js` 676.6 KB (**202.4 KB gzip**), `unionfind.worker.js` 1.03 KB (**0.50 KB gzip**), `index.css` 7.89 KB (**2.14 KB gzip**).
- **Decision 13.4: Automated GitHub Pages Deployment (`.github/workflows/pages.yml`)**:
  - Dual-job pipeline: `publish-data` (Python 3.11, `pipeline --verify`, data-contract tests, upload `web-data` artifact) $\to$ `build-and-deploy` (Node 22, `npm ci`, ESLint, Vitest, build with `VITE_BASE_PATH=/bari-link/`, Playwright smoke test, GitHub Pages deployment).
  - Permissions: `pages: write`, `id-token: write`, `contents: read`. Concurrency group: `pages` (`cancel-in-progress: false`).
  - Required one-time manual repository configuration: **Settings -> Pages -> Build and deployment -> Source = GitHub Actions**.
- **Decision 13.5: Canonical Benchmark Reconciliation for Household Confirmation**:
  - Reconciled an internal discrepancy in `results/summary/household_table.json` where `champion` reported F1 $0.4601$ (Precision $0.6886$) while the base-weight ($1.0\times$) robustness row reported $0.4592$ (Precision $0.6848$).
  - **Root Cause & Provenance**:
    - During Phase 7, the 5-seed confirmation benchmark (`run_household_confirmation` at frozen $t_{\text{hh}} = 5.0$) evaluated `holdout_5..9`, yielding headline champion and base-weight metrics: Record F1 $= 0.4592 \pm 0.0049$, Precision $= 0.6848 \pm 0.0147$, Recall $= 0.3455 \pm 0.0042$, committed into `results/holdout_confirm/household_table.md`.
    - In Phase 8, running `pipeline --profile publish` executed end-to-end stages exclusively on `holdout_5` to prepare static demo assets and single-seed verification targets (`results/publish/expected_headline.json`). This execution overwrote `results/holdout_5/household/household_metrics.json` with single-run values (F1 $0.4694$, Precision $0.7027$, within $\pm 0.005$ cross-OS determinism tolerance), while `holdout_6..9` remained untouched.
    - Dynamically averaging the post-Phase 8 `holdout_5` file with the untouched Phase 7 `holdout_6..9` files produced F1 $0.4601$ and Precision $0.6886$ in `summary.py`.
  - **Canonical Value & Resolution**:
    - The Phase 7 confirmation benchmark table `results/holdout_confirm/household_table.md` (Record F1 $= \mathbf{0.4592}$, Precision $= \mathbf{0.6848}$) is the sole canonical reference for the 5-seed confirmation benchmark, matching all error decompositions ($-0.1470$ delta vs Oracle F1 $0.6062$), evidence ablations, and weight robustness rows.
    - Refactored `src/barilink/evaluate/summary.py` so both `champion` and `weight_robustness.base_1_0x` parse directly from this single canonical markdown source of truth.













