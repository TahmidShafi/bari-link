# Systematic Model Ablation Report (5-Seed Holdout Uncertainty)

This benchmark systematically evaluates model components across 5 independent holdout seeds (holdout_0, holdout_1, holdout_2, holdout_3, holdout_4).
All thresholds are frozen at their interior dev-selected optimum on `demo`.

> [!NOTE]
> Asymmetric expected operational cost (5:1 penalty: $5 \cdot \text{FP} + 1 \cdot \text{FN}$ at the cluster level) is the primary selection objective for pre-registered decisions. Cluster F1, Precision, and Recall are reported for comparison.

---

## 1. Multi-Seed Ablation Summary Table

| Method | Operational Threshold | DEV Cost | Holdout Cost (5:1) (mean ± sd) | Paired $\Delta\text{Cost}$ vs v1 | Paired $\Delta\text{Cost}$ vs v3 | Cluster Precision (mean ± sd) | Cluster Recall (mean ± sd) | Cluster F1 (mean ± sd) | Paired $\Delta F_1$ vs v1 | Doppelganger FM Pooled Rate [Wilson 95% CI] | Reach Error % (mean ± sd) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `splink_v1` | $w=9.25$ ($p=0.9984$) | 960.0 | 3929.8 ± 595.8 | ref | +3001.2 ± 597.1 | 0.6068 ± 0.0421 | 0.7564 ± 0.0106 | 0.6728 ± 0.0266 | ref | 16.76% [13.30%, 20.90%] | -1.22% ± 0.87% |
| `splink_v2` | $w=9.25$ ($p=0.9984$) | 937.0 | 1071.4 ± 73.1 | -2858.4 ± 602.9 | +142.8 ± 81.3 | 0.9144 ± 0.0197 | 0.4923 ± 0.0180 | 0.6397 ± 0.0127 | -0.0331 ± 0.0317 | 1.35% [0.58%, 3.12%] | +13.93% ± 0.96% |
| `splink_v3` | $w=8.00$ ($p=0.9961$) | 875.0 | 928.6 ± 21.2 | -3001.2 ± 597.1 | ref | 0.9439 ± 0.0050 | 0.5107 ± 0.0159 | 0.6627 ± 0.0126 | -0.0101 ± 0.0329 | 1.89% [0.92%, 3.85%] | +13.76% ± 0.76% |
| `splink_v3_no_tf` | $w=7.75$ ($p=0.9954$) | 886.0 | 949.6 ± 20.0 | -2980.2 ± 595.8 | +21.0 ± 12.3 | 0.9381 ± 0.0071 | 0.5142 ± 0.0185 | 0.6641 ± 0.0141 | -0.0087 ± 0.0282 | 2.97% [1.67%, 5.24%] | +13.73% ± 0.77% |
| `splink_v3_no_kinship` | $w=1.25$ ($p=0.7040$) | 805.0 | 828.6 ± 35.4 | -3101.2 ± 621.4 | -100.0 ± 38.6 | 0.9424 ± 0.0084 | 0.6164 ± 0.0186 | 0.7452 ± 0.0125 | +0.0724 ± 0.0327 | 1.89% [0.92%, 3.85%] | +10.28% ± 0.68% |
| `splink_v3_resolved` | $t_{\text{link}}=6.5$, $t_{\text{bridge}}=8.0$ | 830.0 | 862.6 ± 54.7 | -3067.2 ± 621.4 | -66.0 ± 36.4 | 0.9500 ± 0.0071 | 0.5488 ± 0.0185 | 0.6956 ± 0.0157 | +0.0228 ± 0.0356 | 1.89% [0.92%, 3.85%] | +12.26% ± 0.70% |

---

## 2. Component Analysis & Findings

1. **Guardian Type Disambiguation (H1: `splink_v2`)**:
   - Separating different/unknown guardian types from matching guardian types reduced dev expected cost from 960.0 to 937.0 (-2.4%), lowering holdout cost by over 2,800 points.

2. **Household vs Individual Kinship Disambiguation (H2: `splink_v3`)**:
   - Filtering the participant's own name from roster arrays and penalising co-residents listed in the other member's roster (`listed_as_other_member`) lowered dev expected cost to 875.0 (-6.6% vs v2), dropping holdout cost to 928.6.

3. **Impact of Term Frequency (`splink_v3_no_tf`)**:
   - Removing TF weights slightly increases holdout cost (+21.0 vs v3) due to reduced discrimination on frequent Bangladeshi given names.

4. **Kinship Evidence as Fellegi-Sunter (`splink_v3_no_kinship`)**:
   - Disabling the kinship comparison optimizes at a lower match-weight threshold ($w=1.25$), reducing false negatives on holdout registries but increasing vulnerability under stress.

5. **Entity Resolution (`splink_v3_resolved`)**:
   - Deterministic `listed_as_other_member` cannot-link cuts and weak-bridge pruning with frozen parameters ($t_{\text{link}}=6.5, t_{\text{bridge}}=8.0$) lower dev cost to 830.0 and holdout cost to 862.6 (-66.0 vs v3, -3067.2 vs v1).

