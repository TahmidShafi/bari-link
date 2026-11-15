# Evaluation Report: splink_k (stress_0)

- **Dataset Role**: `stress`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `95a50ae901ef905a...`
- **Selected $t_{\text{cost}}$**: `Weight = 1.25 (p = 0.704003)`
- **Selected $t_{p99}$**: `Weight = 9.25 (p = 0.998360)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.6162** | 0.6341 | 0.9301 |
| **Recall** | **0.6292** | 0.5744 | 0.9168 |
| **F1 Score** | **0.6227** | 0.6028 | **0.9234** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **62.89%** |
| **False-Merge Clusters** | 276 |
| **False-Merged Records (Minority)** | 289 |
| **Split Persons** | 363 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 3,318.0 |
| **Clerical Review Load (per 10k records)** | 229.5 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **5,142** | **4,117** | **4,003** | **+2.85%** |
| `club_formation` | 365 | 358 | 353 | +1.42% |
| `livelihood_support` | 2,179 | 2,117 | 2,109 | +0.38% |
| `microfinance_group` | 1,709 | 1,667 | 1,659 | +0.48% |
| `upg_enrolment` | 889 | 659 | 876 | -24.77% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 57,243 / 13,217,511
- **Reduction Ratio**: 99.5669%
- **Pair Completeness (Recall Ceiling)**: 89.54%
- **Pair Quality**: 2.23%
