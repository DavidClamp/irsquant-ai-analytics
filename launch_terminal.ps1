# ==============================================================================
# 🚀 IRSQUANTanalytics WORKSTATION: AUTOMATED BOOT ORCHESTRATOR
# ==============================================================================
Clear-Host

# 🛡️ Force the active PowerShell session engine to process output channels as pure UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

# 🟢 GLOBAL ENVIRONMENT INJECTION: Forces Python to append the root folder directory path natively
$env:PYTHONPATH = "."

Write-Host "================================================================================" -ForegroundColor Green
Write-Host "📊 INITIALIZING IRSQUANT NEXTGEN RUNTIME FRAMEWORK MODULES" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "📌 Node Execution Anchor Timeline: 2026-09-16" -ForegroundColor Cyan

# 1. Check for Standalone Python Virtual Workspace Environments
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "`n[VENV] Spinning up dedicated python execution shell context..." -ForegroundColor Yellow
    # 🟢 FIXED: Dot-sourcing forces the virtual environment to bind permanently to the master parent session
    . .venv\Scripts\Activate.ps1
} else {
    Write-Host "`n[WARNING] Local isolated venv paths not found. Running system binary tracks directly." -ForegroundColor Red
}

# Double-enforce pathing rules down inside the active terminal process pipeline
$env:PYTHONPATH = "."

# 2. Trigger Continuous Data Generation Matrices
Write-Host "`n[DATA] Regenerating 100-day historical options grid universes..." -ForegroundColor Yellow
python generate_vol_data.py
if ($LASTEXITCODE -ne 0) { 
    Write-Host "❌ CRITICAL: Volatility database initialization failed." -ForegroundColor Red; exit 
}
Write-Host "✔ Market parameters successfully structured inside local JSON storage blocks." -ForegroundColor Green

# 3. Execute Native C++ QuantLib SABR Optimization Loops
Write-Host "`n[MATH] Launching Levenberg-Marquardt solvers across 8 global currency blocks..." -ForegroundColor Yellow
python options_calibration.py
if ($LASTEXITCODE -ne 0) { 
    Write-Host "❌ CRITICAL: Parametric option smile calibration sequence crashed." -ForegroundColor Red; exit 
}
Write-Host "✔ Parameters calibrated and safely written to disk." -ForegroundColor Green

# 4. Spin Up Front-Office Decoupled Web Interfaces
Write-Host "`n[UI] Launching Master Presentation Router app.py Network Server..." -ForegroundColor Yellow
Write-Host "🌍 Dispatching local loop address. Point Chrome directly to: http://127.0.0.1:8050" -ForegroundColor Cyan

# Asynchronously fire up the default browser session window after a minor 2-second thread sleep delay
Start-Sleep -Seconds 2
Start-Process "http://127.0.0.1:8050"

# Boot the terminal app directly into the active foreground window pipeline
python app.py
