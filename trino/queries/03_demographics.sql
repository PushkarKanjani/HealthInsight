-- 03_demographics.sql — Demographic Distributions
-- Run against: Trino with Iceberg catalog
-- Tables: iceberg.healthcare.patients & iceberg.healthcare.encounter_analytics

-- 1. Patient count by gender (from canonical patients table)
SELECT
    gender,
    COUNT(*) AS patient_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM iceberg.healthcare.patients
WHERE gender IS NOT NULL
GROUP BY gender
ORDER BY patient_count DESC;

-- 2. Encounter distribution by age group (from encounter_analytics)
SELECT
    age_group,
    COUNT(DISTINCT patient_id)  AS distinct_patients,
    COUNT(encounter_id)         AS encounter_count
FROM iceberg.healthcare.encounter_analytics
WHERE age_group IS NOT NULL
GROUP BY age_group
ORDER BY age_group;

-- 3. Patient distribution by race
SELECT
    race,
    COUNT(*) AS patient_count
FROM iceberg.healthcare.patients
WHERE race IS NOT NULL
GROUP BY race
ORDER BY patient_count DESC;

-- 4. Patient distribution by ethnicity
SELECT
    ethnicity,
    COUNT(*) AS patient_count
FROM iceberg.healthcare.patients
WHERE ethnicity IS NOT NULL
GROUP BY ethnicity
ORDER BY patient_count DESC;
