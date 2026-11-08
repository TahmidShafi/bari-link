# Bari-Link System & Verification Audit

**Audit Date:** 2026-11-08  
**Operating System:** Windows 11 (PowerShell)  
**Python Version:** Python 3.14.6 (Virtualenv `.venv`)  
**Node Version:** v22.14.0  

This document logs real command outputs from the final pre-release hardening audit (Phase 10).

---

## 1. Documentation & Markdown Link Integrity

Command:
```bash
python scripts/check_links.py
```
Output:
```text
All relative links in 3 markdown files resolved successfully.
```

---

## 2. README Automated Results Render Check

Command:
```bash
python scripts/render_readme.py --check
```
Output:
```text
README.md results block is UP TO DATE.
```

---

## 3. Git Tracking & Artifact Hygiene

### 3.1 Tracked File Size Audit (> 5 MB)
Command:
```powershell
git ls-files | ForEach-Object { $item = Get-Item $_ -ErrorAction SilentlyContinue; if ($item.Length -gt 5MB) { [PSCustomObject]@{ Path = $_; SizeMB = [math]::Round($item.Length / 1MB, 2) } } }
```
Output:
```text
(Zero files over 5 MB tracked)
```

### 3.2 Working Tree Status & Untracked Files
Command:
```bash
git status --short
```
Output:
```text
 M PROJECT_CONTEXT.md
 M README.md
 M docs/screenshots/findings.png
 M docs/screenshots/households.png
 M docs/screenshots/pairs.png
 M results/summary/confirm_table.json
 M scripts/export_fixture.py
 M src/barilink/cli.py
 M src/barilink/evaluate/summary.py
 M src/barilink/pipeline.py
 M tests/test_pipeline.py
 M web/e2e/smoke.spec.ts
 M web/src/tests/fixtures/pair_labels_100.json
 M web/src/tests/fixtures/pairs_sample.json
 M web/src/tests/fixtures/raw_eval_fixture.json
?? .gitattributes
?? LICENSE
?? docs/AUDIT.md
?? docs/METHODS.md
?? results/summary/preregistration.json
?? results/summary/untrained_params_audit.json
?? scripts/check_links.py
?? scripts/generate_preregistration_json.py
?? scripts/render_readme.py
?? src/barilink/evaluate/audit_untrained.py
?? tests/test_pipeline_determinism.py
?? tests/test_readme_render.py
?? web/src/tests/fixtures/e2e_target.json
```

---

## 4. Code Quality & Linter Audits

### 4.1 Python Code Style (Ruff)
Command:
```bash
ruff check .
```
Output:
```text
All checks passed!
```

### 4.2 Web Code Style (ESLint)
Command:
```bash
npm run lint --prefix web
```
Output:
```text
> bari-link-web@1.0.0 lint
> eslint src --ext .ts,.tsx
```

---

## 5. Automated Test Suites

### 5.1 CI Test Suite (Unit, Regression & Hashseed Determinism)
Command:
```bash
pytest -q -m "not publish and not artifacts"
```
Output:
```text
93 passed, 15 deselected in 50.46s
```

### 5.2 Artifact Verification Suite (Golden Metrics & Leakage Bounds)
Command:
```bash
pytest -q -m artifacts
```
Output:
```text
11 passed, 97 deselected in 4.51s
```

### 5.3 Publish Profile Suite
Command:
```bash
pytest -q -m publish
```
Output:
```text
4 passed, 104 deselected in 1.12s
```

### 5.4 Web Unit & AST Suite (Vitest)
Command:
```bash
npm test --prefix web
```
Output:
```text
> bari-link-web@1.0.0 test
> vitest run

 RUN  v2.1.9 D:/bari-link/web

 ✓ src/tests/unionfind.test.ts (4 tests) 2ms
 ✓ src/tests/eval_isolation.test.ts (2 tests) 13ms
 ✓ src/tests/waterfall.test.ts (5 tests) 25ms
 ✓ src/tests/raw_metrics.test.ts (2 tests) 131ms
 ✓ src/tests/findings_no_hardcoded_numbers.test.ts (2 tests) 21ms

 Test Files  5 passed (5)
      Tests  15 passed (15)
   Duration  597ms
```

### 5.5 Static Web Build (TypeScript & Vite)
Command:
```bash
npm run build --prefix web
```
Output:
```text
> bari-link-web@1.0.0 build
> tsc && vite build

vite v6.4.5 building for production...
transforming...
✓ 220 modules transformed.
rendering chunks...
computing gzip size...
dist/assets/unionfind.worker-Bn1gdN7N.js    1.05 kB
dist/index.html                             1.22 kB │ gzip:   0.70 kB
dist/assets/index-2E6L89Sw.css              8.08 kB │ gzip:   2.19 kB
dist/assets/index-xX3ONiH2.js             696.78 kB │ gzip: 208.73 kB
✓ built in 1.65s
```

### 5.6 End-to-End Browser Test Suite (Playwright)
Command:
```bash
npm run test:e2e --prefix web
```
Output:
```text
> bari-link-web@1.0.0 test:e2e
> playwright test

Running 2 tests using 2 workers

[PERF REPORT] First Meaningful Paint: 120.2 ms | Full DuckDB Ready: 1949.5 ms | Slider Latency: 76.7 ms
[PERF REPORT] First Meaningful Paint: 113.0 ms | Full DuckDB Ready: 1951.7 ms | Slider Latency: 74.3 ms
  ok 1 [mobile] › e2e\smoke.spec.ts:15:3 › Bari-Link Static Web App E2E Smoke Tests › full workflow: overview, slider, pair explorer, households, findings (4.1s)
  ok 2 [chromium] › e2e\smoke.spec.ts:15:3 › Bari-Link Static Web App E2E Smoke Tests › full workflow: overview, slider, pair explorer, households, findings (4.4s)

  2 passed (5.9s)
```

---

## 6. Pipeline Determinism Verification

Command:
```bash
python -m barilink.cli pipeline --profile publish --verify
```
Output:
```text
======================================================================
PIPELINE DETERMINISM VERIFICATION
======================================================================
Run Name:      publish_holdout_5
Expected File: results\publish\expected_headline.json
Tolerance:     Rates/F1 <= 0.005, Counts <= 1.0%
----------------------------------------------------------------------
Metric                           Expected     Actual       Diff       Status
----------------------------------------------------------------------
Person Cluster Precision         0.9651       0.9651       0.0000     PASS
Person Cluster Recall            0.5566       0.5566       0.0000     PASS
Person Cluster F1                0.7060       0.7060       0.0000     PASS
Person Expected Cost             784.0000     784.0000     0.0000     PASS
False-Merge Clusters             23           23           0          PASS
Split Persons                    427          427          0          PASS
Dedup Reach (Clusters)           4136         4136         0          PASS
Doppelganger FM Rate             0.0127       0.0127       0.0000     PASS
Household Record Precision       0.7027       0.7027       0.0000     PASS
Household Record Recall          0.3524       0.3524       0.0000     PASS
Household Record F1              0.4694       0.4694       0.0000     PASS
Household Unit B-cubed F1        0.7536       0.7536       0.0000     PASS
Household Size MAE               2.0105       2.0105       0.0000     PASS
Household Reached Error %        57.8993      57.8993      0.0000     PASS
Inferred Households              3608         3608         0          PASS
----------------------------------------------------------------------
ALL METRICS WITHIN TOLERANCE -> VERIFICATION PASSED ✓
```

---

## 7. Live Production Endpoint Accessibility (GitHub Pages)

Command:
```python
import urllib.request

urls = [
    "https://tahmidshafi.github.io/bari-link/",
    "https://tahmidshafi.github.io/bari-link/data/manifest.json",
]
for u in urls:
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    resp = urllib.request.urlopen(req)
    print(u, resp.status)
```
Output:
```text
https://tahmidshafi.github.io/bari-link/ 200
https://tahmidshafi.github.io/bari-link/data/manifest.json 200
```

