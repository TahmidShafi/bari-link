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
  - *Dev Evaluation Outcome*:
    - Resolved cannot-link cuts separating the same person fell from 5 to 3.
    - DEV expected operational cost decreased from 830.0 (`splink_v3_resolved`) to **828.0** (`splink_v3_1_resolved`, $t_{\text{link}}=6.5, t_{\text{bridge}}=8.0$).
    - Cluster F1 improved to 0.6672.
    - **Model v3.1 is adopted as the champion reference model** replacing v3 for H3.
- **Pre-Registration Hypothesis H3 & Decision Rule**:
  > H3 (formed after inspecting holdout_0..4 ablations, therefore confirmed only on fresh holdout_5..9): Kinship evidence should act as deterministic constraints, not as probabilistic Fellegi-Sunter evidence, because roster overlap violates conditional independence (it signals household, not person). Pipeline K = the reference model (v3, or v3.1 if adopted) with the kinship comparison removed, plus resolution with the listed_as_other_member cannot-link constraint (roster arrays still computed for the constraint). Decision rule: adopt K if its dev expected cost (resolved, own selected t_link/t_bridge) is at least 2% lower than the reference model's resolved dev cost. Confirmation: report K vs the reference on holdout_5..9 (seed offsets 1005-1009, never used before), using paired per-seed cost differences and the direction on 5/5 seeds.
- **Reference Model Resolved Dev Cost**:
  - Baseline reference: `splink_v3_1_resolved` dev expected operational cost = **828.0**.
  - Adoption threshold for Pipeline K: $0.98 \times 828.0 = \mathbf{811.44}$.
- **Fresh Holdouts Generated**:
  - Built `holdout_5` through `holdout_9` (seed offsets 1005–1009) with `--role holdout` and exported features. No model has been evaluated on them.







