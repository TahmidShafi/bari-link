# Evaluation Report: splink_v3_resolved (holdout_3)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 6.5$,
  $t_{\text{bridge}} = 8.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9509** | 0.9923 |
| **Recall** | **0.5736** | 0.8975 |
| **F1 Score** | **0.7156** | 0.9425 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.82%** |
| **False-Merge Clusters** | 35 |
| **False-Merged Records (Minority)** | 35 |
| **Split Persons** | 427 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 815.0 |
| **Deduplicated Reach** | 4,147 (Error: +11.60%) |
| **Pair Completeness (Recall Ceiling)** | 88.72% |
