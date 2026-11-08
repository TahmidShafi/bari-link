param([Parameter(Mandatory = $true)][string]$Message)

.venv\Scripts\ruff check .
if ($LASTEXITCODE -ne 0) { Write-Host "STOP: ruff failed" -ForegroundColor Red; exit 1 }

git add .
git commit -m $Message
if ($LASTEXITCODE -ne 0) { Write-Host "STOP: commit failed" -ForegroundColor Red; exit 1 }

.venv\Scripts\python scripts\prove_ci.py
if ($LASTEXITCODE -ne 0) { Write-Host "STOP: CI proof failed - NOT pushing" -ForegroundColor Red; exit 1 }

git push