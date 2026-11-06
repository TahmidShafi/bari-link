# Evaluation Report: splink_v1 (demo)

- **Dataset Role**: `dev`
- **Evaluation Mode**: `select`
- **Selected $t_{\text{cost}}$**: `0.99`
- **Selected $t_{p99}$**: `N/A`

> **Note on $t_{p99}$**: No threshold achieved monotonic cluster precision >= 0.99.

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.8884** | 0.9178 | 0.9854 |
| **Recall** | **0.5309** | 0.4937 | 0.8872 |
| **F1 Score** | **0.6646** | 0.6420 | **0.9337** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **2.74%** |
| **False-Merge Clusters** | 58 |
| **False-Merged Records (Minority)** | 64 |
| **Split Persons** | 467 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,143.0 |
| **Clerical Review Load (per 10k records)** | 3285.5 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,806** | **4,107** | **3,667** | **+12.00%** |
| `club_formation` | 365 | 363 | 353 | +2.83% |
| `livelihood_support` | 2,179 | 2,069 | 2,109 | -1.90% |
| `microfinance_group` | 1,709 | 1,694 | 1,659 | +2.11% |
| `upg_enrolment` | 553 | 544 | 540 | +0.74% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 49,984 / 11,546,415
- **Reduction Ratio**: 99.5671%
- **Pair Completeness (Recall Ceiling)**: 88.69%
- **Pair Quality**: 2.53%
