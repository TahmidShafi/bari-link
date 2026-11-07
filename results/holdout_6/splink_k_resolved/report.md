# Evaluation Report: splink_k_resolved (holdout_6)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 2.0$,
  $t_{\text{bridge}} = 4.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9739** | 0.9966 |
| **Recall** | **0.5217** | 0.8905 |
| **F1 Score** | **0.6794** | 0.9406 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.59%** |
| **False-Merge Clusters** | 15 |
| **False-Merged Records (Minority)** | 15 |
| **Split Persons** | 430 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 784.0 |
| **Deduplicated Reach** | 4,172 (Error: +12.70%) |
| **Pair Completeness (Recall Ceiling)** | 89.02% |
