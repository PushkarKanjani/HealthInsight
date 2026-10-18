#!/usr/bin/env bash
# ==============================================================================
# HealthInsight — Full Automated Big Data Pipeline (Prompt 15)
# Engine Order: Spark Profiler -> Iceberg Ingest -> Analytics Marts -> MongoDB -> Trino Validation
# ==============================================================================

set -euo pipefail

echo "================================================================================"
echo "  HealthInsight — Big Data End-to-End Pipeline Execution"
echo "================================================================================"

# Step 0: Ensure Docker services are running
echo ""
echo "[Step 0/5] Verifying Infrastructure Services..."
docker compose up -d trino mongodb

# Step 1: Profile Source Dataset
echo ""
echo "[Step 1/5] Running Spark Dataset Profiler..."
python spark/01_profile_dataset.py

# Step 2: Ingest Raw CSVs into Iceberg
echo ""
echo "[Step 2/5] Ingesting Raw CSVs into Apache Iceberg..."
python spark/02_ingest_raw_to_iceberg.py

# Step 3: Build Curated Analytical Tables
echo ""
echo "[Step 3/5] Constructing Analytical Iceberg Datamarts..."
python spark/03_build_analytics_tables.py

# Register tables in Trino
echo ""
echo "Registering tables in Trino..."
docker exec healthinsight-trino trino --execute "
CALL iceberg.system.register_table(schema_name => 'healthcare', table_name => 'patients', table_location => 'file:/warehouse/healthcare/patients');
CALL iceberg.system.register_table(schema_name => 'healthcare', table_name => 'encounters', table_location => 'file:/warehouse/healthcare/encounters');
CALL iceberg.system.register_table(schema_name => 'healthcare', table_name => 'conditions', table_location => 'file:/warehouse/healthcare/conditions');
CALL iceberg.system.register_table(schema_name => 'healthcare', table_name => 'organizations', table_location => 'file:/warehouse/healthcare/organizations');
CALL iceberg.system.register_table(schema_name => 'healthcare', table_name => 'encounter_analytics', table_location => 'file:/warehouse/healthcare/encounter_analytics');
CALL iceberg.system.register_table(schema_name => 'healthcare', table_name => 'condition_analytics', table_location => 'file:/warehouse/healthcare/condition_analytics');
" || true

# Step 4: Export Serving Layer Aggregates to MongoDB
echo ""
echo "[Step 4/5] Exporting Analytics Aggregates to MongoDB..."
python spark/04_export_mongodb.py

# Step 5: Verify Trino Visibility
echo ""
echo "[Step 5/5] Running Trino SQL Validation Suite..."
docker exec healthinsight-trino trino --execute "
SHOW TABLES FROM iceberg.healthcare;
SELECT 'encounter_analytics' AS table_name, COUNT(*) AS total_rows FROM iceberg.healthcare.encounter_analytics;
SELECT 'condition_analytics' AS table_name, COUNT(*) AS total_rows FROM iceberg.healthcare.condition_analytics;
"

echo ""
echo "================================================================================"
echo "  HEALTHINSIGHT PIPELINE EXECUTION FINISHED SUCCESSFULLY (Exit Code 0)"
echo "================================================================================"
