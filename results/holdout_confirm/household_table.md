# Phase 7 Holdout Confirmation Table: Household Inference & Reach

Pre-registered evaluation across 5 independent holdout seeds (`holdout_5` through `holdout_9`).
Operating point frozen at DEV-selected edge threshold **$t_{\text{hh}}^* = 5.0$**.

### 1. Headline Record-Level & Reach Performance (Mean +/- SD)

| Pipeline / Configuration | Record Pairwise F1 | Record Precision | Record Recall | Unit B-cubed F1 | HH Reached Error % | Household Size MAE |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| Champion Pipeline (splink_k_resolved + Household) | 0.4592 +/- 0.0049 | 0.6848 +/- 0.0147 | 0.3455 +/- 0.0042 | 0.7528 +/- 0.0017 | +59.13% +/- 1.15% | 2.07 +/- 0.06 |
| Oracle Persons + Household Inference | 0.6062 +/- 0.0109 | 0.7147 +/- 0.0210 | 0.5264 +/- 0.0066 | 0.8102 +/- 0.0042 | +38.74% +/- 0.93% | 2.01 +/- 0.08 |
| Ablation: Drop E1 (listed_member, w=0) | 0.3149 +/- 0.0096 | 0.9983 +/- 0.0019 | 0.1869 +/- 0.0067 | 0.7132 +/- 0.0035 | +80.67% +/- 1.34% | 1.69 +/- 0.03 |
| Ablation: Drop E2 (husband_link, w=0) | 0.4760 +/- 0.0077 | 0.9332 +/- 0.0152 | 0.3195 +/- 0.0066 | 0.7556 +/- 0.0028 | +66.62% +/- 0.91% | 1.70 +/- 0.04 |
| Ablation: Drop E3 (father_link, w=0) | 0.4597 +/- 0.0069 | 0.7240 +/- 0.0197 | 0.3369 +/- 0.0046 | 0.7516 +/- 0.0016 | +61.22% +/- 1.21% | 1.99 +/- 0.06 |
| Ablation: Drop E4 (roster_overlap, w=0) | 0.3411 +/- 0.0083 | 0.6555 +/- 0.0118 | 0.2305 +/- 0.0064 | 0.7178 +/- 0.0034 | +69.57% +/- 1.17% | 2.03 +/- 0.06 |
| Ablation: Drop E5 (shared_phone, w=0) | 0.4559 +/- 0.0040 | 0.6847 +/- 0.0146 | 0.3418 +/- 0.0042 | 0.7515 +/- 0.0020 | +59.50% +/- 1.19% | 2.06 +/- 0.06 |
| Weight Robustness: All Weights x0.5 | 0.3069 +/- 0.0086 | 0.9982 +/- 0.0019 | 0.1814 +/- 0.0060 | 0.7105 +/- 0.0033 | +81.52% +/- 1.30% | 1.70 +/- 0.03 |
| Weight Robustness: All Weights x2.0 | 0.2055 +/- 0.0061 | 0.1435 +/- 0.0046 | 0.3619 +/- 0.0120 | 0.6363 +/- 0.0049 | +3.04% +/- 1.87% | 7.40 +/- 0.15 |

### 2. Error Decomposition: Person Linkage vs Household Inference

Decomposes total household error into error from household inference logic itself (Oracle) vs error inherited from Splink K person linkage:

- **Record Pairwise F1 Difference (K - Oracle)**: `-0.1470 +/- 0.0104`
- **Record Precision Difference (K - Oracle)**: `-0.0299 +/- 0.0116`
- **Record Recall Difference (K - Oracle)**: `-0.1810 +/- 0.0098`
- **Unit B-cubed F1 Difference (K - Oracle)**: `-0.0575 +/- 0.0034`
- **HH Reached Error % Delta**: `+20.39% +/- 1.19%`
- **Household Size MAE Delta**: `0.06 +/- 0.02`

Oracle persons reach only F1 0.61 (0.6062 +/- 0.0109) and +38.74% +/- 0.93% households-reached error, so most household error is intrinsic to household inference. Inherited person-linkage error accounts for about 0.15 F1 (-0.1470 +/- 0.0104, predominantly lost recall).

### 3. Ablation Findings & Consumption of Holdouts

- **Ablation on E2 (`husband_link`)**: Dropping E2 raises F1 (0.459 -> 0.476; precision 0.68 -> 0.93), indicating husband-name skeleton matching causes false household merges.
- **Ablation on E3 (`father_link`)**: Dropping E3 has no measurable effect (F1 0.4597 +/- 0.0069 vs 0.4592 +/- 0.0049).
- **Protocol**: Do not re-tune; holdout_5..9 are consumed for household decisions.

### 4. Graph Partitioning & Max-Size Split Behavior

At $t_{\text{hh}} = 5.0$, the max-size split fired on only 2 components across all 5 holdout seeds: `holdout_5` had 1 component of size 15 (cut weight 6.0), and `holdout_9` had 1 component of size 13 (cut weight 7.0), while `holdout_6`, `holdout_7`, and `holdout_8` had 0 oversize components. Both components (<= 25 nodes) were partitioned via exact Stoer-Wagner min-cut. Note: the sorted-bisection fallback (which splits components > 25 nodes by arbitrary node index) is a heuristic, not a min-cut.

### 5. Stratified Indirect Reach & Household Size (Amendment 3)

Reported across two administrative strata: (a) households with >= 1 attached roster; (b) households with no roster.
For Stratum (b), the indirect reach estimator is structurally zero because no roster was collected for any member of the household.

| Pipeline | Stratum (a) Share | Stratum (a) Ind. Reach Err % | Stratum (a) Size MAE | Stratum (b) Share | Stratum (b) Ind. Reach Note |
|:---|:---:|:---:|:---:|:---:|:---|
| Champion Pipeline (splink_k_resolved + Household) | +65.47% +/- 0.90% | +13.71% +/- 1.59% | 1.35 +/- 0.09 | +34.53% +/- 0.90% | *Structurally zero* |
| Oracle Persons + Household Inference | +68.71% +/- 0.75% | +16.51% +/- 1.76% | 1.36 +/- 0.12 | +31.29% +/- 0.75% | *Structurally zero* |
| Ablation: Drop E1 (listed_member, w=0) | +64.01% +/- 0.77% | +0.21% +/- 1.01% | 0.71 +/- 0.03 | +35.99% +/- 0.77% | *Structurally zero* |
| Ablation: Drop E2 (husband_link, w=0) | +64.93% +/- 0.86% | +0.25% +/- 0.71% | 0.77 +/- 0.04 | +35.07% +/- 0.86% | *Structurally zero* |
| Ablation: Drop E3 (father_link, w=0) | +65.39% +/- 0.89% | +10.95% +/- 1.72% | 1.23 +/- 0.09 | +34.61% +/- 0.89% | *Structurally zero* |
| Ablation: Drop E4 (roster_overlap, w=0) | +64.88% +/- 0.84% | +14.76% +/- 1.16% | 1.27 +/- 0.07 | +35.12% +/- 0.84% | *Structurally zero* |
| Ablation: Drop E5 (shared_phone, w=0) | +65.36% +/- 0.90% | +13.60% +/- 1.58% | 1.34 +/- 0.08 | +34.64% +/- 0.90% | *Structurally zero* |
| Weight Robustness: All Weights x0.5 | +63.88% +/- 0.78% | +0.36% +/- 0.92% | 0.71 +/- 0.03 | +36.12% +/- 0.78% | *Structurally zero* |
| Weight Robustness: All Weights x2.0 | +78.00% +/- 0.47% | +155.38% +/- 6.05% | 8.53 +/- 0.20 | +22.00% +/- 0.47% | *Structurally zero* |

### 6. Weight Robustness Analysis (Amendment 5)

Sensitivity of the Champion K pipeline to a-priori weights at frozen $t_{\text{hh}} = 5.0$:
- **Base Weights (1.0x)**: Record F1 = `0.4592 +/- 0.0049`
- **Halved Weights (0.5x)**: Record F1 = `0.3069 +/- 0.0086`
- **Doubled Weights (2.0x)**: Record F1 = `0.2055 +/- 0.0061`

Results are highly sensitive to the a-priori weights (F1 0.46 -> 0.31 at x0.5, 0.21 at x2). The operating point depends on the threshold sitting just above the E1 weight, so single-channel E1 links are excluded and multi-channel links are kept. This is a fragility, not a robustness result.

### 7. Future Work

Corroborate E1 with roster age_raw (+/- 5 years vs unit birth_year) and relation_raw consistency (e.g. spouse <-> inferred sex), plus stricter E2 (require E2 + same village + age plausibility). Must be validated on fresh seeds holdout_10..14 under a new pre-registration.
