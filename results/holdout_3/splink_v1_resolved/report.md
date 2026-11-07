# Evaluation Report: splink_v1_resolved (holdout_3)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 9.0$,
  $t_{\text{bridge}} = 9.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9519** | 0.9944 |
| **Recall** | **0.4877** | 0.8769 |
| **F1 Score** | **0.6449** | 0.9320 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.82%** |
| **False-Merge Clusters** | 24 |
| **False-Merged Records (Minority)** | 25 |
| **Split Persons** | 509 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 902.0 |
| **Deduplicated Reach** | 4,255 (Error: +14.50%) |
| **Pair Completeness (Recall Ceiling)** | 88.72% |
