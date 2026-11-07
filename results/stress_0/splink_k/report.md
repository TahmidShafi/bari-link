# Evaluation Report: splink_k (stress_0)

- **Dataset Role**: `stress`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `95a50ae901ef905a...`
- **Selected $t_{\text{cost}}$**: `Weight = 1.25 (p = 0.704003)`
- **Selected $t_{p99}$**: `Weight = 9.25 (p = 0.998360)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.6095** | 0.6206 | 0.9273 |
| **Recall** | **0.6462** | 0.5776 | 0.9206 |
| **F1 Score** | **0.6273** | 0.5983 | **0.9239** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **68.87%** |
| **False-Merge Clusters** | 294 |
| **False-Merged Records (Minority)** | 303 |
| **Split Persons** | 355 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 3,466.0 |
| **Clerical Review Load (per 10k records)** | 232.4 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **5,207** | **4,162** | **4,079** | **+2.03%** |
| `club_formation` | 400 | 394 | 386 | +2.07% |
| `livelihood_support` | 2,163 | 2,106 | 2,108 | -0.09% |
| `microfinance_group` | 1,733 | 1,689 | 1,678 | +0.66% |
| `upg_enrolment` | 911 | 666 | 891 | -25.25% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 58,120 / 13,553,821
- **Reduction Ratio**: 99.5712%
- **Pair Completeness (Recall Ceiling)**: 90.21%
- **Pair Quality**: 2.22%
