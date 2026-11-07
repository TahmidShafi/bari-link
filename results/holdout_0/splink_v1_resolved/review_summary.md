# Budgeted Clerical Review Summary: `splink_v1_resolved` on `holdout_0`

**Total Records ($N$)**: 4,798  
**Review Queue Size**: 890 uncertainty-ranked pairs  
**Operational Thresholds**: $t_{\text{link}} = 9.0$, $t_{\text{bridge}} = 9.0$  

---

## 1. Review Curve Table

| Budget ($K$ per 10k) | Pairs Reviewed | Merges (True Pairs) | Splits (False Pairs) | Cluster Precision | Cluster Recall | Cluster F1 | Expected Cost | Reach Error % |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **0** | 0 | 0 | 0 | 0.9560 | 0.4581 | 0.6194 | 951.0 | +15.96% |
| **50** | 24 | 17 | 7 | 0.9578 | 0.4636 | 0.6248 | 938.0 | +15.80% |
| **100** | 48 | 38 | 10 | 0.9624 | 0.4704 | 0.6319 | 913.0 | +15.69% |
| **250** | 120 | 99 | 21 | 0.9732 | 0.4935 | 0.6549 | 844.0 | +15.16% |
| **500** | 240 | 201 | 39 | 0.9808 | 0.5214 | 0.6809 | 778.0 | +14.34% |

---

## 2. Review Dynamics & Monotonicity Analysis
Expected operational cost decreased monotonically across all simulated review budgets.

### Efficiency Insights:
- Prioritising cut edges (4 pairs) and boundary pairs ($|w - t_{\text{link}}| \le 6.0$) provides field staff with high-yield clerical review targets.
- At $K = 500$ pairs per 10k (240 pairs reviewed), cluster F1 reaches 0.6809 with expected cost reduced to 778.0.
