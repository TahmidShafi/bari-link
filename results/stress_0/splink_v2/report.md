# Evaluation Report: splink_v2 (stress_0)

- **Dataset Role**: `stress`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `bf3eb6e3610b6dc7...`
- **Selected $t_{\text{cost}}$**: `Weight = 9.25 (p = 0.998360)`
- **Selected $t_{p99}$**: `Weight = 17.25 (p = 0.999994)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.6360** | 0.6788 | 0.9469 |
| **Recall** | **0.5007** | 0.4600 | 0.8862 |
| **F1 Score** | **0.5603** | 0.5483 | **0.9155** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **45.30%** |
| **False-Merge Clusters** | 215 |
| **False-Merged Records (Minority)** | 224 |
| **Split Persons** | 502 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 2,751.0 |
| **Clerical Review Load (per 10k records)** | 2526.3 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **5,142** | **4,331** | **4,003** | **+8.19%** |
| `club_formation` | 365 | 363 | 353 | +2.83% |
| `livelihood_support` | 2,179 | 2,092 | 2,109 | -0.81% |
| `microfinance_group` | 1,709 | 1,692 | 1,659 | +1.99% |
| `upg_enrolment` | 889 | 717 | 876 | -18.15% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 57,243 / 13,217,511
- **Reduction Ratio**: 99.5669%
- **Pair Completeness (Recall Ceiling)**: 89.54%
- **Pair Quality**: 2.23%
