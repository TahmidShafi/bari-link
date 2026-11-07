# Evaluation Report: splink_v1_resolved (holdout_1)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 9.0$,
  $t_{\text{bridge}} = 9.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9389** | 0.9932 |
| **Recall** | **0.4685** | 0.8695 |
| **F1 Score** | **0.6251** | 0.9272 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **4.65%** |
| **False-Merge Clusters** | 27 |
| **False-Merged Records (Minority)** | 30 |
| **Split Persons** | 524 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,009.0 |
| **Deduplicated Reach** | 4,243 (Error: +15.39%) |
| **Pair Completeness (Recall Ceiling)** | 89.56% |
