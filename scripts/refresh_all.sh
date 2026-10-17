#!/bin/bash
# scripts/refresh_all.sh
# Full data refresh: reruns Spark pipeline (phases 2-4) and verifies MongoDB.
# Use this when new/updated CSV files are placed in data/raw/.

set -e

if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

SPARK_SUBMIT="$SPARK_HOME/bin/spark-submit"
JARS="$ICEBERG_JAR,$MONGO_JAR"

echo "=== HealthInsight Full Refresh ==="
echo ""

echo "[1/3] Recreating Iceberg tables from latest CSVs..."
$SPARK_SUBMIT --master local[*] --jars "$JARS" spark/02_create_iceberg_tables.py

echo "[2/3] Running transformation pipeline..."
$SPARK_SUBMIT --master local[*] --jars "$JARS" spark/03_transform_healthcare_data.py

echo "[3/3] Exporting refreshed summaries to MongoDB..."
$SPARK_SUBMIT --master local[*] --jars "$JARS" spark/04_export_mongodb.py

echo ""
echo "Refresh complete. Trino queries will see updated Iceberg snapshots."
echo "Superset dashboards will reflect new data on next chart load."
