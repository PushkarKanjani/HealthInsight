# ==============================================================================
# HealthInsight - Full Automated Big Data Pipeline for Windows PowerShell (Prompt 15)
# Engine Order: Spark Profiler -> Iceberg Ingest -> Analytics Marts -> MongoDB -> Trino Validation
# ==============================================================================

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  HealthInsight - Big Data End-to-End Pipeline Execution (PowerShell)" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# Step 0: Ensure Docker services are running
Write-Host ""
Write-Host "[Step 0/5] Verifying Infrastructure Services..." -ForegroundColor Yellow
docker compose up -d trino mongodb
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker compose failed"
    exit 1
}

# Step 1: Profile Source Dataset
Write-Host ""
Write-Host "[Step 1/5] Running Spark Dataset Profiler..." -ForegroundColor Yellow
python spark/01_profile_dataset.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "Dataset Profiler failed with exit code $LASTEXITCODE"
    exit 1
}

# Step 2: Ingest Raw CSVs into Iceberg
Write-Host ""
Write-Host "[Step 2/5] Ingesting Raw CSVs into Apache Iceberg..." -ForegroundColor Yellow
python spark/02_ingest_raw_to_iceberg.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "Raw Ingestion failed with exit code $LASTEXITCODE"
    exit 1
}

# Step 3: Build Curated Analytical Tables
Write-Host ""
Write-Host "[Step 3/5] Constructing Analytical Iceberg Datamarts..." -ForegroundColor Yellow
python spark/03_build_analytics_tables.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "Analytics Table Construction failed with exit code $LASTEXITCODE"
    exit 1
}

# Register tables in Trino
Write-Host ""
Write-Host "Registering tables in Trino..." -ForegroundColor Yellow
docker exec healthinsight-trino trino --execute "CALL iceberg.system.register_table(schema_name => 'healthcare', table_name => 'patients', table_location => 'file:/warehouse/healthcare/patients');" 2>$null
docker exec healthinsight-trino trino --execute "CALL iceberg.system.register_table(schema_name => 'healthcare', table_name => 'encounters', table_location => 'file:/warehouse/healthcare/encounters');" 2>$null
docker exec healthinsight-trino trino --execute "CALL iceberg.system.register_table(schema_name => 'healthcare', table_name => 'conditions', table_location => 'file:/warehouse/healthcare/conditions');" 2>$null
docker exec healthinsight-trino trino --execute "CALL iceberg.system.register_table(schema_name => 'healthcare', table_name => 'organizations', table_location => 'file:/warehouse/healthcare/organizations');" 2>$null
docker exec healthinsight-trino trino --execute "CALL iceberg.system.register_table(schema_name => 'healthcare', table_name => 'encounter_analytics', table_location => 'file:/warehouse/healthcare/encounter_analytics');" 2>$null
docker exec healthinsight-trino trino --execute "CALL iceberg.system.register_table(schema_name => 'healthcare', table_name => 'condition_analytics', table_location => 'file:/warehouse/healthcare/condition_analytics');" 2>$null

# Step 4: Export Serving Layer Aggregates to MongoDB
Write-Host ""
Write-Host "[Step 4/5] Exporting Analytics Aggregates to MongoDB..." -ForegroundColor Yellow
python spark/04_export_mongodb.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "MongoDB Export failed with exit code $LASTEXITCODE"
    exit 1
}

# Step 5: Verify Trino Visibility
Write-Host ""
Write-Host "[Step 5/5] Running Trino SQL Validation Suite..." -ForegroundColor Yellow
docker exec healthinsight-trino trino --execute "SHOW TABLES FROM iceberg.healthcare;"
docker exec healthinsight-trino trino --execute "SELECT count(*) AS total_encounters FROM iceberg.healthcare.encounter_analytics;"
docker exec healthinsight-trino trino --execute "SELECT count(*) AS total_conditions FROM iceberg.healthcare.condition_analytics;"

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "  HEALTHINSIGHT PIPELINE EXECUTION FINISHED SUCCESSFULLY (Exit Code 0)" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""
