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
| **Precision** | **0.6209** | 0.6737 | 0.9493 |
| **Recall** | **0.4580** | 0.4000 | 0.8790 |
| **F1 Score** | **0.5272** | 0.5020 | **0.9128** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **45.80%** |
| **False-Merge Clusters** | 210 |
| **False-Merged Records (Minority)** | 215 |
| **Split Persons** | 529 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 2,775.0 |
| **Clerical Review Load (per 10k records)** | 2679.1 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **5,207** | **4,459** | **4,079** | **+9.32%** |
| `club_formation` | 400 | 400 | 386 | +3.63% |
| `livelihood_support` | 2,163 | 2,086 | 2,108 | -1.04% |
| `microfinance_group` | 1,733 | 1,711 | 1,678 | +1.97% |
| `upg_enrolment` | 911 | 739 | 891 | -17.06% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 58,120 / 13,553,821
- **Reduction Ratio**: 99.5712%
- **Pair Completeness (Recall Ceiling)**: 90.21%
- **Pair Quality**: 2.22%
