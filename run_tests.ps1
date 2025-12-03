Param(
    [switch]$RecreateVenv
)

$ErrorActionPreference = "Stop"
$venvPath = Join-Path $PSScriptRoot ".venv"

if ($RecreateVenv -and (Test-Path $venvPath)) {
    Remove-Item -Recurse -Force $venvPath
}

if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv $venvPath
}

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
. (Join-Path $venvPath "Scripts/Activate.ps1")

Write-Host "Installing dependencies..." -ForegroundColor Cyan
python -m pip install --upgrade pip > $null
python -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")

Write-Host "Running tests..." -ForegroundColor Cyan
python -m pytest -q tests
