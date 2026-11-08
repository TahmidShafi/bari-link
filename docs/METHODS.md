# Bari-Link Methodology and System Architecture

This document specifies the technical design, data generation process, statistical assumptions, and algorithmic pipeline of the Bari-Link entity resolution system. For historical decisions, pre-registration milestones, and execution logs, see [PROJECT_CONTEXT.md](../PROJECT_CONTEXT.md).

---

## 1. Demographic Simulation & Data Generation

Bari-Link operates on an end-to-end synthetic population engine designed to replicate the administrative challenges of multi-program humanitarian registries in rural Bangladesh.

### 1.1 Household and Kinship Topologies
- **Compound Structure (*Bari*):** Populations are organized into multi-family residential compounds (*baris*) partitioned into distinct nuclear or extended household kitchens (*chula*) [Citation Required].
- **Patrilocal Residence:** Upon marriage, adult females are assumed [Assumed] to reside primarily in the husband's household.
- **Household Sizes:** Household size follows a truncated Poisson-lognormal distribution with an assumed [Assumed] mean of ~4.5 individuals.

### 1.2 Administrative Enrolment Modules
Records are distributed across four simulated administrative programs:
1. **General Food Distribution (GFD):** Primary household beneficiary registry.
2. **Maternal & Child Health (MCH):** Target mothers and infant children.
3. **Livelihood & Cash Transfer (LIV):** Variable wage-earner enrolment.
4. **Vulnerable Group Development (VGD):** Targeted ultra-poor transfers.

Each module collects varying subsets of administrative fields (name, guardian name, village, mobile phone number, and household roster lists). Beneficiary sex is omitted across all administrative forms.

---

## 2. Corruption & Variation Model

To evaluate record linkage without data leakage, synthetic corruption is applied post-generation using parameterized noise models:
- **Phonological Name Variation:** Romanized Bangla names undergo vowel shifts (e.g., `a` <-> `o`, `ee` <-> `i`), consonant gemination, and honorific prefix variations (e.g., `Md.`, `Mohd.`, `Most.`) [Citation Required]. Corruption rate: assumed [Assumed] 12% across records.
- **Guardian Naming Invariance & Role Ambiguity:** Registrations list either father or husband as primary guardian without explicit relationship tagging in raw text [Citation Required].
- **Phonetic & OCR Noise:** Double Metaphone transliteration mismatches, OCR character confusions (`c`/`e`, `rn`/`m`), and keyboard adjacencies.
- **Mobile Phone Churn:** Shared household numbers, digit transpositions, and digit churn. Assumed [Assumed] shared-device rate: 35%.
- **Age Heaping:** Digit preference on multiples of 5 and 10 (Whipple-like heaping index) assumed [Assumed] at 40% probability for self-reported ages [Citation Required].

---

## 3. Preprocessing & Normalisation

Incoming raw records pass through deterministic normalisation before candidate pair generation:
1. **Honorific & Title Stripping:** Standardized tokenization removes clerical prefixes (`Md`, `Mohd`, `Mst`, `Begum`, `Khatun`).
2. **Bangla Phonetic Encoding:** Double Metaphone transliteration produces dual-token phonetic representations.
3. **Village Canonicalization:** Canonical string mapping with Jaro-Winkler fuzzy tolerance.
4. **Phone Normalisation:** Extraction of the last 8 digits (`phone_last8`) to handle country-code (`+880` / `01`) formatting variances.

---

## 4. Probabilistic Person Linkage (Splink / Fellegi-Sunter)

Individual record linkage uses the Fellegi-Sunter (1969) model of record linkage, implemented via Splink 4.x.

### 4.1 Blocking Rules
Candidate pairs are formed using two disjunctive blocking rules:
1. `l.first_name_dm = r.first_name_dm AND l.village_canon = r.village_canon`
2. `l.phone_last8 = r.phone_last8 AND l.phone_last8 IS NOT NULL`

### 4.2 Comparison Features
- `full_name`: Exact match, Jaro-Winkler similarity >= 0.92, Jaro-Winkler similarity >= 0.85, else.
- `guardian_name`: Exact match, Jaro-Winkler similarity >= 0.88, else.
- `phone`: Exact match on `phone_last8`, else.
- `village`: Exact match, Jaro-Winkler similarity >= 0.88, else.
- `sex_raw`: Not estimated; every candidate pair across all holdout seeds evaluates to null ($\gamma = -1$) because administrative modules do not collect sex. The comparison is completely inert and recommended for removal.

### 4.3 Training & Parameter Estimation
Parameters ($m$ and $u$ probabilities) are estimated on development seed `dev_0` using Expectation-Maximisation (EM) conditioned on blocking rules. Parameters not identifiable under specific blocks fall back to Splink's heuristic defaults (documented in [untrained_params_audit.json](../results/summary/untrained_params_audit.json)). All reported $m$ and $u$ default parameters lie strictly in $[0, 1]$.

---

## 5. Graph Resolution & Kinship Constraints

Probabilistic candidate pairs with match weight $w \ge t_{\text{link}}$ form an undirected linkage graph.

### 5.1 Deterministic Cannot-Link Kinship Constraints (Pipeline K)
When two records in a candidate component are linked as *different co-members* of the same household roster (`listed_as_other_member = true`), they are subject to a hard **cannot-link** constraint. Even if their Fellegi-Sunter score exceeds $t_{\text{link}}$, they cannot be resolved into the same individual person cluster.

### 5.2 Weak-Bridge Splitting
Components containing cycle-breaking weak bridges (edges where weight $< t_{\text{bridge}}$ connecting denser sub-cliques) are severed to prevent runaway transitive chaining.

---

## 6. Household Inference

Households are inferred across resolved person clusters using a multi-channel evidence graph.

### 6.1 Household Evidence Channels
Weights are defined in `results/publish/publish_spec.json` and `results/household/selected_thresholds.json`:
1. **E1 (Roster Link):** Person $A$ listed on the household roster of Person $B$ ($w_1 = 4.0$).
2. **E2 (Husband Link):** Skeleton match between Person $A$'s name and Person $B$'s recorded husband ($w_2 = 4.0$).
3. **E3 (Father Link):** Shared father between individuals in the same village ($w_3 = 2.0$).
4. **E4 (Roster Overlap):** Substantial overlap in co-listed roster members ($w_4 = 3.0$).
5. **E5 (Shared Phone):** Co-occurring mobile phone within village ($w_5 = 1.0$).

### 6.2 Thresholding & Cuts
Clusters of persons are merged into household entities when total edge weight $\sum w_i \ge t_{\text{hh}} = 5.0$. Because the single-channel roster weight $w_1 = 4.0$ sits strictly below $t_{\text{hh}} = 5.0$, a single roster link cannot trigger a household merge on its own without multi-channel corroboration (e.g., $E1 + E5 = 5.0 \ge 5.0$ or $E1 + E3 = 6.0 \ge 5.0$). Merges that exceed a maximum household cap (12 individuals) or violate cannot-household constraints are deterministically pruned using deterministic edge sorting (tie-broken by composite key).

---

## 7. Evaluation Protocol & Operating Ratios

### 7.1 Dataset Partitions & Record ID Determinism
- **Development Seed:** `dev_0` (used for parameter exploration, threshold freezes, and hypothesis testing).
- **Confirmation Holdout Seeds:** `holdout_5`, `holdout_6`, `holdout_7`, `holdout_8`, `holdout_9` (strictly evaluated once post-freeze).
- **Publication Holdout Seed:** `publish_holdout_5` (dedicated namespace for web data export).
- **Adversarial Stress Seeds:** `stress_0` (elevated corruption rates, doppelgänger density, and phone churn).

**Record ID Independence:** Record ID generation does not depend on `run_name`. In `src/barilink/corrupt/registry.py`, record IDs are 10-character hex tokens generated by a NumPy PRNG initialized with `seed = config.seed + seed_offset`. `holdout_5` and `publish_holdout_5` share identical numeric seeds (`seed_offset = 1005`, `seed = 1047`). Both datasets have identical row counts (4,841 rows), 100% identical record IDs (4,841 shared IDs), and an identical multiset of record contents across all fields.

### 7.2 Asymmetric Operational Cost Metric
Evaluation prioritizes real-world program trade-offs over raw accuracy. The operational cost metric is defined as:
$$\text{Cost} = 5 \times \text{False Merges} + 1 \times \text{Missed Merges}$$
The 5:1 penalty ratio is an assumed [Assumed] operational parameter reflecting the ethical severity of a false merge: wrongfully collapsing two distinct poor households can cause permanent denial of cash or food assistance to an eligible family.

---

## 8. Reproducing the Experiments

The `pytest -q -m artifacts` verification suite evaluates the full set of multi-seed experiment outputs stored in `results/` and `data/generated/`. To re-execute the entire research experiment sweep from scratch:

### 8.1 Synthetic Data Generation
```bash
# Generate development, holdout, and stress populations
python -m barilink.cli generate --config configs/default.yaml --run-name dev_0
for seed in 0 1 2 3 4 5 6 7 8 9; do
    python -m barilink.cli generate --config configs/default.yaml --run-name holdout_$seed
done
python -m barilink.cli generate --config configs/default.yaml --run-name stress_0
```

### 8.2 Model Training
```bash
# Train Fellegi-Sunter models on dev_0
python -m barilink.cli link train-splink --config configs/default.yaml --run-name dev_0 --model-name splink_v1
python -m barilink.cli link train-splink --config configs/default.yaml --run-name dev_0 --model-name splink_v2
python -m barilink.cli link train-splink --config configs/default.yaml --run-name dev_0 --model-name splink_v3
python -m barilink.cli link train-splink --config configs/default.yaml --run-name dev_0 --model-name splink_k
```

### 8.3 Holdout Predictions and Kinship Resolution
```bash
# Run prediction and graph resolution across confirmation holdouts (holdout_5..9)
for seed in 5 6 7 8 9; do
    python -m barilink.cli link predict --run-name holdout_$seed --model-name splink_k
    python -m barilink.cli resolve graph --run-name holdout_$seed --model-name splink_k --t-link 2.0 --t-bridge 4.0
    python -m barilink.cli household infer --run-name holdout_$seed --t-hh 5.0
done
```

### 8.4 Evaluation Summaries
```bash
# Recompute summary JSON tables from experiment results
python -m barilink.cli evaluate summarize --results-dir results --data-dir data/generated --output-dir results/summary
python scripts/generate_preregistration_json.py
python -m barilink.evaluate.audit_untrained
```


