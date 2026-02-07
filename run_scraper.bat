@echo off
REM GhostPrice Daily Price Scraper
REM Updates prices for all tracked products

cd /d "%~dp0"

echo ====================================
echo GhostPrice Price Scraper
echo Started: %date% %time%
echo ====================================
echo.

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Run scraper with output to log file
python daily_price_scraper.py >> "logs\scraper_%date:~-4,4%-%date:~-10,2%-%date:~-7,2%.log" 2>&1

echo.
echo ====================================
echo Scraping Complete: %date% %time%
echo ====================================

REM Optional: Show quick stats
python view_database.py stats
