# Evaluation Report: splink_v1_resolved (demo)

- **Dataset Role**: `dev`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 8.5$,
  $t_{\text{bridge}} = 10.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9533** | 0.9942 |
| **Recall** | **0.4305** | 0.8646 |
| **F1 Score** | **0.5931** | 0.9249 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 27 |
| **False-Merged Records (Minority)** | 27 |
| **Split Persons** | 545 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 961.0 |
| **Deduplicated Reach** | 4,247 (Error: +15.82%) |
| **Pair Completeness (Recall Ceiling)** | 88.69% |
