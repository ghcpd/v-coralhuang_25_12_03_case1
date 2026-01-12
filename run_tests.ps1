# User Display Module - One-Click Test Runner
# This script runs all tests in the tests/ directory

Write-Host "================================" -ForegroundColor Cyan
Write-Host "User Display Module - Test Runner" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Check if Python is available
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} else {
    Write-Host "ERROR: Python not found. Please install Python 3.8 or later." -ForegroundColor Red
    exit 1
}

Write-Host "Using Python: $pythonCmd" -ForegroundColor Green
& $pythonCmd --version
Write-Host ""

# Check Python version (require 3.8+)
$version = & $pythonCmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$majorMinor = $version -split '\.'
if ([int]$majorMinor[0] -lt 3 -or ([int]$majorMinor[0] -eq 3 -and [int]$majorMinor[1] -lt 8)) {
    Write-Host "ERROR: Python 3.8+ required (found $version)" -ForegroundColor Red
    exit 1
}

Write-Host "Python version check: OK" -ForegroundColor Green
Write-Host ""

# Run functional tests
Write-Host "================================" -ForegroundColor Yellow
Write-Host "Running Functional Tests..." -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Yellow
& $pythonCmd -m unittest tests.test_functional -v
$functionalResult = $LASTEXITCODE

Write-Host ""

# Run performance tests
Write-Host "================================" -ForegroundColor Yellow
Write-Host "Running Performance Tests..." -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Yellow
& $pythonCmd -m unittest tests.test_performance -v
$performanceResult = $LASTEXITCODE

Write-Host ""

# Run robustness tests
Write-Host "================================" -ForegroundColor Yellow
Write-Host "Running Robustness Tests..." -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Yellow
& $pythonCmd -m unittest tests.test_robustness -v
$robustnessResult = $LASTEXITCODE

Write-Host ""

# Run concurrency tests
Write-Host "================================" -ForegroundColor Yellow
Write-Host "Running Concurrency Tests..." -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Yellow
& $pythonCmd -m unittest tests.test_concurrency -v
$concurrencyResult = $LASTEXITCODE

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Display results
$allPassed = $true

if ($functionalResult -eq 0) {
    Write-Host "✓ Functional Tests: PASSED" -ForegroundColor Green
} else {
    Write-Host "✗ Functional Tests: FAILED" -ForegroundColor Red
    $allPassed = $false
}

if ($performanceResult -eq 0) {
    Write-Host "✓ Performance Tests: PASSED" -ForegroundColor Green
} else {
    Write-Host "✗ Performance Tests: FAILED" -ForegroundColor Red
    $allPassed = $false
}

if ($robustnessResult -eq 0) {
    Write-Host "✓ Robustness Tests: PASSED" -ForegroundColor Green
} else {
    Write-Host "✗ Robustness Tests: FAILED" -ForegroundColor Red
    $allPassed = $false
}

if ($concurrencyResult -eq 0) {
    Write-Host "✓ Concurrency Tests: PASSED" -ForegroundColor Green
} else {
    Write-Host "✗ Concurrency Tests: FAILED" -ForegroundColor Red
    $allPassed = $false
}

Write-Host ""

if ($allPassed) {
    Write-Host "================================" -ForegroundColor Green
    Write-Host "ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    exit 0
} else {
    Write-Host "================================" -ForegroundColor Red
    Write-Host "SOME TESTS FAILED" -ForegroundColor Red
    Write-Host "================================" -ForegroundColor Red
    exit 1
}
