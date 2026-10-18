-- ==============================================================================
-- HealthInsight — Prompt 09 Trino Validation Suite
-- File: trino/queries/00_validation.sql
-- ==============================================================================

-- 1. Verify Catalogs
SHOW CATALOGS;

-- 2. Verify Iceberg Schemas
SHOW SCHEMAS FROM iceberg;

-- 3. Verify All 6 Tables in 'healthcare'
SHOW TABLES FROM iceberg.healthcare;

-- 4. Verify Encounter Analytics Table Count (Exactly 321,528 rows)
SELECT 'encounter_analytics' AS table_name, COUNT(*) AS total_rows
FROM iceberg.healthcare.encounter_analytics;

-- 5. Verify Condition Analytics Table Count (Exactly 114,544 rows)
SELECT 'condition_analytics' AS table_name, COUNT(*) AS total_rows
FROM iceberg.healthcare.condition_analytics;
