-- 01_kpis.sql — Key Performance Indicators
-- Run against: Trino with Iceberg catalog
-- Table: iceberg.healthcare.encounter_analytics (1 row per encounter)

SELECT
    COUNT(DISTINCT patient_id)              AS total_patients,
    COUNT(encounter_id)                     AS total_encounters,
    ROUND(AVG(duration_minutes), 2)         AS avg_encounter_duration_mins,
    ROUND(AVG(total_claim_cost), 2)         AS avg_claim_cost,
    ROUND(SUM(total_claim_cost), 2)         AS total_synthetic_cost,
    ROUND(SUM(payer_coverage), 2)           AS total_payer_coverage,
    ROUND(SUM(patient_out_of_pocket), 2)    AS total_out_of_pocket
FROM iceberg.healthcare.encounter_analytics;
