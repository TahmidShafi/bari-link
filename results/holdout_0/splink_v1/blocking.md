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

The table below breaks down the candidate generation and true-pair capture for each blocking rule evaluated sequentially in the union:

| Blocking Rule | Marginal Candidates | Marginal True Pairs | Marginal Pair Completeness (%) | Cumulative Candidates | Cumulative True Pairs | Cumulative Reduction Ratio (%) | Cumulative Pair Completeness (%) |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Rule 1**: `given_first_skel` AND `village_canon` | 35,764 | 1,098 | 74.74% | 35,764 | 1,098 | 99.69% | 74.74% |
| **Rule 2**: `phone_norm` | 189 | 150 | 10.21% | 35,841 | 1,136 | 99.69% | 77.33% |
| **Rule 3**: `guardian_skeleton` AND `village_canon` | 6,252 | 775 | 52.76% | 41,360 | 1,272 | 99.64% | 86.59% |
| **Rule 4**: `name_skeleton` AND `union_raw` | 5,345 | 848 | 57.73% | 44,724 | 1,295 | 99.61% | 88.16% |
| **Rule 5**: `given_first_skel` AND `birth_year_est` | 1,212 | 143 | 9.73% | 45,507 | 1,298 | 99.60% | 88.36% |

---

## Observations & Analysis

1. **High Search Space Reduction**:
   The multi-rule blocking strategy reduces the comparison search space from 11.5M pairs down to 45,507 candidates (a 99.60% reduction ratio), making probabilistic linkage fast and tractable in DuckDB while retaining 88.36% of all true matching pairs.

2. **Primary Driver**:
   Rule 1 (`given_first_skel` + `village_canon`) captures the vast majority of true matches (74.74% marginal completeness) while generating only 35,764 candidate comparisons.

3. **Complementary Rules**:
   - Rule 2 (`phone_norm`) has extreme precision: only 189 candidates generated, of which 150 are true matches (79.4% precision), recovering true cross-village or corrupted-village matches that Rule 1 missed.
   - Rule 3 (`guardian_skeleton` + `village_canon`) adds substantial recall (raising cumulative completeness to 86.59%), capturing beneficiaries whose given names suffered severe transliteration or typographical corruption but whose guardian name remained identifiable.
   - Rule 4 (`name_skeleton` + `union_raw`) broadens geographic tolerance across villages within the same union, adding 23 new true pairs.
   - Rule 5 (`given_first_skel` + `birth_year_est`) recovers 3 additional cross-union/village matches with estimated birth year agreement.

4. **Ceiling Analysis (Missed True Pairs)**:
   A total of 171 true pairs (11.64% of 1,469) were unblocked. These represent cases where multiple fields simultaneously corrupted across records (e.g. absent/mismatched phone, severe given name and guardian name transliteration/typos, or cross-village displacement), which cannot be recovered without wider or fuzzy indexing rules that would increase candidate volume.

