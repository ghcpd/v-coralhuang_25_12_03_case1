# Run all tests for the user display module

param(
    [switch]$Coverage,
    [switch]$Verbose
)

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Change to project directory
Set-Location $scriptDir

Write-Host "User Display Module - Test Suite" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "ERROR: Python not found in PATH" -ForegroundColor Red
    exit 1
}

# Display Python version
$pythonVersion = python --version 2>&1
Write-Host "Using: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Run tests
Write-Host "Running test suite..." -ForegroundColor Yellow
Write-Host ""

$testCommand = "python -m unittest discover -s tests -p 'test_*.py' -v"

if ($Verbose) {
    Write-Host "Command: $testCommand" -ForegroundColor Gray
}

# Execute tests
Invoke-Expression $testCommand
$testResult = $LASTEXITCODE

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan

if ($testResult -eq 0) {
    Write-Host "✓ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "✗ Some tests failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "Test files:" -ForegroundColor Cyan
Write-Host "  - tests/test_functional.py    (Formatting, filtering, storage)"
Write-Host "  - tests/test_robustness.py    (Error handling, edge cases)"
Write-Host "  - tests/test_performance.py   (Performance targets validation)"
Write-Host "  - tests/test_concurrency.py   (Thread-safety, concurrent access)"
Write-Host ""

exit $testResult
