-- 01_kpis.sql — Key Performance Indicators
-- Run against: Trino with Iceberg catalog
-- Table: iceberg.healthcare.healthcare_analytics

SELECT
    COUNT(DISTINCT patient_id)              AS total_patients,
    COUNT(encounter_id)                     AS total_encounters,
    ROUND(AVG(encounter_duration_days), 2)  AS avg_encounter_duration_days,
    ROUND(AVG(total_claim_cost), 2)         AS avg_claim_cost,
    ROUND(SUM(total_claim_cost), 2)         AS total_synthetic_cost
FROM iceberg.healthcare.healthcare_analytics;
