@echo off
REM GhostPrice Weekly Product Discovery
REM Automatically discovers new electronics from Amazon Best Sellers

cd /d "%~dp0"

echo ====================================
echo GhostPrice Product Discovery
echo Started: %date% %time%
echo ====================================
echo.

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Run discovery with output to log file
python discover_products.py >> "logs\discovery_%date:~-4,4%-%date:~-10,2%-%date:~-7,2%.log" 2>&1

echo.
echo ====================================
echo Discovery Complete: %date% %time%
echo ====================================

REM Optional: Show quick stats
python view_database.py stats
