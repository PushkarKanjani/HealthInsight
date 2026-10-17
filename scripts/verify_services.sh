#!/bin/bash
# scripts/verify_services.sh
# Verify all HealthInsight services are running and at correct versions.
# Run this before starting the pipeline.

set -e

echo "==================================================================="
echo "  HealthInsight — Service Verification"
echo "==================================================================="

# --- Java ---
echo ""
echo "--- Java ---"
java -version 2>&1
if [[ $? -ne 0 ]]; then
  echo "ERROR: Java not found. Install Java 17."
  exit 1
fi

# --- Spark ---
echo ""
echo "--- Apache Spark ---"
if [ -z "$SPARK_HOME" ]; then
  echo "WARNING: SPARK_HOME not set. Set it in .env"
else
  $SPARK_HOME/bin/spark-submit --version 2>&1
fi

# --- Python ---
echo ""
echo "--- Python ---"
python3 --version
python3 -c "import pyspark; print('PySpark:', pyspark.__version__)" 2>/dev/null || echo "PySpark not installed"
python3 -c "import pymongo; print('PyMongo:', pymongo.__version__)" 2>/dev/null || echo "PyMongo not installed"

# --- Trino ---
echo ""
echo "--- Trino ---"
TRINO_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/v1/info 2>/dev/null)
if [ "$TRINO_STATUS" = "200" ]; then
  echo "Trino is running at localhost:8080"
  curl -s http://localhost:8080/v1/info | python3 -m json.tool 2>/dev/null || true
else
  echo "ERROR: Trino not reachable at localhost:8080 (HTTP $TRINO_STATUS)"
  echo "Start Trino with: $TRINO_HOME/bin/launcher start"
fi

# --- MongoDB ---
echo ""
echo "--- MongoDB ---"
MONGO_STATUS=$(mongosh --quiet --eval "db.adminCommand({ping:1}).ok" 2>/dev/null)
if [ "$MONGO_STATUS" = "1" ]; then
  echo "MongoDB is running."
  mongosh --quiet --eval "db.adminCommand({serverStatus:1}).version" 2>/dev/null || true
else
  echo "ERROR: MongoDB not running."
  echo "Start with: mongod --dbpath /path/to/data"
fi

echo ""
echo "==================================================================="
echo "  Verification complete."
echo "==================================================================="
