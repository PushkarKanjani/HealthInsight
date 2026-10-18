# HealthInsight v2 — Clinical AI Command Center Portal Launcher (PowerShell)
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  STARTING HEALTHINSIGHT v2 CLINICAL AI COMMAND CENTER" -ForegroundColor Cyan
Write-Host "  URL: http://localhost:5000" -ForegroundColor Yellow
Write-Host "  Default Login: admin / healthinsight2024" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan

python -m uvicorn portal.server:app --host 0.0.0.0 --port 5000 --reload
