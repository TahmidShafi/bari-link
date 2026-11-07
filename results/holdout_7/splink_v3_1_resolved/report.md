# Evaluation Report: splink_v3_1_resolved (holdout_7)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 6.5$,
  $t_{\text{bridge}} = 8.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9291** | 0.9913 |
| **Recall** | **0.5328** | 0.8872 |
| **F1 Score** | **0.6772** | 0.9363 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **4.12%** |
| **False-Merge Clusters** | 36 |
| **False-Merged Records (Minority)** | 38 |
| **Split Persons** | 477 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 940.0 |
| **Deduplicated Reach** | 4,180 (Error: +12.79%) |
| **Pair Completeness (Recall Ceiling)** | 90.66% |
