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
