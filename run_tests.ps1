param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    & $Python -m venv .venv
}

. .\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
pytest -q
