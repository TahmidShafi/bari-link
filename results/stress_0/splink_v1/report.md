# Evaluation Report: splink_v1 (stress_0)

- **Dataset Role**: `stress`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `4e303cd4a82445ed...`
- **Selected $t_{\text{cost}}$**: `Weight = 9.25 (p = 0.998360)`
- **Selected $t_{p99}$**: `Weight = 16.75 (p = 0.999991)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.6368** | 0.6835 | 0.9507 |
| **Recall** | **0.4593** | 0.4171 | 0.8776 |
| **F1 Score** | **0.5337** | 0.5181 | **0.9127** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **43.03%** |
| **False-Merge Clusters** | 202 |
| **False-Merged Records (Minority)** | 210 |
| **Split Persons** | 533 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 2,635.0 |
| **Clerical Review Load (per 10k records)** | 2602.1 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **5,142** | **4,388** | **4,003** | **+9.62%** |
| `club_formation` | 365 | 363 | 353 | +2.83% |
| `livelihood_support` | 2,179 | 2,095 | 2,109 | -0.66% |
| `microfinance_group` | 1,709 | 1,693 | 1,659 | +2.05% |
| `upg_enrolment` | 889 | 732 | 876 | -16.44% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 57,243 / 13,217,511
- **Reduction Ratio**: 99.5669%
- **Pair Completeness (Recall Ceiling)**: 89.54%
- **Pair Quality**: 2.23%
