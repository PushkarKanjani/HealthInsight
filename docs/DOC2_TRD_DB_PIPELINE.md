# HealthInsight — Document 2 of 3
## Technical Reference Document · Database Schemas · Pipeline Implementation

> **Covers:** Spark scripts spec, corrected Iceberg schemas (two analytical tables), Trino SQL, MongoDB collections, service configs, age-at-event calculation, troubleshooting.

---

## 1. Spark Scripts Specification

### 1.1 `spark/01_profile_dataset.py` — Dataset Profiler

**Purpose:** Inspect every Synthea CSV and produce the data dictionary. No transformation. No assumptions.

**Required output per file:**
- File name and full path
- Column headers (exact names from file)
- Inferred data types (Spark schema inference)
- Row count
- Null count per column
- 5 sample rows (untruncated)

**Output:** Console AND `docs/dataset_dictionary.py`.

**Hard rule:** Do not proceed to Phase 2 scripts until this has run and all column names are confirmed.

**Key code pattern:**
```python
for fname in FILES:
    df = spark.read.option("header", True).option("inferSchema", True).csv(path)
    df.printSchema()
    print("Row count:", df.count())
    df.select([count(when(col(c).isNull(), c)).alias(c) for c in df.columns]).show()
    df.show(5, truncate=False)
```

---

### 1.2 `spark/02_ingest_raw_to_iceberg.py` — Raw Ingestion

**Purpose:** Normalize source column names to lowercase and write raw Iceberg tables. No transformation logic.

**Tables created:**
- `healthcare.patients`
- `healthcare.encounters`
- `healthcare.conditions`
- `healthcare.organizations`

**Column normalization:**
```python
# Normalize column names: strip whitespace, lowercase, replace spaces with underscore
df = df.toDF(*[c.strip().lower().replace(" ", "_") for c in df.columns])
```

**Table write pattern:**
```python
df.writeTo("healthcare.patients").using("iceberg").createOrReplace()
```

**Verification:**
```python
spark.sql("SHOW TABLES IN healthcare").show()
spark.sql("SELECT COUNT(*) FROM healthcare.patients").show()
```

**Stop condition:** If any table write fails, print the full error and halt.

---

### 1.3 `spark/03_build_analytics_tables.py` — Analytical Table Builder

**Purpose:** Build two separate analytical tables with no schema overlap in counting or costing.

#### Why two tables

One encounter may have multiple conditions. Joining conditions directly onto the encounter table creates multiple rows per encounter, inflating encounter counts and costs. Two tables prevent this.

#### Path A — `healthcare.encounter_analytics` (one row per encounter)

**Joins:** `encounters` + `patients` + `organizations`

**Age calculation (correct — relative to event date):**
```python
from pyspark.sql.functions import floor, months_between, to_date

encounter_analytics = encounters.join(patients, "patient_id", "left") \
    .join(orgs, "organization_id", "left") \
    .withColumn(
        "age_at_encounter",
        floor(
            months_between(
                to_date(col("encounter_start")),
                to_date(col("birth_date"))
            ) / 12
        ).cast("int")
    ) \
    .withColumn(
        "age_group",
        when(col("age_at_encounter") < 18, "0-17")
        .when(col("age_at_encounter") < 35, "18-34")
        .when(col("age_at_encounter") < 50, "35-49")
        .when(col("age_at_encounter") < 65, "50-64")
        .otherwise("65+")
    ) \
    .withColumn(
        "encounter_duration_days",
        (col("encounter_stop").cast("long") - col("encounter_start").cast("long")) / 86400.0
    )
```

> Do NOT use `current_date()` — it makes historical age values change every day.

**Write:**
```python
encounter_analytics.writeTo("healthcare.encounter_analytics") \
    .using("iceberg").createOrReplace()
```

**Verify one row per encounter:**
```python
total = spark.sql("SELECT COUNT(*) FROM healthcare.encounter_analytics").collect()[0][0]
distinct = spark.sql("SELECT COUNT(DISTINCT encounter_id) FROM healthcare.encounter_analytics").collect()[0][0]
assert total == distinct, f"FAIL: {total} rows != {distinct} distinct encounters"
print(f"PASS: encounter_analytics has {total} rows, all unique encounters.")
```

#### Path B — `healthcare.condition_analytics` (one row per encounter-condition pair)

**Joins:** `conditions` + `patients` + `encounters` (for demographic context only — no costs)

**Age calculation (relative to condition_start):**
```python
condition_analytics = conditions.join(patients, "patient_id", "left") \
    .join(encounters.select("encounter_id", "encounter_type", "organization_id"), "encounter_id", "left") \
    .join(orgs.select("organization_id", "organization_name"), "organization_id", "left") \
    .withColumn(
        "age_at_condition",
        floor(
            months_between(
                to_date(col("condition_start")),
                to_date(col("birth_date"))
            ) / 12
        ).cast("int")
    ) \
    .withColumn(
        "age_group",
        when(col("age_at_condition") < 18, "0-17")
        .when(col("age_at_condition") < 35, "18-34")
        .when(col("age_at_condition") < 50, "35-49")
        .when(col("age_at_condition") < 65, "50-64")
        .otherwise("65+")
    )
```

**Write:**
```python
condition_analytics.writeTo("healthcare.condition_analytics") \
    .using("iceberg").createOrReplace()
```

---

### 1.4 `spark/04_export_mongodb.py` — MongoDB Exporter

**Source mapping — critical:**

| MongoDB Collection | Source Table | Reason |
|---|---|---|
| `kpis` | `encounter_analytics` | Encounter counts and costs must come from encounter-level table |
| `encounter_type_summary` | `encounter_analytics` | Encounter-level grouping |
| `encounter_trends` | `encounter_analytics` | Encounter-level time series |
| `organization_summary` | `encounter_analytics` | Encounter-level org grouping |
| `condition_summary` | `condition_analytics` | Condition-level grouping |
| `demographic_summary` | `condition_analytics` or distinct patient table | Demographic distribution |

**KPI aggregate (from encounter_analytics only):**
```python
enc = spark.table("healthcare.encounter_analytics")
kpis = enc.agg(
    countDistinct("patient_id").alias("total_patients"),
    count("encounter_id").alias("total_encounters"),
    round(avg("encounter_duration_days"), 2).alias("avg_duration_days"),
    round(avg("total_claim_cost"), 2).alias("avg_claim_cost"),
    round(sum("total_claim_cost"), 2).alias("total_cost")
).withColumn("generated_at", lit(NOW)) \
 .withColumn("source_table", lit("healthcare.encounter_analytics"))
```

**Condition summary (from condition_analytics):**
```python
cond = spark.table("healthcare.condition_analytics")
condition_df = cond \
    .filter(col("condition_description").isNotNull()) \
    .groupBy("condition_description") \
    .agg(count("*").alias("frequency")) \
    .withColumn("generated_at", lit(NOW)) \
    .withColumn("source_table", lit("healthcare.condition_analytics"))
```

**Write pattern:**
```python
df.write.format("mongodb").mode("overwrite") \
    .option("database", MONGODB_DATABASE) \
    .option("collection", "collection_name").save()
```

**Required collections (create only if data supports them):**
- `kpis` — required
- `condition_summary` — required
- `encounter_type_summary` — required
- `encounter_trends` — required

**Optional collections (create only if source columns exist):**
- `demographic_summary`
- `organization_summary`

> Do not create empty or fake collections just to reach a target count.

---

## 2. Iceberg Table Schemas

> **Templates only.** Finalize column list after running `01_profile_dataset.py`.
> Remove any column that does not exist in real source files.
> All column names normalized to lowercase.

### 2.1 `healthcare.patients` (raw)

| Column | Type | Source Column |
|---|---|---|
| patient_id | STRING | id |
| gender | STRING | gender |
| birth_date | DATE | birthdate |
| race | STRING | race |
| ethnicity | STRING | ethnicity |
| city | STRING | city |
| state | STRING | state |

### 2.2 `healthcare.encounters` (raw)

| Column | Type | Source Column |
|---|---|---|
| encounter_id | STRING | id |
| patient_id | STRING | patient |
| organization_id | STRING | organization |
| encounter_type | STRING | encounterclass |
| encounter_start | TIMESTAMP | start |
| encounter_stop | TIMESTAMP | stop |
| base_cost | DOUBLE | base_encounter_cost |
| total_claim_cost | DOUBLE | total_claim_cost |

> Remove cost columns if they do not exist in the real file.

### 2.3 `healthcare.conditions` (raw)

| Column | Type | Source Column |
|---|---|---|
| patient_id | STRING | patient |
| encounter_id | STRING | encounter |
| condition_code | STRING | code |
| condition_description | STRING | description |
| condition_start | DATE | start |
| condition_stop | DATE | stop |

### 2.4 `healthcare.organizations` (raw)

| Column | Type | Source Column |
|---|---|---|
| organization_id | STRING | id |
| organization_name | STRING | name |
| city | STRING | city |
| state | STRING | state |

### 2.5 `healthcare.encounter_analytics` (analytical — 1 row per encounter)

| Column | Type | Derived From |
|---|---|---|
| encounter_id | STRING | encounters |
| patient_id | STRING | encounters |
| organization_id | STRING | encounters |
| organization_name | STRING | organizations |
| gender | STRING | patients |
| birth_date | DATE | patients |
| age_at_encounter | INT | derived: months_between(encounter_start, birth_date)/12 |
| age_group | STRING | derived: bucketed from age_at_encounter |
| race | STRING | patients |
| ethnicity | STRING | patients |
| encounter_type | STRING | encounters |
| encounter_start | TIMESTAMP | encounters |
| encounter_stop | TIMESTAMP | encounters |
| encounter_duration_days | DOUBLE | derived: (stop - start) in seconds / 86400 |
| base_cost | DOUBLE | encounters (if exists) |
| total_claim_cost | DOUBLE | encounters (if exists) |

> **One row per encounter. No condition columns. No cost inflation.**

### 2.6 `healthcare.condition_analytics` (analytical — 1 row per encounter-condition)

| Column | Type | Derived From |
|---|---|---|
| patient_id | STRING | conditions |
| encounter_id | STRING | conditions |
| condition_code | STRING | conditions |
| condition_description | STRING | conditions |
| condition_start | DATE | conditions |
| condition_stop | DATE | conditions |
| gender | STRING | patients |
| birth_date | DATE | patients |
| age_at_condition | INT | derived: months_between(condition_start, birth_date)/12 |
| age_group | STRING | derived: bucketed from age_at_condition |
| race | STRING | patients |
| ethnicity | STRING | patients |
| encounter_type | STRING | encounters |
| organization_id | STRING | encounters |
| organization_name | STRING | organizations |

> **No cost columns. No encounter-count aggregation should use this table.**

---

## 3. Trino SQL Queries

### 3.1 `trino/queries/01_kpis.sql`

```sql
-- KPIs from encounter_analytics only
-- Never calculate encounter counts or costs from condition_analytics
SELECT
    COUNT(DISTINCT patient_id)              AS total_patients,
    COUNT(encounter_id)                     AS total_encounters,
    ROUND(AVG(encounter_duration_days), 2)  AS avg_encounter_duration_days,
    ROUND(AVG(total_claim_cost), 2)         AS avg_claim_cost,
    ROUND(SUM(total_claim_cost), 2)         AS total_synthetic_cost
FROM iceberg.healthcare.encounter_analytics;
```

### 3.2 `trino/queries/02_conditions.sql`

```sql
-- Condition frequency (top 20) — from condition_analytics
SELECT
    condition_description,
    COUNT(*) AS frequency
FROM iceberg.healthcare.condition_analytics
WHERE condition_description IS NOT NULL
GROUP BY condition_description
ORDER BY frequency DESC
LIMIT 20;

-- Condition by gender
SELECT
    gender,
    condition_description,
    COUNT(*) AS frequency
FROM iceberg.healthcare.condition_analytics
WHERE condition_description IS NOT NULL AND gender IS NOT NULL
GROUP BY gender, condition_description
ORDER BY frequency DESC
LIMIT 40;

-- Condition by age group
SELECT
    age_group,
    condition_description,
    COUNT(*) AS frequency
FROM iceberg.healthcare.condition_analytics
WHERE condition_description IS NOT NULL AND age_group IS NOT NULL
GROUP BY age_group, condition_description
ORDER BY age_group, frequency DESC;
```

### 3.3 `trino/queries/03_demographics.sql`

```sql
-- Gender distribution (distinct patients)
SELECT gender, COUNT(DISTINCT patient_id) AS patient_count
FROM iceberg.healthcare.encounter_analytics
WHERE gender IS NOT NULL
GROUP BY gender;

-- Age group distribution
SELECT age_group, COUNT(DISTINCT patient_id) AS patient_count
FROM iceberg.healthcare.encounter_analytics
WHERE age_group IS NOT NULL
GROUP BY age_group ORDER BY age_group;

-- Race distribution
SELECT race, COUNT(DISTINCT patient_id) AS patient_count
FROM iceberg.healthcare.encounter_analytics
WHERE race IS NOT NULL
GROUP BY race ORDER BY patient_count DESC;

-- Ethnicity distribution
SELECT ethnicity, COUNT(DISTINCT patient_id) AS patient_count
FROM iceberg.healthcare.encounter_analytics
WHERE ethnicity IS NOT NULL
GROUP BY ethnicity ORDER BY patient_count DESC;
```

### 3.4 `trino/queries/04_encounters.sql`

```sql
-- Encounter count by type — from encounter_analytics
SELECT
    encounter_type,
    COUNT(*) AS encounter_count
FROM iceberg.healthcare.encounter_analytics
WHERE encounter_type IS NOT NULL
GROUP BY encounter_type ORDER BY encounter_count DESC;

-- Average duration by encounter type
SELECT
    encounter_type,
    ROUND(AVG(encounter_duration_days), 2) AS avg_duration_days,
    COUNT(*) AS encounter_count
FROM iceberg.healthcare.encounter_analytics
WHERE encounter_type IS NOT NULL AND encounter_duration_days IS NOT NULL
GROUP BY encounter_type ORDER BY avg_duration_days DESC;

-- Average and total cost by type (if cost columns exist)
SELECT
    encounter_type,
    ROUND(AVG(total_claim_cost), 2) AS avg_claim_cost,
    ROUND(SUM(total_claim_cost), 2) AS total_claim_cost,
    COUNT(*) AS encounter_count
FROM iceberg.healthcare.encounter_analytics
WHERE encounter_type IS NOT NULL AND total_claim_cost IS NOT NULL
GROUP BY encounter_type ORDER BY total_claim_cost DESC;

-- Top 20 organizations by encounter count
SELECT
    organization_name,
    COUNT(*) AS encounter_count
FROM iceberg.healthcare.encounter_analytics
WHERE organization_name IS NOT NULL
GROUP BY organization_name ORDER BY encounter_count DESC LIMIT 20;
```

### 3.5 `trino/queries/05_trends.sql`

```sql
-- Monthly encounter trend
SELECT
    YEAR(encounter_start)  AS year,
    MONTH(encounter_start) AS month,
    COUNT(*)               AS encounter_count
FROM iceberg.healthcare.encounter_analytics
WHERE encounter_start IS NOT NULL
GROUP BY YEAR(encounter_start), MONTH(encounter_start)
ORDER BY year, month;

-- Year-over-year encounter count
SELECT
    YEAR(encounter_start) AS year,
    COUNT(*)              AS encounter_count
FROM iceberg.healthcare.encounter_analytics
WHERE encounter_start IS NOT NULL
GROUP BY YEAR(encounter_start)
ORDER BY year;
```

---

## 4. MongoDB Collection Schemas

### Required Collections

#### `healthinsight.kpis`
```json
{
  "total_patients": 1000,
  "total_encounters": 15234,
  "avg_duration_days": 0.5,
  "avg_claim_cost": 432.12,
  "total_cost": 6581234.50,
  "generated_at": "2026-10-18T02:00:00",
  "source_table": "healthcare.encounter_analytics"
}
```

#### `healthinsight.condition_summary`
```json
{
  "condition_description": "Hypertension",
  "frequency": 421,
  "generated_at": "2026-10-18T02:00:00",
  "source_table": "healthcare.condition_analytics"
}
```

#### `healthinsight.encounter_type_summary`
```json
{
  "encounter_type": "outpatient",
  "encounter_count": 5432,
  "avg_duration_days": 0.3,
  "avg_claim_cost": 385.20,
  "generated_at": "2026-10-18T02:00:00",
  "source_table": "healthcare.encounter_analytics"
}
```

#### `healthinsight.encounter_trends`
```json
{
  "year": 2020,
  "month": 3,
  "encounter_count": 432,
  "generated_at": "2026-10-18T02:00:00",
  "source_table": "healthcare.encounter_analytics"
}
```

### Optional Collections (only if source columns exist)

#### `healthinsight.demographic_summary`
```json
{
  "gender": "F",
  "age_group": "50-64",
  "race": "white",
  "ethnicity": "nonhispanic",
  "encounter_count": 3421,
  "generated_at": "2026-10-18T02:00:00"
}
```

#### `healthinsight.organization_summary`
```json
{
  "organization_id": "uuid-here",
  "organization_name": "General Hospital",
  "total_encounters": 1200,
  "avg_cost": 512.34,
  "generated_at": "2026-10-18T02:00:00",
  "source_table": "healthcare.encounter_analytics"
}
```

### MongoDB Indexes (`mongodb/indexes.js`)

```javascript
use healthinsight;
db.condition_summary.createIndex({ condition_description: 1 });
db.condition_summary.createIndex({ frequency: -1 });
db.demographic_summary.createIndex({ gender: 1, age_group: 1 });
db.encounter_type_summary.createIndex({ encounter_type: 1 });
db.encounter_trends.createIndex({ year: 1, month: 1 });
db.organization_summary.createIndex({ organization_name: 1 });
db.organization_summary.createIndex({ total_encounters: -1 });
```

---

## 5. Service Configuration

### 5.1 `scripts/check_versions.sh`

```bash
#!/bin/bash
echo "=== HealthInsight Version Check ==="
java -version 2>&1
python3 --version
python3 -c "import pyspark; print('PySpark:', pyspark.__version__)"
python3 -c "import pymongo; print('PyMongo:', pymongo.__version__)"
echo "Trino:" && curl -s http://localhost:8080/v1/info | python3 -m json.tool
echo "MongoDB:" && mongosh --quiet --eval "db.adminCommand({serverStatus:1}).version"
```

### 5.2 `scripts/run_pipeline.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
source .env

echo "[1/4] Profiling dataset"
"$SPARK_HOME/bin/spark-submit" \
  --jars "$ICEBERG_JAR,$MONGO_JAR" \
  spark/01_profile_dataset.py

echo "[2/4] Ingesting raw data to Iceberg"
"$SPARK_HOME/bin/spark-submit" \
  --jars "$ICEBERG_JAR,$MONGO_JAR" \
  spark/02_ingest_raw_to_iceberg.py

echo "[3/4] Building analytical tables"
"$SPARK_HOME/bin/spark-submit" \
  --jars "$ICEBERG_JAR,$MONGO_JAR" \
  spark/03_build_analytics_tables.py

echo "[4/4] Exporting MongoDB aggregates"
"$SPARK_HOME/bin/spark-submit" \
  --jars "$ICEBERG_JAR,$MONGO_JAR" \
  spark/04_export_mongodb.py

echo "HealthInsight pipeline completed successfully."
```

### 5.3 Trino Verification Commands

```sql
SHOW CATALOGS;
SHOW SCHEMAS FROM iceberg;
SHOW TABLES FROM iceberg.healthcare;
SELECT COUNT(*) FROM iceberg.healthcare.encounter_analytics;
SELECT COUNT(DISTINCT encounter_id) FROM iceberg.healthcare.encounter_analytics;
-- These two counts must be equal
```

---

## 6. Troubleshooting

| Error | Likely Cause | Resolution |
|---|---|---|
| `ClassNotFoundException: IcebergSparkCatalog` | Iceberg JAR not on classpath | Pass via `--jars "$ICEBERG_JAR"` |
| `Cannot resolve catalog 'healthcare'` in Trino | Wrong property name or wrong warehouse path | Check Trino version docs, verify paths match |
| `MongoSocketOpenException` | MongoDB not running | `mongod --dbpath /path/to/data` |
| `encounter count != distinct encounter_id count` | Many-to-many join leak into encounter_analytics | Check that conditions are NOT joined into encounter_analytics |
| `java.lang.UnsupportedClassVersionError` | Java version mismatch | Use Java 17 for both Spark and Trino |
| Superset cannot connect to Trino | `trino` package not in Superset env | `pip install trino` in Superset venv only |
| Iceberg JAR version mismatch | JAR Scala version != Spark Scala version | Use `_2.12` suffix for Spark 3.5.x |

### Stop Conditions

Stop and report when:
- Any Spark script exits non-zero.
- An Iceberg table cannot be written or queried.
- Trino cannot connect to the Iceberg catalog.
- MongoDB is not accessible.
- A script references a column that does not exist in the real CSV.
- `encounter_analytics` row count != distinct encounter_id count.

---

## 7. Version Lock Record (`docs/version_lock.md`)

> Fill in after actual installation. Do not guess.

| Component | Installed Version | JAR/Package |
|---|---|---|
| Java | | |
| Python | | |
| Scala binary | | |
| Apache Spark | | |
| Iceberg Runtime JAR | | `iceberg-spark-runtime-3.5_2.12-?.jar` |
| Trino | | |
| MongoDB | | |
| MongoDB Spark Connector | | `mongo-spark-connector_2.12-?.jar` |
| PySpark | | |
| PyMongo | | |
| trino-python-client | | |
| Apache Superset | | |
