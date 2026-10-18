#!/bin/bash
# HealthInsight v2 — Clinical AI Command Center Portal Launcher (Bash)

echo "================================================================================"
echo "  STARTING HEALTHINSIGHT v2 CLINICAL AI COMMAND CENTER"
echo "  URL: http://localhost:5000"
echo "  Default Login: admin / healthinsight2024"
echo "================================================================================"

python -m uvicorn portal.server:app --host 0.0.0.0 --port 5000 --reload
