# Systematic Model Ablation Report (5-Seed Holdout Uncertainty)

This benchmark systematically evaluates model components across 5 independent holdout seeds (holdout_0, holdout_1, holdout_2, holdout_3, holdout_4).
All thresholds are frozen at their interior dev-selected optimum on `demo`.

> [!NOTE]
> Asymmetric expected operational cost (5:1 penalty: $5 \cdot \text{FP} + 1 \cdot \text{FN}$ at the cluster level) is the primary selection objective for pre-registered decisions. Cluster F1, Precision, and Recall are reported for comparison.

---

## 1. Multi-Seed Ablation Summary Table

| Method | Operational Threshold | DEV Cost | Holdout Cost (5:1) (mean ± sd) | Paired $\Delta\text{Cost}$ vs v1 | Paired $\Delta\text{Cost}$ vs v3 | Cluster Precision (mean ± sd) | Cluster Recall (mean ± sd) | Cluster F1 (mean ± sd) | Paired $\Delta F_1$ vs v1 | Doppelganger FM Pooled Rate [Wilson 95% CI] | Reach Error % (mean ± sd) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `splink_v1` | $w=9.25$ ($p=0.9984$) | 960.0 | 1074.0 ± 66.2 | ref | +146.8 ± 73.2 | 0.9243 ± 0.0209 | 0.4408 ± 0.0194 | 0.5965 ± 0.0154 | ref | 1.35% [0.58%, 3.12%] | +15.65% ± 1.02% |
| `splink_v2` | $w=9.25$ ($p=0.9984$) | 937.0 | 1071.4 ± 73.1 | -2.6 ± 24.3 | +144.2 ± 85.8 | 0.9144 ± 0.0197 | 0.4923 ± 0.0180 | 0.6397 ± 0.0127 | +0.0432 ± 0.0045 | 1.35% [0.58%, 3.12%] | +13.93% ± 0.96% |
| `splink_v3` | $w=8.00$ ($p=0.9961$) | 876.0 | 927.2 ± 26.2 | -146.8 ± 73.2 | ref | 0.9441 ± 0.0036 | 0.5110 ± 0.0160 | 0.6630 ± 0.0132 | +0.0665 ± 0.0082 | 1.89% [0.92%, 3.85%] | +13.75% ± 0.75% |
| `splink_v3_no_tf` | $w=7.75$ ($p=0.9954$) | 888.0 | 950.0 ± 21.2 | -124.0 ± 74.7 | +22.8 ± 12.2 | 0.9380 ± 0.0049 | 0.5139 ± 0.0180 | 0.6638 ± 0.0142 | +0.0673 ± 0.0087 | 2.97% [1.67%, 5.24%] | +13.73% ± 0.73% |
| `splink_v3_no_kinship` | $w=1.25$ ($p=0.7040$) | 805.0 | 828.6 ± 35.4 | -245.4 ± 82.8 | -98.6 ± 43.8 | 0.9424 ± 0.0084 | 0.6164 ± 0.0186 | 0.7452 ± 0.0125 | +0.1486 ± 0.0102 | 1.89% [0.92%, 3.85%] | +10.28% ± 0.68% |
| `splink_v3_resolved` | $t_{\text{link}}=6.5$, $t_{\text{bridge}}=8.0$ | 828.0 | 864.6 ± 57.8 | -209.4 ± 89.8 | -62.6 ± 35.5 | 0.9494 ± 0.0071 | 0.5495 ± 0.0193 | 0.6959 ± 0.0166 | +0.0994 ± 0.0050 | 1.89% [0.92%, 3.85%] | +12.23% ± 0.69% |

---

## 2. Component Analysis & Findings

1. **Guardian Type Disambiguation (H1: `splink_v2`)**:
   - Separating different/unknown guardian types from matching guardian types reduced dev expected cost from 960.0 to 937.0 (-2.4%), changing holdout cost by -2.6 points.

2. **Household vs Individual Kinship Disambiguation (H2: `splink_v3`)**:
   - Filtering the participant's own name from roster arrays and penalising co-residents listed in the other member's roster (`listed_as_other_member`) lowered dev expected cost to 876.0 (-6.5% vs v2), with holdout cost at 927.2.

3. **Impact of Term Frequency (`splink_v3_no_tf`)**:
   - Removing TF weights changes holdout cost by +22.8 vs v3 due to reduced discrimination on frequent Bangladeshi given names.

4. **Kinship Evidence as Fellegi-Sunter (`splink_v3_no_kinship`)**:
   - Disabling the kinship comparison optimizes at a lower match-weight threshold ($w=1.25$), reducing false negatives on holdout registries but increasing vulnerability under stress.

5. **Entity Resolution (`splink_v3_resolved`)**:
   - Deterministic `listed_as_other_member` cannot-link cuts and weak-bridge pruning with frozen parameters ($t_{\text{link}}=6.5, t_{\text{bridge}}=8.0$) set dev cost to 828.0 and holdout cost to 864.6 (-62.6 vs v3, -209.4 vs v1).

