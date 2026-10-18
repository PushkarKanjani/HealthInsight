# HealthInsight Version Check (PowerShell)
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " HealthInsight Environment & Version Audit" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

Write-Host "`n[1] Operating System:" -ForegroundColor Yellow
(Get-CimInstance Win32_OperatingSystem).Caption + " (Build " + (Get-CimInstance Win32_OperatingSystem).BuildNumber + ")"

Write-Host "`n[2] PowerShell Version:" -ForegroundColor Yellow
$PSVersionTable.PSVersion.ToString()

Write-Host "`n[3] Python Version:" -ForegroundColor Yellow
try { & python --version } catch { Write-Host "Python not found in PATH" -ForegroundColor Red }

Write-Host "`n[4] Java Version:" -ForegroundColor Yellow
try { & java -version } catch { Write-Host "Java not found in PATH" -ForegroundColor Red }

Write-Host "`n[5] Apache Spark (spark-submit):" -ForegroundColor Yellow
try { & spark-submit --version } catch { Write-Host "spark-submit not found in PATH" -ForegroundColor Red }

Write-Host "`n[6] Trino CLI:" -ForegroundColor Yellow
try { & trino --version } catch { Write-Host "trino not found in PATH" -ForegroundColor Red }

Write-Host "`n[7] MongoDB Server (mongod):" -ForegroundColor Yellow
try { & mongod --version } catch { Write-Host "mongod not found in PATH" -ForegroundColor Red }

Write-Host "`n[8] MongoDB Shell (mongosh):" -ForegroundColor Yellow
try { & mongosh --version } catch { Write-Host "mongosh not found in PATH" -ForegroundColor Red }

Write-Host "`n[9] Docker Daemon:" -ForegroundColor Yellow
try { & docker --version } catch { Write-Host "Docker not found in PATH" -ForegroundColor Red }

Write-Host "`n=========================================" -ForegroundColor Cyan
