# LifeCycle Backend Setup Script
# Run this to initialize the database and start the API server

Write-Host "🚀 LifeCycle Backend Setup" -ForegroundColor Cyan
Write-Host "=" * 50

# Step 1: Check Python
Write-Host "`n📦 Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not found! Please install Python 3.11+" -ForegroundColor Red
    exit 1
}
Write-Host "✅ $pythonVersion" -ForegroundColor Green

# Step 2: Install dependencies
Write-Host "`n📦 Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Step 3: Initialize database
Write-Host "`n📊 Initializing database..." -ForegroundColor Yellow
python init_db.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Database initialization failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Database initialized" -ForegroundColor Green

# Step 4: Start API server
Write-Host "`n🌐 Starting API server..." -ForegroundColor Yellow
Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""
python main.py
