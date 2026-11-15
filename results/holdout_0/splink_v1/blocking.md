# Blocking Diagnostics: `splink_v1` on `holdout_0`

## Overview
- **Total Records ($N$)**: 4,798
- **Total Possible Pairs ($N(N-1)/2$)**: 11,508,003
- **Total True Match Pairs**: 1,469
- **Total Candidate Pairs Generated**: 45,507
- **Total True Pairs Captured**: 1,298
- **Cumulative Reduction Ratio**: 99.60%
- **Cumulative Pair Completeness (Recall Ceiling)**: 88.36%

---

## Blocking Rule Performance

| Blocking Rule | Marginal Candidates | Marginal True Pairs | Marginal Pair Completeness (%) | Cumulative Candidates | Cumulative True Pairs | Cumulative Reduction Ratio (%) | Cumulative Pair Completeness (%) |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Rule 1: given_first_skel + village_canon** | 35,764 | 1,098 | 74.74% | 35,764 | 1,098 | 99.69% | 74.74% |
| **Rule 2: phone_norm** | 189 | 150 | 10.21% | 35,841 | 1,136 | 99.69% | 77.33% |
| **Rule 3: guardian_skeleton + village_canon** | 6,252 | 775 | 52.76% | 41,360 | 1,272 | 99.64% | 86.59% |
| **Rule 4: name_skeleton + union_raw** | 5,345 | 848 | 57.73% | 44,724 | 1,295 | 99.61% | 88.16% |
| **Rule 5: given_first_skel + birth_year_est** | 1,212 | 143 | 9.73% | 45,507 | 1,298 | 99.60% | 88.36% |
