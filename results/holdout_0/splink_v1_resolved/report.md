# Evaluation Report: splink_v1_resolved (holdout_0)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 9.0$,
  $t_{\text{bridge}} = 9.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9560** | 0.9945 |
| **Recall** | **0.4581** | 0.8654 |
| **F1 Score** | **0.6194** | 0.9255 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.12%** |
| **False-Merge Clusters** | 24 |
| **False-Merged Records (Minority)** | 24 |
| **Split Persons** | 545 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 951.0 |
| **Deduplicated Reach** | 4,214 (Error: +15.96%) |
| **Pair Completeness (Recall Ceiling)** | 88.36% |
