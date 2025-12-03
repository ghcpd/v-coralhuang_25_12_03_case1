# Run tests in this repository: creates venv if missing, installs requirements, and runs pytest
$venv = ".\.venv"
if (-not (Test-Path $venv)) {
    python -m venv $venv
}
& $venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
