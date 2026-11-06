# Evaluation Report: phone (demo)

- **Dataset Role**: `dev`
- **Evaluation Mode**: `select`
- **Selected $t_{\text{cost}}$**: `0.99`
- **Selected $t_{p99}$**: `N/A`

> **Note on $t_{p99}$**: No threshold achieved monotonic cluster precision >= 0.99.

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.8531** | 0.8531 | 0.9951 |
| **Recall** | **0.1060** | 0.1060 | 0.7885 |
| **F1 Score** | **0.1886** | 0.1886 | **0.8798** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 22 |
| **False-Merged Records (Minority)** | 23 |
| **Split Persons** | 796 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,403.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,806** | **4,645** | **3,667** | **+26.67%** |
| `club_formation` | 365 | 365 | 353 | +3.40% |
| `livelihood_support` | 2,179 | 2,161 | 2,109 | +2.47% |
| `microfinance_group` | 1,709 | 1,700 | 1,659 | +2.47% |
| `upg_enrolment` | 553 | 552 | 540 | +2.22% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 2,306,560 / 11,546,415
- **Reduction Ratio**: 80.0236%
- **Pair Completeness (Recall Ceiling)**: 10.60%
- **Pair Quality**: 0.01%
