# Evaluation Report: splink_v1_resolved (holdout_4)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 8.5$,
  $t_{\text{bridge}} = 10.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.5945** | 0.9144 |
| **Recall** | **0.7561** | 0.9417 |
| **F1 Score** | **0.6656** | 0.9278 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **17.50%** |
| **False-Merge Clusters** | 270 |
| **False-Merged Records (Minority)** | 364 |
| **Split Persons** | 251 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 4,061.0 |
| **Deduplicated Reach** | 3,688 (Error: -1.97%) |
| **Pair Completeness (Recall Ceiling)** | 89.44% |
