# Evaluation Report: exact_or_phone (holdout)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `b9ecf88160e89fec...`
- **Selected $t_{\text{cost}}$**: `0.99`
- **Selected $t_{p99}$**: `N/A`

> **Note on $t_{p99}$**: No threshold achieves cluster-level precision >= 0.99 (maximum observed: 0.8860)

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.8750** | 0.8794 | 0.9932 |
| **Recall** | **0.1715** | 0.1688 | 0.8005 |
| **F1 Score** | **0.2869** | 0.2833 | **0.8865** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **3.37%** |
| **False-Merge Clusters** | 31 |
| **False-Merged Records (Minority)** | 31 |
| **Split Persons** | 737 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,397.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,798** | **4,534** | **3,634** | **+24.77%** |
| `club_formation` | 383 | 380 | 373 | +1.88% |
| `livelihood_support` | 2,160 | 2,138 | 2,105 | +1.57% |
| `microfinance_group` | 1,699 | 1,682 | 1,658 | +1.45% |
| `upg_enrolment` | 556 | 554 | 540 | +2.59% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 2,312,311 / 11,508,003
- **Reduction Ratio**: 79.9069%
- **Pair Completeness (Recall Ceiling)**: 16.88%
- **Pair Quality**: 0.01%
