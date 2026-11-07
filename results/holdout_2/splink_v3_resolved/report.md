# Evaluation Report: splink_v3_resolved (holdout_2)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 6.5$,
  $t_{\text{bridge}} = 8.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9596** | 0.9937 |
| **Recall** | **0.5616** | 0.8963 |
| **F1 Score** | **0.7085** | 0.9425 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.67%** |
| **False-Merge Clusters** | 29 |
| **False-Merged Records (Minority)** | 29 |
| **Split Persons** | 428 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 800.0 |
| **Deduplicated Reach** | 4,168 (Error: +11.71%) |
| **Pair Completeness (Recall Ceiling)** | 89.14% |
