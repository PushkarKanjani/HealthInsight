-- 02_conditions.sql — Condition Analytics
-- Run against: Trino with Iceberg catalog
-- Table: iceberg.healthcare.condition_analytics (1 row per condition event)

-- 1. Top 20 conditions by frequency
SELECT
    condition_description,
    COUNT(*) AS frequency
FROM iceberg.healthcare.condition_analytics
WHERE condition_description IS NOT NULL
GROUP BY condition_description
ORDER BY frequency DESC
LIMIT 20;

-- 2. Condition distribution by gender
SELECT
    patient_gender,
    condition_description,
    COUNT(*) AS frequency
FROM iceberg.healthcare.condition_analytics
WHERE condition_description IS NOT NULL
  AND patient_gender IS NOT NULL
GROUP BY patient_gender, condition_description
ORDER BY frequency DESC
LIMIT 40;

-- 3. Condition distribution by age group (event-time age at diagnosis)
SELECT
    age_group,
    condition_description,
    COUNT(*) AS frequency
FROM iceberg.healthcare.condition_analytics
WHERE condition_description IS NOT NULL
  AND age_group IS NOT NULL
GROUP BY age_group, condition_description
ORDER BY age_group, frequency DESC;
