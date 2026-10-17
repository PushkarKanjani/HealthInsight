-- 04_encounters.sql — Encounter Analytics
-- Run against: Trino with Iceberg catalog

-- Encounter count by type
SELECT
    encounter_type,
    COUNT(*) AS encounter_count
FROM iceberg.healthcare.healthcare_analytics
WHERE encounter_type IS NOT NULL
GROUP BY encounter_type
ORDER BY encounter_count DESC;

-- Average encounter duration by type
SELECT
    encounter_type,
    ROUND(AVG(encounter_duration_days), 2) AS avg_duration_days,
    COUNT(*) AS encounter_count
FROM iceberg.healthcare.healthcare_analytics
WHERE encounter_type IS NOT NULL
  AND encounter_duration_days IS NOT NULL
GROUP BY encounter_type
ORDER BY avg_duration_days DESC;

-- Average and total cost by encounter type (only if cost columns exist)
SELECT
    encounter_type,
    ROUND(AVG(total_claim_cost), 2) AS avg_claim_cost,
    ROUND(SUM(total_claim_cost), 2) AS total_claim_cost,
    COUNT(*) AS encounter_count
FROM iceberg.healthcare.healthcare_analytics
WHERE encounter_type IS NOT NULL
  AND total_claim_cost IS NOT NULL
GROUP BY encounter_type
ORDER BY total_claim_cost DESC;

-- Top 20 organizations by encounter count
SELECT
    organization_name,
    COUNT(*) AS encounter_count
FROM iceberg.healthcare.healthcare_analytics
WHERE organization_name IS NOT NULL
GROUP BY organization_name
ORDER BY encounter_count DESC
LIMIT 20;
