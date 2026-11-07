# bari-link

Kinship-aware probabilistic deduplication of NGO beneficiary registries in rural Bangladesh where national identification numbers are unavailable.

## Overview
In rural Bangladesh, humanitarian cash and voucher delivery programs face significant deduplication challenges due to the absence of universal digital IDs, prevalent phonetic spelling variations, and high name collision rates. `bari-link` jointly resolves individuals and households across independent enrolment modules by treating household co-residence and kinship networks (paternal and spousal relationships) as primary linkage evidence.

For detailed architecture, hard rules, and design rationale, see [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md).

## Quickstart

### Prerequisites
- Python 3.11+
- Virtual environment (`.venv`)

### Installation
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -e .[dev]
```

### Generating Synthetic Ground-Truth Data
```bash
python -m barilink.cli generate --config configs/default.yaml --run-name demo
```

Outputs will be generated in `data/generated/demo/`:
- `persons.parquet` and `persons.csv`
- `households.parquet` and `households.csv`
- `manifest.json`

### Running Tests and Linting
```bash
pytest -q -m "not publish and not artifacts"
ruff check .
```

### Static Web Application & Offline Fixtures
The browser application in `web/` runs client-side on DuckDB-Wasm and deploys to GitHub Pages:
```bash
# Regenerate Vitest fixtures from published web data
python scripts/export_fixture.py

# Web development & test suite
npm ci --prefix web
npm run lint --prefix web
npm test --prefix web
npm run build --prefix web
npm run test:e2e --prefix web
npm run perf --prefix web  # Standalone performance audit via web/scripts/measure_perf.cjs
```

