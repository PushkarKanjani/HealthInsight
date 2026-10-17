#!/bin/bash
# scripts/run_spark_pipeline.sh
# Runs all four Spark phases in sequence.
# Stop on any failure (set -e).

set -e

# Load environment
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "ERROR: .env file not found. Copy .env.example to .env and configure it."
  exit 1
fi

SPARK_SUBMIT="$SPARK_HOME/bin/spark-submit"
JARS="$ICEBERG_JAR,$MONGO_JAR"

echo "==================================================================="
echo "  HealthInsight Spark Pipeline"
echo "==================================================================="

# ---- Phase 1: Profile ----
echo ""
echo "[Phase 1] Profiling dataset..."
$SPARK_SUBMIT \
  --master local[*] \
  spark/01_profile_dataset.py
echo "Phase 1 complete."

# ---- Phase 2: Create Iceberg Tables ----
echo ""
echo "[Phase 2] Creating Iceberg tables..."
$SPARK_SUBMIT \
  --master local[*] \
  --jars "$JARS" \
  spark/02_create_iceberg_tables.py
echo "Phase 2 complete."

# ---- Phase 3: Transform ----
echo ""
echo "[Phase 3] Running transformations..."
$SPARK_SUBMIT \
  --master local[*] \
  --jars "$JARS" \
  spark/03_transform_healthcare_data.py
echo "Phase 3 complete."

# ---- Phase 4: Export to MongoDB ----
echo ""
echo "[Phase 4] Exporting to MongoDB..."
$SPARK_SUBMIT \
  --master local[*] \
  --jars "$JARS" \
  spark/04_export_mongodb.py
echo "Phase 4 complete."

echo ""
echo "==================================================================="
echo "  Pipeline finished successfully."
echo "  Next: Run Trino SQL queries and verify MongoDB collections."
echo "==================================================================="
