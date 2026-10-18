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

echo "[1/3] Ingesting raw CSVs into Iceberg..."
python spark/02_ingest_raw_to_iceberg.py

echo "[2/3] Building analytical datamarts (encounter & condition)..."
python spark/03_build_analytics_tables.py

echo "[3/3] Exporting refreshed summaries to MongoDB..."
python spark/04_export_mongodb.py

echo ""
echo "Refresh complete. Trino queries will see updated Iceberg snapshots."
echo "Superset dashboards will reflect new data on next chart load."
