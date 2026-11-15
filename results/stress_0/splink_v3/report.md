# Evaluation Report: splink_v3 (stress_0)

- **Dataset Role**: `stress`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `5b19102078e953a8...`
- **Selected $t_{\text{cost}}$**: `Weight = 8.00 (p = 0.996109)`
- **Selected $t_{p99}$**: `Weight = 20.00 (p = 0.999999)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.6278** | 0.6647 | 0.9429 |
| **Recall** | **0.5176** | 0.4747 | 0.8908 |
| **F1 Score** | **0.5674** | 0.5539 | **0.9161** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **50.70%** |
| **False-Merge Clusters** | 232 |
| **False-Merged Records (Minority)** | 241 |
| **Split Persons** | 478 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 2,872.0 |
| **Clerical Review Load (per 10k records)** | 2108.1 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **5,142** | **4,292** | **4,003** | **+7.22%** |
| `club_formation` | 365 | 363 | 353 | +2.83% |
| `livelihood_support` | 2,179 | 2,110 | 2,109 | +0.05% |
| `microfinance_group` | 1,709 | 1,687 | 1,659 | +1.69% |
| `upg_enrolment` | 889 | 696 | 876 | -20.55% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 57,243 / 13,217,511
- **Reduction Ratio**: 99.5669%
- **Pair Completeness (Recall Ceiling)**: 89.54%
- **Pair Quality**: 2.23%
