-- 02_conditions.sql — Condition Analytics
-- Run against: Trino with Iceberg catalog

-- Top 20 conditions by frequency
SELECT
    condition_description,
    COUNT(*) AS frequency
FROM iceberg.healthcare.healthcare_analytics
WHERE condition_description IS NOT NULL
GROUP BY condition_description
ORDER BY frequency DESC
LIMIT 20;

-- Condition distribution by gender
SELECT
    gender,
    condition_description,
    COUNT(*) AS frequency
FROM iceberg.healthcare.healthcare_analytics
WHERE condition_description IS NOT NULL
  AND gender IS NOT NULL
GROUP BY gender, condition_description
ORDER BY frequency DESC
LIMIT 40;

-- Condition distribution by age group
SELECT
    age_group,
    condition_description,
    COUNT(*) AS frequency
FROM iceberg.healthcare.healthcare_analytics
WHERE condition_description IS NOT NULL
  AND age_group IS NOT NULL
GROUP BY age_group, condition_description
ORDER BY age_group, frequency DESC;
