# Evaluation Report: splink_k_resolved (holdout_5)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 2.0$,
  $t_{\text{bridge}} = 4.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9651** | 0.9948 |
| **Recall** | **0.5566** | 0.8946 |
| **F1 Score** | **0.7060** | 0.9421 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.27%** |
| **False-Merge Clusters** | 23 |
| **False-Merged Records (Minority)** | 23 |
| **Split Persons** | 427 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 784.0 |
| **Deduplicated Reach** | 4,136 (Error: +12.12%) |
| **Pair Completeness (Recall Ceiling)** | 89.04% |
