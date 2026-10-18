-- 04_encounters.sql — Encounter Analytics
-- Run against: Trino with Iceberg catalog
-- Table: iceberg.healthcare.encounter_analytics (1 row per encounter)

-- 1. Encounter count by class / type
SELECT
    encounter_class,
    COUNT(*) AS encounter_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM iceberg.healthcare.encounter_analytics
WHERE encounter_class IS NOT NULL
GROUP BY encounter_class
ORDER BY encounter_count DESC;

-- 2. Average encounter duration by class (in minutes)
SELECT
    encounter_class,
    ROUND(AVG(duration_minutes), 2) AS avg_duration_minutes,
    COUNT(*) AS encounter_count
FROM iceberg.healthcare.encounter_analytics
WHERE encounter_class IS NOT NULL
  AND duration_minutes IS NOT NULL
GROUP BY encounter_class
ORDER BY avg_duration_minutes DESC;

-- 3. Average and total financial cost by encounter class
SELECT
    encounter_class,
    ROUND(AVG(total_claim_cost), 2)         AS avg_claim_cost,
    ROUND(SUM(total_claim_cost), 2)         AS total_claim_cost,
    ROUND(SUM(payer_coverage), 2)           AS total_payer_coverage,
    ROUND(SUM(patient_out_of_pocket), 2)    AS total_out_of_pocket,
    COUNT(*)                                AS encounter_count
FROM iceberg.healthcare.encounter_analytics
WHERE encounter_class IS NOT NULL
  AND total_claim_cost IS NOT NULL
GROUP BY encounter_class
ORDER BY total_claim_cost DESC;

-- 4. Top 20 organizations by encounter volume and billing
SELECT
    organization_name,
    organization_city,
    organization_state,
    COUNT(*) AS encounter_count,
    ROUND(SUM(total_claim_cost), 2) AS total_billing
FROM iceberg.healthcare.encounter_analytics
WHERE organization_name IS NOT NULL
GROUP BY organization_name, organization_city, organization_state
ORDER BY encounter_count DESC
LIMIT 20;
