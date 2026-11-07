# Evaluation Report: splink_v3_resolved (holdout_4)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 6.5$,
  $t_{\text{bridge}} = 8.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9483** | 0.9924 |
| **Recall** | **0.5483** | 0.8932 |
| **F1 Score** | **0.6948** | 0.9402 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 35 |
| **False-Merged Records (Minority)** | 36 |
| **Split Persons** | 446 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 865.0 |
| **Deduplicated Reach** | 4,212 (Error: +11.96%) |
| **Pair Completeness (Recall Ceiling)** | 89.44% |
