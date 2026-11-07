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
| **Precision** | **0.6276** | 0.6715 | 0.9446 |
| **Recall** | **0.5126** | 0.4531 | 0.8901 |
| **F1 Score** | **0.5643** | 0.5411 | **0.9165** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **49.37%** |
| **False-Merge Clusters** | 230 |
| **False-Merged Records (Minority)** | 234 |
| **Split Persons** | 486 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 2,872.0 |
| **Clerical Review Load (per 10k records)** | 2550.4 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **5,207** | **4,386** | **4,079** | **+7.53%** |
| `club_formation` | 400 | 400 | 386 | +3.63% |
| `livelihood_support` | 2,163 | 2,084 | 2,108 | -1.14% |
| `microfinance_group` | 1,733 | 1,712 | 1,678 | +2.03% |
| `upg_enrolment` | 911 | 721 | 891 | -19.08% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 58,120 / 13,553,821
- **Reduction Ratio**: 99.5712%
- **Pair Completeness (Recall Ceiling)**: 90.21%
- **Pair Quality**: 2.22%
