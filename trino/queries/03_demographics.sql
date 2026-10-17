-- 03_demographics.sql — Demographic Distributions
-- Run against: Trino with Iceberg catalog

-- Gender distribution
SELECT
    gender,
    COUNT(DISTINCT patient_id) AS patient_count
FROM iceberg.healthcare.healthcare_analytics
WHERE gender IS NOT NULL
GROUP BY gender
ORDER BY patient_count DESC;

-- Age group distribution
SELECT
    age_group,
    COUNT(DISTINCT patient_id) AS patient_count
FROM iceberg.healthcare.healthcare_analytics
WHERE age_group IS NOT NULL
GROUP BY age_group
ORDER BY age_group;

-- Race distribution
SELECT
    race,
    COUNT(DISTINCT patient_id) AS patient_count
FROM iceberg.healthcare.healthcare_analytics
WHERE race IS NOT NULL
GROUP BY race
ORDER BY patient_count DESC;

-- Ethnicity distribution
SELECT
    ethnicity,
    COUNT(DISTINCT patient_id) AS patient_count
FROM iceberg.healthcare.healthcare_analytics
WHERE ethnicity IS NOT NULL
GROUP BY ethnicity
ORDER BY patient_count DESC;
