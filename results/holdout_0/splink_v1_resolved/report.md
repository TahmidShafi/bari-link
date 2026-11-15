# Evaluation Report: splink_v1_resolved (holdout_0)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 8.5$,
  $t_{\text{bridge}} = 10.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9448** | 0.9930 |
| **Recall** | **0.4309** | 0.8601 |
| **F1 Score** | **0.5919** | 0.9218 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.12%** |
| **False-Merge Clusters** | 32 |
| **False-Merged Records (Minority)** | 32 |
| **Split Persons** | 563 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,021.0 |
| **Deduplicated Reach** | 4,224 (Error: +16.24%) |
| **Pair Completeness (Recall Ceiling)** | 88.36% |
