# Evaluation Report: splink_v1_resolved (holdout_1)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 8.5$,
  $t_{\text{bridge}} = 10.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.6416** | 0.9228 |
| **Recall** | **0.7586** | 0.9412 |
| **F1 Score** | **0.6952** | 0.9319 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **19.77%** |
| **False-Merge Clusters** | 252 |
| **False-Merged Records (Minority)** | 334 |
| **Split Persons** | 246 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 3,481.0 |
| **Deduplicated Reach** | 3,626 (Error: -1.39%) |
| **Pair Completeness (Recall Ceiling)** | 89.56% |
