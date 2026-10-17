-- 05_trends.sql — Time-based Encounter Trends
-- Run against: Trino with Iceberg catalog

-- Monthly encounter trend (full history)
SELECT
    YEAR(encounter_start)  AS year,
    MONTH(encounter_start) AS month,
    COUNT(*)               AS encounter_count
FROM iceberg.healthcare.healthcare_analytics
WHERE encounter_start IS NOT NULL
GROUP BY YEAR(encounter_start), MONTH(encounter_start)
ORDER BY year, month;

-- Year-over-year encounter count
SELECT
    YEAR(encounter_start) AS year,
    COUNT(*)              AS encounter_count
FROM iceberg.healthcare.healthcare_analytics
WHERE encounter_start IS NOT NULL
GROUP BY YEAR(encounter_start)
ORDER BY year;

-- Encounter count by day of week (optional)
SELECT
    DAY_OF_WEEK(encounter_start) AS day_of_week,
    COUNT(*)                     AS encounter_count
FROM iceberg.healthcare.healthcare_analytics
WHERE encounter_start IS NOT NULL
GROUP BY DAY_OF_WEEK(encounter_start)
ORDER BY day_of_week;
