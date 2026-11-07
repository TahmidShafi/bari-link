# Evaluation Report: splink_v3_resolved (holdout_3)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 6.5$,
  $t_{\text{bridge}} = 8.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9507** | 0.9923 |
| **Recall** | **0.5708** | 0.8969 |
| **F1 Score** | **0.7133** | 0.9422 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.82%** |
| **False-Merge Clusters** | 35 |
| **False-Merged Records (Minority)** | 35 |
| **Split Persons** | 429 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 819.0 |
| **Deduplicated Reach** | 4,150 (Error: +11.68%) |
| **Pair Completeness (Recall Ceiling)** | 88.72% |
