# ==============================================================================
# HealthInsight — Full Automated Big Data Pipeline for Windows PowerShell (Prompt 15)
# Engine Order: Spark Profiler -> Iceberg Ingest -> Analytics Marts -> MongoDB -> Trino Validation
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "  HealthInsight — Big Data End-to-End Pipeline Execution (PowerShell)" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# Step 0: Ensure Docker services are running
Write-Host "`n[Step 0/5] Verifying Infrastructure Services..." -ForegroundColor Yellow
docker compose up -d trino mongodb

# Step 1: Profile Source Dataset
Write-Host "`n[Step 1/5] Running Spark Dataset Profiler..." -ForegroundColor Yellow
python spark/01_profile_dataset.py
if ($LASTEXITCODE -ne 0) { throw "Dataset Profiler failed with exit code $LASTEXITCODE" }

# Step 2: Ingest Raw CSVs into Iceberg
Write-Host "`n[Step 2/5] Ingesting Raw CSVs into Apache Iceberg..." -ForegroundColor Yellow
python spark/02_ingest_raw_to_iceberg.py
if ($LASTEXITCODE -ne 0) { throw "Raw Ingestion failed with exit code $LASTEXITCODE" }

# Step 3: Build Curated Analytical Tables
Write-Host "`n[Step 3/5] Constructing Analytical Iceberg Datamarts..." -ForegroundColor Yellow
python spark/03_build_analytics_tables.py
if ($LASTEXITCODE -ne 0) { throw "Analytics Table Construction failed with exit code $LASTEXITCODE" }

# Register tables in Trino
Write-Host "`nRegistering tables in Trino..." -ForegroundColor Yellow
docker exec healthinsight-trino trino --execute "
CALL iceberg.system.register_table(schema_name => 'healthcare', table_name => 'patients', table_location => 'file:/warehouse/healthcare/patients');
CALL iceberg.system.register_table(schema_name => 'healthcare', table_name => 'encounters', table_location => 'file:/warehouse/healthcare/encounters');
CALL iceberg.system.register_table(schema_name => 'healthcare', table_name => 'conditions', table_location => 'file:/warehouse/healthcare/conditions');
CALL iceberg.system.register_table(schema_name => 'healthcare', table_name => 'organizations', table_location => 'file:/warehouse/healthcare/organizations');
CALL iceberg.system.register_table(schema_name => 'healthcare', table_name => 'encounter_analytics', table_location => 'file:/warehouse/healthcare/encounter_analytics');
CALL iceberg.system.register_table(schema_name => 'healthcare', table_name => 'condition_analytics', table_location => 'file:/warehouse/healthcare/condition_analytics');
"

# Step 4: Export Serving Layer Aggregates to MongoDB
Write-Host "`n[Step 4/5] Exporting Analytics Aggregates to MongoDB..." -ForegroundColor Yellow
python spark/04_export_mongodb.py
if ($LASTEXITCODE -ne 0) { throw "MongoDB Export failed with exit code $LASTEXITCODE" }

# Step 5: Verify Trino Visibility
Write-Host "`n[Step 5/5] Running Trino SQL Validation Suite..." -ForegroundColor Yellow
docker exec healthinsight-trino trino --execute "
SHOW TABLES FROM iceberg.healthcare;
SELECT 'encounter_analytics' AS table_name, COUNT(*) AS total_rows FROM iceberg.healthcare.encounter_analytics;
SELECT 'condition_analytics' AS table_name, COUNT(*) AS total_rows FROM iceberg.healthcare.condition_analytics;
"
if ($LASTEXITCODE -ne 0) { throw "Trino Validation failed with exit code $LASTEXITCODE" }

Write-Host "`n================================================================================" -ForegroundColor Green
Write-Host "  HEALTHINSIGHT PIPELINE EXECUTION FINISHED SUCCESSFULLY (Exit Code 0)" -ForegroundColor Green
Write-Host "================================================================================`n" -ForegroundColor Green
