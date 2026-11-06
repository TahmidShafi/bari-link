# Holdout Baseline Comparison Report: Probabilistic Linkage vs. Baselines

This benchmark evaluates the performance of the **Splink 4 probabilistic linkage model** (`splink_v1`) against four non-ML baseline methods on the **holdout** dataset (seed offset `1000`, 4,798 records across 4 administrative modules, 1,469 ground-truth matching pairs).

In strict accordance with the Dev vs. Holdout protocol:
- The Splink model was trained solely on `demo` and exported to `results/models/splink_v1/model.json`.
- Operational decision thresholds ($t_{\text{cost}} = 0.99$) were frozen from the development run (`demo`) and applied to `holdout` with zero re-tuning or re-training.

---

## 1. Summary Comparison Table

| Method | Cluster Precision | Cluster Recall | Cluster F1 | B-cubed F1 | Doppelganger FM Rate | Reach Error % | Expected Cost |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `no_link` | **1.0000** | 0.0000 | 0.0000 | 0.8620 | **0.00%** | +32.03% | 1,469.0 |
| `exact` | 0.9769 | 0.0865 | 0.1588 | 0.8756 | 3.37% | +28.67% | 1,357.0 |
| `phone` | 0.8155 | 0.0933 | 0.1674 | 0.8748 | **0.00%** | +27.68% | 1,487.0 |
| `exact_or_phone` | 0.8750 | 0.1715 | 0.2869 | 0.8865 | 3.37% | +24.77% | 1,397.0 |
| `splink_v1` | 0.9017 | **0.5310** | **0.6684** | **0.9319** | 1.12% | **+12.77%** | **1,114.0** |

---

## 2. Key Findings & Performance Highlights

1. **Massive Recall Gain (>3x over Best Baseline)**:
   - `splink_v1` achieves **53.10%** cluster-level recall on unseen holdout data, compared to only **17.15%** for `exact_or_phone` and **8.65%** for `exact`.
   - Cluster F1 surges from **0.2869** to **0.6684** (+133.0% relative improvement).

2. **Substantial Beneficiary Reach Correction**:
   - The naive `no_link` assumption inflates beneficiary reach by +32.03% (4,798 predicted vs 3,634 actual individuals).
   - Deterministic matching only slightly reduces this error (+24.77% to +28.67%).
   - `splink_v1` cuts the reach inflation error nearly in half to **+12.77%** (4,098 predicted clusters).

3. **Robust Doppelganger Separation**:
   - Despite phonetic variation, `splink_v1` limits the false-merge rate on injected cross-household doppelgangers to **1.12%** (down from 3.37% in `exact` and `exact_or_phone`), proving that combining multi-field evidence (kinship rosters, age estimation, guardian, and union) successfully resists false merges.

4. **Operational Cost Minimization**:
   - In asymmetric cost evaluation ($C_{\text{FM}} = 5.0$, $C_{\text{FN}} = 1.0$), `splink_v1` reduces expected operational loss from **1,469.0** (`no_link`) and **1,397.0** (`exact_or_phone`) to **1,114.0** (a 20.3% net cost reduction).

5. **Clerical Review Window**:
   - At $t_{\text{cost}} = 0.99$, the model flags 3,157.6 candidate pairs per 10,000 records within the clerical review window ($[0.50, 0.99)$), providing field operators with high-yield pairs for targeted verification.
