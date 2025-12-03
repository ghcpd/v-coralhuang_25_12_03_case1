# PowerShell script to run all tests for the user_display module

Write-Host "======================================" -ForegroundColor Green
Write-Host "User Display Module - Test Runner" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$testsDir = Join-Path $scriptDir "tests"

# Check if tests directory exists
if (-not (Test-Path $testsDir)) {
    Write-Host "ERROR: tests directory not found at $testsDir" -ForegroundColor Red
    exit 1
}

Write-Host "Running tests from: $testsDir" -ForegroundColor Cyan
Write-Host ""

# Run all test files
$testFiles = @(
    "test_functional.py",
    "test_robustness.py",
    "test_concurrency.py",
    "test_performance.py"
)

$totalPassed = 0
$totalFailed = 0
$totalErrors = 0

foreach ($testFile in $testFiles) {
    $testPath = Join-Path $testsDir $testFile
    
    if (Test-Path $testPath) {
        Write-Host "Running: $testFile" -ForegroundColor Yellow
        Write-Host "---" -ForegroundColor Gray
        
        # Run the test
        python -m pytest "$testPath" -v 2>&1 | ForEach-Object {
            Write-Host $_
        }
        
        Write-Host ""
    } else {
        Write-Host "WARNING: Test file not found: $testPath" -ForegroundColor Yellow
    }
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "Test run completed" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "To run specific test file:" -ForegroundColor Cyan
Write-Host "  python -m pytest tests/test_functional.py -v" -ForegroundColor Gray
Write-Host "  python -m pytest tests/test_robustness.py -v" -ForegroundColor Gray
Write-Host "  python -m pytest tests/test_concurrency.py -v" -ForegroundColor Gray
Write-Host "  python -m pytest tests/test_performance.py -v" -ForegroundColor Gray
Write-Host ""
Write-Host "To run all tests with coverage:" -ForegroundColor Cyan
Write-Host "  python -m pytest tests/ -v --cov=user_display" -ForegroundColor Gray
Write-Host ""
