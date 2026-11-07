# Linkage Error Diagnosis: `splink_v1` on `demo`

This report evaluates linking errors on the DEV dataset (`demo`) at the frozen operational threshold $t_{\text{cost}} = 9.25$.

## Summary Metrics

- **Total Scored Candidate Pairs**: 49,984
- **Total Candidate True Pairs**: 1,263
- **Missed True Candidate Pairs (False Negatives)**: 708 (56.06%)
- **False Merges at $t_{\text{cost}}$ (False Positives)**: 23

---

## 1. Missed True Candidate Pairs Analysis

### A. Guardian Type Raw Combination

| Guardian Type Combination | Count | Percentage |
| :--- | :--- | :--- |
| `both null` | 396 | 55.93% |
| `null/known` | 308 | 43.50% |
| `husband/husband` | 3 | 0.42% |
| `father/husband` | 1 | 0.14% |

### B. True Guardian Switch vs Same Guardian

| Relationship Status | Count | Percentage |
| :--- | :--- | :--- |
| `Same guardian` | 463 | 65.40% |
| `True guardian switch` | 245 | 34.60% |

### C. Cross-Module Pair Distribution

| Module Pair | Count | Percentage |
| :--- | :--- | :--- |
| `livelihood_support vs microfinance_group` | 270 | 38.14% |
| `microfinance_group vs upg_enrolment` | 229 | 32.34% |
| `livelihood_support vs upg_enrolment` | 75 | 10.59% |
| `club_formation vs microfinance_group` | 50 | 7.06% |
| `microfinance_group vs microfinance_group` | 36 | 5.08% |
| `club_formation vs livelihood_support` | 20 | 2.82% |
| `club_formation vs club_formation` | 11 | 1.55% |
| `livelihood_support vs livelihood_support` | 9 | 1.27% |
| `club_formation vs upg_enrolment` | 4 | 0.56% |
| `upg_enrolment vs upg_enrolment` | 4 | 0.56% |

### D. Null Field Count Across Pair (out of 20 raw fields)

| Null Count | Count | Percentage |
| :--- | :--- | :--- |
| 2 | 1 | 0.14% |
| 3 | 4 | 0.56% |
| 4 | 14 | 1.98% |
| 5 | 36 | 5.08% |
| 6 | 46 | 6.50% |
| 7 | 102 | 14.41% |
| 8 | 156 | 22.03% |
| 9 | 179 | 25.28% |
| 10 | 68 | 9.60% |
| 11 | 35 | 4.94% |
| 12 | 56 | 7.91% |
| 13 | 11 | 1.55% |

### E. Most Damaging Bayes Factor

Comparison whose log2 Bayes factor was most negative, pulling match weight below $t_{\text{cost}}$:

| Damaging Comparison | Count | Percentage |
| :--- | :--- | :--- |
| `kinship` | 364 | 51.41% |
| `guardian_name` | 137 | 19.35% |
| `title_token` | 72 | 10.17% |
| `phone` | 69 | 9.75% |
| `given_name` | 61 | 8.62% |
| `birth_year` | 5 | 0.71% |

---

## 2. False Merges Analysis

### A. Ground-Truth Relationship of Erroneously Merged Pairs

| Ground-Truth Relationship | Count | Percentage |
| :--- | :--- | :--- |
| `Same household (Sibling)` | 20 | 86.96% |
| `Same household (Parent-Child)` | 3 | 13.04% |

### B. Comparison Features Driving False Merges (Positive Bayes Factors)

Number of false-merge pairs where the comparison contributed $\text{BF} > 1.0$ (positive log-odds):

| Comparison Feature | Pairs with Positive BF | Fraction of False Merges |
| :--- | :--- | :--- |
| `kinship` | 23 | 100.00% |
| `union_raw` | 23 | 100.00% |
| `village` | 23 | 100.00% |
| `guardian_name` | 22 | 95.65% |
| `birth_year` | 14 | 60.87% |
| `phone` | 8 | 34.78% |
| `title_token` | 2 | 8.70% |
| `given_name` | 1 | 4.35% |
| `sex_raw` | 0 | 0.00% |
