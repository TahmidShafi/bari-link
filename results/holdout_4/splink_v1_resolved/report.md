# Evaluation Report: splink_v1_resolved (holdout_4)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 8.5$,
  $t_{\text{bridge}} = 10.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9132** | 0.9893 |
| **Recall** | **0.4461** | 0.8696 |
| **F1 Score** | **0.5994** | 0.9256 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 47 |
| **False-Merged Records (Minority)** | 50 |
| **Split Persons** | 536 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,102.0 |
| **Deduplicated Reach** | 4,310 (Error: +14.57%) |
| **Pair Completeness (Recall Ceiling)** | 89.44% |
