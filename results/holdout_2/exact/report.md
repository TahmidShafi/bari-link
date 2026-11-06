# Evaluation Report: exact (holdout_2)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `fd0c101a41f62d94...`
- **Selected $t_{\text{cost}}$**: `Weight = 25.00 (p = 1.000000)`
- **Selected $t_{p99}$**: `none`

> **Warning on $t_{\text{cost}}$**: Selected threshold lies on the grid boundary! The true optimum may lie outside the current grid range.

> **Note on $t_{p99}$**: No threshold achieves cluster-level precision >= 0.99 (maximum observed: 0.9648)

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9661** | 0.9661 | 0.9988 |
| **Recall** | **0.1190** | 0.1190 | 0.7948 |
| **F1 Score** | **0.2119** | 0.2119 | **0.8852** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **13.33%** |
| **False-Merge Clusters** | 6 |
| **False-Merged Records (Minority)** | 6 |
| **Split Persons** | 775 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,296.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,866** | **4,705** | **3,731** | **+26.11%** |
| `club_formation` | 397 | 395 | 381 | +3.67% |
| `livelihood_support` | 2,200 | 2,190 | 2,133 | +2.67% |
| `microfinance_group` | 1,714 | 1,703 | 1,667 | +2.16% |
| `upg_enrolment` | 555 | 555 | 540 | +2.78% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 2,361,049 / 11,836,545
- **Reduction Ratio**: 80.0529%
- **Pair Completeness (Recall Ceiling)**: 11.90%
- **Pair Quality**: 0.01%
