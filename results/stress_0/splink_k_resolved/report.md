# Evaluation Report: splink_k_resolved (stress_0)

- **Dataset Role**: `stress`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 2.0$,
  $t_{\text{bridge}} = 4.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.6171** | 0.9359 |
| **Recall** | **0.5545** | 0.9017 |
| **F1 Score** | **0.5842** | 0.9185 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **63.51%** |
| **False-Merge Clusters** | 271 |
| **False-Merged Records (Minority)** | 275 |
| **Split Persons** | 430 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 3,097.0 |
| **Deduplicated Reach** | 4,280 (Error: +4.93%) |
| **Pair Completeness (Recall Ceiling)** | 89.04% |
