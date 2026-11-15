# Evaluation Report: splink_v1_resolved (holdout_2)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 8.5$,
  $t_{\text{bridge}} = 10.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9120** | 0.9893 |
| **Recall** | **0.4614** | 0.8726 |
| **F1 Score** | **0.6128** | 0.9273 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.67%** |
| **False-Merge Clusters** | 46 |
| **False-Merged Records (Minority)** | 49 |
| **Split Persons** | 519 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,094.0 |
| **Deduplicated Reach** | 4,262 (Error: +14.23%) |
| **Pair Completeness (Recall Ceiling)** | 89.14% |
