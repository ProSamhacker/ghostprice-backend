# GhostPrice - Simple Task Scheduler Setup
Write-Host "Creating GhostPrice Scheduled Tasks..." -ForegroundColor Cyan

$BackendPath = "C:\Users\SAMIR\Desktop\WEBSITE\GHOST PRICE\ext\backend"
$PythonExe = "python"

# Task 1: Weekly Discovery
$action1 = New-ScheduledTaskAction -Execute $PythonExe -Argument "discover_products.py" -WorkingDirectory $BackendPath
$trigger1 = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 1:00AM
$settings1 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "GhostPrice Weekly Discovery" -Action $action1 -Trigger $trigger1 -Settings $settings1 -Force

Write-Host "✓ Created: GhostPrice Weekly Discovery (Sundays 1 AM)" -ForegroundColor Green

# Task 2: Daily Scraper  
$action2 = New-ScheduledTaskAction -Execute $PythonExe -Argument "daily_price_scraper.py" -WorkingDirectory $BackendPath
$trigger2 = New-ScheduledTaskTrigger -Daily -At 2:00AM
$settings2 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "GhostPrice Daily Scraper" -Action $action2 -Trigger $trigger2 -Settings $settings2 -Force

Write-Host "✓ Created: GhostPrice Daily Scraper (Daily 2 AM)" -ForegroundColor Green
Write-Host ""
Write-Host "✓ Setup Complete! Open taskschd.msc to view tasks." -ForegroundColor Green
