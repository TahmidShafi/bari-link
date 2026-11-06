# Project Context: bari-link

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

