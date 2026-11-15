# Budgeted Clerical Review Summary: `splink_v1_resolved` on `holdout_0`

**Total Records ($N$)**: 4,798  
**Review Queue Size**: 1,001 uncertainty-ranked pairs  
**Operational Thresholds**: $t_{\text{link}} = 8.5$, $t_{\text{bridge}} = 10.0$  

---

## 1. Review Curve Table

| Budget ($K$ per 10k) | Pairs Reviewed | Merges (True Pairs) | Splits (False Pairs) | Cluster Precision | Cluster Recall | Cluster F1 | Expected Cost | Reach Error % |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **0** | 0 | 0 | 0 | 0.9448 | 0.4309 | 0.5919 | 1021.0 | +16.24% |
| **50** | 24 | 19 | 5 | 0.9463 | 0.4561 | 0.6155 | 989.0 | +15.74% |
| **100** | 48 | 38 | 10 | 0.9483 | 0.4615 | 0.6209 | 976.0 | +15.60% |
| **250** | 120 | 92 | 28 | 0.9619 | 0.4806 | 0.6409 | 903.0 | +15.30% |
| **500** | 240 | 181 | 59 | 0.9693 | 0.5160 | 0.6735 | 831.0 | +14.31% |

---

## 2. Review Dynamics & Monotonicity Analysis
Expected operational cost decreased monotonically across all simulated review budgets.

### Efficiency Insights:
- Prioritising cut edges (26 pairs) and boundary pairs ($|w - t_{\text{link}}| \le 6.0$) provides field staff with high-yield clerical review targets.
- At $K = 500$ pairs per 10k (240 pairs reviewed), cluster F1 reaches 0.6735 with expected cost reduced to 831.0.
