# Evaluation Report: splink_v3_1_resolved (holdout_9)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 6.5$,
  $t_{\text{bridge}} = 8.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9572** | 0.9941 |
| **Recall** | **0.5114** | 0.8798 |
| **F1 Score** | **0.6667** | 0.9334 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 25 |
| **False-Merged Records (Minority)** | 27 |
| **Split Persons** | 481 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 896.0 |
| **Deduplicated Reach** | 4,135 (Error: +14.10%) |
| **Pair Completeness (Recall Ceiling)** | 88.56% |
