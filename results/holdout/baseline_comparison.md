# Holdout Baseline Comparison Report: Probabilistic Linkage vs. Baselines (5-Seed Uncertainty)

This benchmark evaluates the performance of the **Splink 4 probabilistic linkage model** (`splink_v1`) against four non-ML baseline methods across 5 independent holdout seeds (seed offsets `1000`, `1001`, `1002`, `1003`, `1004`, corresponding to runs `holdout_0` through `holdout_4`). Each holdout contains ~4,800 records across 4 administrative modules and ~1,450 ground-truth matching pairs.

In strict accordance with the Dev vs. Holdout protocol:
- The Splink model was trained solely on `demo` and frozen at `results/models/splink_v1/model.json`.
- Operational decision thresholds ($t_{\text{cost}} = 9.00$ weight / $0.998051$ probability, $t_{\text{p99}} = 15.50$ weight / $0.999978$ probability) were selected on `demo` via match-weight grid sweep ($-5.0$ to $+25.0$ in steps of $0.25$) and evaluated on all holdouts with zero re-tuning or re-training.
- Baseline methods output deterministic matches ($p = 1.0$), corresponding to match-weight $+\infty$ ($t_{\text{cost}} = 25.00$ boundary).

---

## 1. Multi-Seed Summary Comparison Table

| Method | Cluster Precision (mean ± sd) | Cluster Recall (mean ± sd) | Cluster F1 (mean ± sd) | Pair Completeness | Doppelganger FM Pooled Rate [Wilson 95% CI] | Reach Error % (mean ± sd) | Review Pairs per 10k | $t_{\text{cost}}$ (Weight / Prob) | $t_{\text{p99}}$ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `no_link` | 1.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.00% | 0.00% [0.00%, 1.03%] | +31.00% ± 0.70% | 0.0 | 25.00 / 1.000000 | none |
| `exact` | 0.9769 ± 0.0089 | 0.0979 ± 0.0155 | 0.1776 ± 0.0255 | 9.79% | 4.86% [3.10%, 7.56%] | +27.34% ± 1.03% | 0.0 | 25.00 / 1.000000 | none |
| `phone` | 0.7751 ± 0.0731 | 0.0867 ± 0.0106 | 0.1559 ± 0.0183 | 8.67% | 0.27% [0.05%, 1.51%] | +27.03% ± 0.61% | 0.0 | 25.00 / 1.000000 | none |
| `exact_or_phone` | 0.8557 ± 0.0419 | 0.1795 ± 0.0212 | 0.2964 ± 0.0302 | 17.63% | 5.14% [3.31%, 7.88%] | +23.70% ± 0.99% | 0.0 | 25.00 / 1.000000 | none |
| `splink_v1` | **0.9404 ± 0.0081** | **0.4741 ± 0.0122** | **0.6303 ± 0.0105** | **89.04%** | **1.89% [0.92%, 3.85%]** | **+14.85% ± 0.69%** | 2031.1 | 9.00 / 0.998051 | 15.50 / 0.999978 |

> Note: B-cubed is reported only in `metrics.json` because singleton-heavy data inflate it (`no_link` scores about 0.86).

---

## 2. Key Findings & Performance Highlights

1. **Substantial Recall Gain Across Seeds**:
   - `splink_v1` delivers **0.4741 ± 0.0122** cluster recall across the 5 holdouts, representing a **2.6x** recall multiplier over `exact_or_phone` (0.1795) and **4.8x** over `exact` (0.0979).
   - Cluster F1 reaches **0.6303 ± 0.0105** (more than double the best baseline `exact_or_phone` at 0.2964).

2. **Beneficiary Reach Correction**:
   - Unlinked registries (`no_link`) suffer from severe beneficiary overcounting (+31.00% ± 0.70% reach error).
   - `splink_v1` cuts reach overcounting in half to **+14.85% ± 0.69%**, directly improving resource allocation accuracy in humanitarian and social safety-net programmes.

3. **High Blocking Pair Completeness**:
   - The multi-rule blocking scheme captures **89.04%** of all true pairs while pruning >99.6% of candidate comparisons, leaving a large recall ceiling for probabilistic scoring.

4. **Doppelganger Separation**:
   - Out of 370 injected cross-household doppelganger pairs across the 5 seeds, `splink_v1` falsely merges only 7 pairs (pooled rate 1.89%, Wilson 95% CI: [0.92%, 3.85%]), compared to 18 pairs (4.86%, CI: [3.10%, 7.56%]) for `exact` and 19 pairs (5.14%, CI: [3.31%, 7.88%]) for `exact_or_phone`.
   - Incorporating guardian skeletons, age estimations, and household rosters provides critical discriminative power that prevents false merges between namesakes living in different households.

5. **Operational Clerical Review**:
   - At the weight-grid selected threshold $t_{\text{cost}} = 9.00$ ($p \approx 0.998051$), `splink_v1` identifies 2,031.1 candidate pairs per 10,000 records within the clerical review zone ($[t_{\text{cost}}, t_{\text{p99}})$), pinpointing borderline cases for human field verification.
