# Evaluation Report: splink_v1_resolved (holdout_2)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 8.5$,
  $t_{\text{bridge}} = 10.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.6047** | 0.9164 |
| **Recall** | **0.7599** | 0.9432 |
| **F1 Score** | **0.6735** | 0.9296 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **20.00%** |
| **False-Merge Clusters** | 265 |
| **False-Merged Records (Minority)** | 355 |
| **Split Persons** | 239 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 3,915.0 |
| **Deduplicated Reach** | 3,661 (Error: -1.88%) |
| **Pair Completeness (Recall Ceiling)** | 89.14% |
