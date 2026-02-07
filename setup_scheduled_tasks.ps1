# GhostPrice - Automated Task Scheduler Setup
# This script creates Windows scheduled tasks for product discovery and price scraping

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GhostPrice Task Scheduler Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get current directory (backend folder)
$BackendPath = $PSScriptRoot
$PythonExe = "python"

# Verify Python is available
try {
    $pythonVersion = & $PythonExe --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found in PATH!" -ForegroundColor Red
    Write-Host "Please install Python or add it to PATH" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Creating scheduled tasks..." -ForegroundColor Yellow
Write-Host ""

# Task 1: Weekly Product Discovery
Write-Host "1. Creating 'GhostPrice Weekly Discovery' task..." -ForegroundColor White

$discoveryAction = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument "discover_products.py" `
    -WorkingDirectory $BackendPath

$discoveryTrigger = New-ScheduledTaskTrigger `
    -Weekly `
    -DaysOfWeek Sunday `
    -At 1:00AM

$discoverySettings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

$discoveryTask = Register-ScheduledTask `
    -TaskName "GhostPrice Weekly Discovery" `
    -Description "Discovers new electronics products from Amazon Best Sellers, New Releases, and Trending lists" `
    -Action $discoveryAction `
    -Trigger $discoveryTrigger `
    -Settings $discoverySettings `
    -Force

if ($discoveryTask) {
    Write-Host "   ✓ Weekly Discovery task created" -ForegroundColor Green
    Write-Host "   ⏰ Runs: Every Sunday at 1:00 AM" -ForegroundColor Gray
} else {
    Write-Host "   ✗ Failed to create Weekly Discovery task" -ForegroundColor Red
}

Write-Host ""

# Task 2: Daily Price Scraping
Write-Host "2. Creating 'GhostPrice Daily Scraper' task..." -ForegroundColor White

$scraperAction = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument "daily_price_scraper.py" `
    -WorkingDirectory $BackendPath

$scraperTrigger = New-ScheduledTaskTrigger `
    -Daily `
    -At 2:00AM

$scraperSettings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

$scraperTask = Register-ScheduledTask `
    -TaskName "GhostPrice Daily Scraper" `
    -Description "Updates prices for all tracked electronics products daily" `
    -Action $scraperAction `
    -Trigger $scraperTrigger `
    -Settings $scraperSettings `
    -Force

if ($scraperTask) {
    Write-Host "   ✓ Daily Scraper task created" -ForegroundColor Green
    Write-Host "   ⏰ Runs: Every day at 2:00 AM" -ForegroundColor Gray
} else {
    Write-Host "   ✗ Failed to create Daily Scraper task" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tasks created:" -ForegroundColor Yellow
Write-Host "  1. GhostPrice Weekly Discovery  - Sundays at 1:00 AM" -ForegroundColor White
Write-Host "  2. GhostPrice Daily Scraper     - Daily at 2:00 AM" -ForegroundColor White
Write-Host ""
Write-Host "To view tasks:" -ForegroundColor Yellow
Write-Host "  • Press Win+R, type 'taskschd.msc', press Enter" -ForegroundColor Gray
Write-Host "  • Look for 'GhostPrice' tasks in Task Scheduler Library" -ForegroundColor Gray
Write-Host ""
Write-Host "To test tasks now (without waiting):" -ForegroundColor Yellow
Write-Host "  • Right-click task → Run" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
