# Evaluation Report: exact (demo)

- **Dataset Role**: `dev`
- **Evaluation Mode**: `select`
- **Selected $t_{\text{cost}}$**: `0.99`
- **Selected $t_{p99}$**: `N/A`

> **Note on $t_{p99}$**: No threshold achieved monotonic cluster precision >= 0.99.

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9648** | 0.9648 | 0.9990 |
| **Recall** | **0.0962** | 0.0962 | 0.7860 |
| **F1 Score** | **0.1750** | 0.1750 | **0.8798** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **8.22%** |
| **False-Merge Clusters** | 5 |
| **False-Merged Records (Minority)** | 5 |
| **Split Persons** | 809 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,312.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,806** | **4,671** | **3,667** | **+27.38%** |
| `club_formation` | 365 | 364 | 353 | +3.12% |
| `livelihood_support` | 2,179 | 2,167 | 2,109 | +2.75% |
| `microfinance_group` | 1,709 | 1,701 | 1,659 | +2.53% |
| `upg_enrolment` | 553 | 553 | 540 | +2.41% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 2,306,560 / 11,546,415
- **Reduction Ratio**: 80.0236%
- **Pair Completeness (Recall Ceiling)**: 9.62%
- **Pair Quality**: 0.01%
