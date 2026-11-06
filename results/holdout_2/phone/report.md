# Evaluation Report: phone (holdout_2)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `1352fa9e86978a46...`
- **Selected $t_{\text{cost}}$**: `Weight = 25.00 (p = 1.000000)`
- **Selected $t_{p99}$**: `none`

> **Warning on $t_{\text{cost}}$**: Selected threshold lies on the grid boundary! The true optimum may lie outside the current grid range.

> **Note on $t_{p99}$**: No threshold achieves cluster-level precision >= 0.99 (maximum observed: 0.8531)

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.8276** | 0.8276 | 0.9942 |
| **Recall** | **0.1002** | 0.1002 | 0.7900 |
| **F1 Score** | **0.1788** | 0.1788 | **0.8804** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 27 |
| **False-Merged Records (Minority)** | 27 |
| **Split Persons** | 793 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,443.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,866** | **4,711** | **3,731** | **+26.27%** |
| `club_formation` | 397 | 397 | 381 | +4.20% |
| `livelihood_support` | 2,200 | 2,171 | 2,133 | +1.78% |
| `microfinance_group` | 1,714 | 1,707 | 1,667 | +2.40% |
| `upg_enrolment` | 555 | 553 | 540 | +2.41% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 2,361,049 / 11,836,545
- **Reduction Ratio**: 80.0529%
- **Pair Completeness (Recall Ceiling)**: 10.02%
- **Pair Quality**: 0.01%
