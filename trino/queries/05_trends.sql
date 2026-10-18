-- 05_trends.sql — Time-based Encounter Trends
-- Run against: Trino with Iceberg catalog
-- Table: iceberg.healthcare.encounter_analytics (1 row per encounter)

-- 1. Monthly encounter trend (full longitudinal history)
SELECT
    YEAR(start_time)  AS year,
    MONTH(start_time) AS month,
    COUNT(*)          AS encounter_count,
    ROUND(SUM(total_claim_cost), 2) AS monthly_claim_cost
FROM iceberg.healthcare.encounter_analytics
WHERE start_time IS NOT NULL
GROUP BY YEAR(start_time), MONTH(start_time)
ORDER BY year, month;

-- 2. Year-over-year encounter count and financial volume
SELECT
    YEAR(start_time)  AS year,
    COUNT(*)          AS encounter_count,
    ROUND(SUM(total_claim_cost), 2) AS yearly_claim_cost,
    ROUND(AVG(total_claim_cost), 2) AS avg_claim_cost
FROM iceberg.healthcare.encounter_analytics
WHERE start_time IS NOT NULL
GROUP BY YEAR(start_time)
ORDER BY year;

-- 3. Encounter distribution by day of week
SELECT
    DAY_OF_WEEK(start_time) AS day_of_week,
    COUNT(*)                AS encounter_count
FROM iceberg.healthcare.encounter_analytics
WHERE start_time IS NOT NULL
GROUP BY DAY_OF_WEEK(start_time)
ORDER BY day_of_week;
