-- superset/dataset_queries.sql
-- Virtual dataset SQL queries for Apache Superset
-- Use these in the "Create Dataset → From SQL" interface in Superset.
-- Primary connection: HealthInsight Trino (trino://localhost:8080/iceberg)

-- ============================================================
-- DATASET: kpi_overview
-- ============================================================
SELECT
    COUNT(DISTINCT patient_id)              AS total_patients,
    COUNT(encounter_id)                     AS total_encounters,
    ROUND(AVG(encounter_duration_days), 2)  AS avg_encounter_duration_days,
    ROUND(AVG(total_claim_cost), 2)         AS avg_claim_cost,
    ROUND(SUM(total_claim_cost), 2)         AS total_synthetic_cost
FROM iceberg.healthcare.healthcare_analytics;

-- ============================================================
-- DATASET: condition_frequency
-- ============================================================
SELECT
    condition_description,
    COUNT(*) AS frequency
FROM iceberg.healthcare.healthcare_analytics
WHERE condition_description IS NOT NULL
GROUP BY condition_description
ORDER BY frequency DESC
LIMIT 20;

-- ============================================================
-- DATASET: demographic_distribution
-- ============================================================
SELECT
    gender,
    age_group,
    race,
    COUNT(DISTINCT patient_id) AS patient_count
FROM iceberg.healthcare.healthcare_analytics
WHERE gender IS NOT NULL
GROUP BY gender, age_group, race;

-- ============================================================
-- DATASET: encounter_analytics
-- ============================================================
SELECT
    encounter_type,
    COUNT(*) AS encounter_count,
    ROUND(AVG(encounter_duration_days), 2) AS avg_duration_days,
    ROUND(AVG(total_claim_cost), 2) AS avg_claim_cost
FROM iceberg.healthcare.healthcare_analytics
WHERE encounter_type IS NOT NULL
GROUP BY encounter_type
ORDER BY encounter_count DESC;

-- ============================================================
-- DATASET: monthly_trends
-- ============================================================
SELECT
    YEAR(encounter_start)  AS year,
    MONTH(encounter_start) AS month,
    COUNT(*)               AS encounter_count
FROM iceberg.healthcare.healthcare_analytics
WHERE encounter_start IS NOT NULL
GROUP BY YEAR(encounter_start), MONTH(encounter_start)
ORDER BY year, month;

-- ============================================================
-- DATASET: organization_summary
-- ============================================================
SELECT
    organization_name,
    COUNT(encounter_id)                    AS total_encounters,
    ROUND(AVG(total_claim_cost), 2)        AS avg_cost
FROM iceberg.healthcare.healthcare_analytics
WHERE organization_name IS NOT NULL
GROUP BY organization_name
ORDER BY total_encounters DESC
LIMIT 20;
