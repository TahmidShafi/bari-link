# Holdout Baseline Comparison Report

This benchmark evaluates three deterministic, non-ML baseline record linkage methods on the **holdout** dataset (seed offset `1000`, 4,798 records across 4 administrative modules, 1,469 ground-truth matching pairs).

In strict accordance with the Dev vs. Holdout protocol, operational decision thresholds ($t_{\text{cost}} = 0.99$) were frozen from the development run (`demo`) and evaluated on `holdout` with zero re-tuning.

---

## 1. Summary Comparison Table

| Method | Pairwise Precision | Pairwise Recall | Pairwise F1 | B-cubed F1 | Doppelganger FM Rate | Reach Error % | Pair Completeness |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `exact` | **0.9769** | 0.0865 | 0.1588 | 0.8756 | 3.37% | +28.67% | 8.65% |
| `phone` | 0.8155 | 0.0933 | 0.1674 | 0.8748 | **0.00%** | +27.68% | 9.33% |
| `exact_or_phone` | 0.8750 | **0.1715** | **0.2869** | **0.8865** | 3.37% | **+24.77%** | **16.88%** |

---

## 2. Key Findings & Deduplication Gaps

1. **High Precision, Severe Recall Deficit (`exact`)**:
   - Exact string matching on normalized canonical tokens (`full_name`, `guardian_name`, `village`) achieves high cluster-level pairwise precision (97.69%), but detects only **8.65%** of all true duplicate pairs.
   - The method completely fails in the presence of phonetic drift, Damerau-Levenshtein typos, transliteration variants, and guardian switching (e.g. husband's name vs father's name).
   - Beneficiary reach is heavily inflated (+28.67% reach error; 4,676 predicted clusters vs 3,634 actual unique individuals).

2. **Phone Vulnerabilities & Noise (`phone`)**:
   - Phone matching yields **0.00%** doppelganger false-merge rate (cross-household hard negatives), confirming that distinct individuals rarely share mobile numbers.
   - However, shared household mobile numbers between family members induce 28 false-merge clusters (degrading pairwise precision to 81.55%).
   - Due to uncollected phone numbers in modules like `club_formation` and simulated SIM churn / missingness, recall remains capped at **9.33%**.

3. **Hybrid Baseline (`exact_or_phone`)**:
   - Combining exact name matching and phone matching nearly doubles pair completeness (16.88%) and pairwise recall (17.15%), achieving B-cubed F1 of 0.8865.
   - Nevertheless, **over 82% of true duplicates remain undetected**, resulting in an unacceptably high deduplicated reach error (+24.77%).

These empirical gaps clearly demonstrate the necessity of Phase 4: probabilistic record linkage (Splink Fellegi-Sunter model) with kinship-aware feature comparison and transliteration normalisation.

