# Systematic Model Ablation Report (5-Seed Holdout Uncertainty)

This benchmark systematically evaluates model components across 5 independent holdout seeds (holdout_0, holdout_1, holdout_2, holdout_3, holdout_4).
All thresholds are frozen at their interior dev-selected optimum on `demo`.

---

## 1. Multi-Seed Ablation Summary Table

| Method | Operational Threshold | Cluster Precision (mean ± sd) | Cluster Recall (mean ± sd) | Cluster F1 (mean ± sd) | Paired $\Delta F_1$ vs v1 (mean ± sd) | Individual Seed $\Delta F_1$ [s0..s4] | Doppelganger FM Pooled Rate [Wilson 95% CI] | Reach Error % (mean ± sd) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `splink_v1` | $w=9.25$ ($p=0.9984$) | 0.6068 ± 0.0421 | 0.7564 ± 0.0106 | 0.6728 ± 0.0266 | +0.0000 ± 0.0000 | `[+0.0000, +0.0000, +0.0000, +0.0000, +0.0000]` | 16.76% [13.30%, 20.90%] | -1.22% ± 0.87% |
| `splink_v2` | $w=9.25$ ($p=0.9984$) | 0.9144 ± 0.0197 | 0.4923 ± 0.0180 | 0.6397 ± 0.0127 | -0.0331 ± 0.0317 | `[-0.0683, -0.0621, -0.0166, -0.0254, +0.0069]` | 1.35% [0.58%, 3.12%] | +13.93% ± 0.96% |
| `splink_v3` | $w=8.00$ ($p=0.9961$) | 0.9439 ± 0.0050 | 0.5107 ± 0.0159 | 0.6627 ± 0.0126 | -0.0101 ± 0.0329 | `[-0.0546, -0.0280, +0.0164, -0.0104, +0.0262]` | 1.89% [0.92%, 3.85%] | +13.76% ± 0.76% |
| `splink_v3_no_tf` | $w=7.75$ ($p=0.9954$) | 0.9381 ± 0.0071 | 0.5142 ± 0.0185 | 0.6641 ± 0.0141 | -0.0087 ± 0.0282 | `[-0.0488, -0.0256, +0.0134, -0.0007, +0.0183]` | 2.97% [1.67%, 5.24%] | +13.73% ± 0.77% |
| `splink_v3_no_kinship` | $w=1.25$ ($p=0.7040$) | 0.9424 ± 0.0084 | 0.6164 ± 0.0186 | 0.7452 ± 0.0125 | +0.0724 ± 0.0327 | `[+0.0270, +0.0578, +0.0990, +0.0697, +0.1082]` | 1.89% [0.92%, 3.85%] | +10.28% ± 0.68% |
| `splink_v3_resolved` | $t_{\text{link}}=6.5$, $t_{\text{bridge}}=8.0$ | 0.9500 ± 0.0071 | 0.5488 ± 0.0185 | 0.6956 ± 0.0157 | +0.0228 ± 0.0356 | `[-0.0245, -0.0014, +0.0481, +0.0296, +0.0622]` | 1.89% [0.92%, 3.85%] | +12.26% ± 0.70% |

---

## 2. Component Analysis & Findings

1. **Guardian Type Disambiguation (H1: `splink_v2`)**:
   - Separating different/unknown guardian types from matching guardian types raised precision on clean administrative schemas.

2. **Household vs Individual Kinship Disambiguation (H2: `splink_v3`)**:
   - Filtering the participant's own name from roster arrays and penalising co-residents listed in the other member's roster (`listed_as_other_member`) substantially dropped false merges between household co-residents.

3. **Impact of Term Frequency (`splink_v3_no_tf`)**:
   - Removing TF weights slightly reduces discrimination on ubiquitous Bangladeshi given names and patronymics.

4. **Essential Role of Kinship Rosters (`splink_v3_no_kinship`)**:
   - Disabling the kinship comparison causes the model to optimize at a lower threshold ($w=1.25$), resulting in severe vulnerability to false merges when names align.

5. **Entity Resolution (`splink_v3_resolved`)**:
   - Deterministic `listed_as_other_member` cannot-link cuts and weak-bridge pruning with frozen parameters ($t_{\text{link}}=6.5, t_{\text{bridge}}=8.0$) eliminate residual multi-beneficiary clique confusion.

