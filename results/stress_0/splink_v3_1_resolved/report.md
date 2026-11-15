# Evaluation Report: splink_v3_1_resolved (stress_0)

- **Dataset Role**: `stress`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 6.5$,
  $t_{\text{bridge}} = 8.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.6376** | 0.9412 |
| **Recall** | **0.5485** | 0.8984 |
| **F1 Score** | **0.5897** | 0.9193 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **52.61%** |
| **False-Merge Clusters** | 243 |
| **False-Merged Records (Minority)** | 250 |
| **Split Persons** | 443 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 2,863.0 |
| **Deduplicated Reach** | 4,244 (Error: +6.02%) |
| **Pair Completeness (Recall Ceiling)** | 89.54% |
