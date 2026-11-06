# Evaluation Report: exact_or_phone (demo)

- **Dataset Role**: `dev`
- **Evaluation Mode**: `select`
- **Threshold Grid**: `weight`
- **Selected $t_{\text{cost}}$**: `Weight = 25.00 (p = 1.000000)`
- **Selected $t_{p99}$**: `none`

> **Warning on $t_{\text{cost}}$**: Selected threshold lies on the grid boundary! The true optimum may lie outside the current grid range.

> **Note on $t_{p99}$**: No threshold achieved monotonic cluster precision >= 0.99.

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.8860** | 0.8953 | 0.9938 |
| **Recall** | **0.1910** | 0.1861 | 0.8087 |
| **F1 Score** | **0.3143** | 0.3081 | **0.8917** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **8.22%** |
| **False-Merge Clusters** | 27 |
| **False-Merged Records (Minority)** | 29 |
| **Split Persons** | 732 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,327.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,806** | **4,531** | **3,667** | **+23.56%** |
| `club_formation` | 365 | 364 | 353 | +3.12% |
| `livelihood_support` | 2,179 | 2,150 | 2,109 | +1.94% |
| `microfinance_group` | 1,709 | 1,691 | 1,659 | +1.93% |
| `upg_enrolment` | 553 | 552 | 540 | +2.22% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 2,306,560 / 11,546,415
- **Reduction Ratio**: 80.0236%
- **Pair Completeness (Recall Ceiling)**: 18.61%
- **Pair Quality**: 0.01%
