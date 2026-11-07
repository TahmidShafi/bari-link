# Evaluation Report: splink_v1_resolved (holdout_3)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 8.5$,
  $t_{\text{bridge}} = 10.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.6335** | 0.9227 |
| **Recall** | **0.7773** | 0.9458 |
| **F1 Score** | **0.6981** | 0.9341 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **14.55%** |
| **False-Merge Clusters** | 264 |
| **False-Merged Records (Minority)** | 323 |
| **Split Persons** | 233 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 3,506.0 |
| **Deduplicated Reach** | 3,664 (Error: -1.40%) |
| **Pair Completeness (Recall Ceiling)** | 88.72% |
