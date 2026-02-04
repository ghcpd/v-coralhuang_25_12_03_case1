#!/usr/bin/env pwsh
Write-Host "Setting up virtual environment and running tests..."

# Use current Python; user environments vary so we assume python is available.
python -m pip install -r requirements.txt
pytest -q
