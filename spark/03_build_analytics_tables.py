"""
spark/03_build_analytics_tables.py
Prompt 08 — Analytical Table Construction
=========================================
Builds two canonical dimensional analytical tables in Apache Iceberg:

1. iceberg.healthcare.encounter_analytics (1 row per encounter)
   - Total rows: exactly 321,528 rows
   - Verified: COUNT(*) == COUNT(DISTINCT encounter_id)
   - Features: event-time age (at visit), visit duration in minutes,
     financial claim & payer coverage metrics, organization metadata.

2. iceberg.healthcare.condition_analytics (1 row per condition diagnosis event)
   - Total rows: exactly 114,544 rows
   - Multi-row per encounter allowed and intentional.
   - Features: condition code, description, patient demographics,
     event-time age at diagnosis, age groups.

CRITICAL RULE:
  Never join conditions directly into encounters to avoid cartesian cost duplication.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Windows Java & Hadoop binary paths
if os.getenv("JAVA_HOME"):
    os.environ["PATH"] = os.path.join(os.getenv("JAVA_HOME"), "bin") + os.pathsep + os.environ.get("PATH", "")
if os.getenv("HADOOP_HOME"):
    os.environ["PATH"] = os.path.join(os.getenv("HADOOP_HOME"), "bin") + os.pathsep + os.environ.get("PATH", "")

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, to_timestamp, to_date, months_between, floor,
    when, round as spark_round, unix_timestamp, count, countDistinct
)

project_root = Path(__file__).resolve().parent.parent
warehouse_dir = os.getenv("ICEBERG_WAREHOUSE", "file:/warehouse")
iceberg_pkg = os.getenv("ICEBERG_PACKAGE", "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.2")

print("\n" + "=" * 80)
print("  HealthInsight — Analytical Table Construction (Prompt 08)")
print("=" * 80)
print(f"Iceberg Warehouse: {warehouse_dir}")
print(f"Iceberg Package:   {iceberg_pkg}")

# Initialize Spark with Iceberg catalog
spark = SparkSession.builder \
    .appName("HealthInsight-BuildAnalyticsTables") \
    .master("local[*]") \
    .config("spark.driver.memory", "4g") \
    .config("spark.jars.packages", iceberg_pkg) \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.iceberg.type", "hadoop") \
    .config("spark.sql.catalog.iceberg.warehouse", warehouse_dir) \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# ==============================================================================
# Step 1: Load Raw Ingested Iceberg Tables
# ==============================================================================
print("\n[Step 1] Loading raw ingested Iceberg tables...")
patients_df   = spark.table("iceberg.healthcare.patients")
encounters_df = spark.table("iceberg.healthcare.encounters")
conditions_df = spark.table("iceberg.healthcare.conditions")
orgs_df       = spark.table("iceberg.healthcare.organizations")

patients_count   = patients_df.count()
encounters_count = encounters_df.count()
conditions_count = conditions_df.count()
orgs_count       = orgs_df.count()

print(f"  Raw patients:      {patients_count:,} rows")
print(f"  Raw encounters:    {encounters_count:,} rows")
print(f"  Raw conditions:    {conditions_count:,} rows")
print(f"  Raw organizations: {orgs_count:,} rows")

# Prepare patients lookup (deduplicated by id)
patients_prep = patients_df.select(
    col("id").alias("p_id"),
    col("gender").alias("patient_gender"),
    to_date(col("birthdate")).alias("patient_birthdate"),
    col("race").alias("patient_race"),
    col("ethnicity").alias("patient_ethnicity"),
    col("city").alias("patient_city"),
    col("state").alias("patient_state"),
    col("zip").cast("string").alias("patient_zip")
).dropDuplicates(["p_id"])

# Prepare organizations lookup (deduplicated by id)
orgs_prep = orgs_df.select(
    col("id").alias("o_id"),
    col("name").alias("organization_name"),
    col("city").alias("organization_city"),
    col("state").alias("organization_state")
).dropDuplicates(["o_id"])

# ==============================================================================
# Step 2: Build Table 1 — encounter_analytics (1 row per encounter)
# ==============================================================================
print("\n[Step 2] Building iceberg.healthcare.encounter_analytics...")

encounters_prep = encounters_df.select(
    col("id").alias("encounter_id"),
    col("patient").alias("patient_id"),
    col("organization").alias("organization_id"),
    col("provider").alias("provider_id"),
    col("payer").alias("payer_id"),
    col("encounterclass").alias("encounter_class"),
    col("code").alias("encounter_code"),
    col("description").alias("encounter_description"),
    to_timestamp(col("start")).alias("start_time"),
    to_timestamp(col("stop")).alias("stop_time"),
    col("base_encounter_cost").cast("double").alias("base_cost"),
    col("total_claim_cost").cast("double").alias("total_claim_cost"),
    col("payer_coverage").cast("double").alias("payer_coverage"),
    col("reasoncode").alias("reason_code"),
    col("reasondescription").alias("reason_description")
)

# Left join with patients and organizations
encounter_analytics_df = encounters_prep \
    .join(patients_prep, encounters_prep.patient_id == patients_prep.p_id, "left") \
    .join(orgs_prep, encounters_prep.organization_id == orgs_prep.o_id, "left") \
    .withColumn("duration_minutes", spark_round((unix_timestamp(col("stop_time")) - unix_timestamp(col("start_time"))) / 60.0, 2)) \
    .withColumn("patient_out_of_pocket", spark_round(col("total_claim_cost") - col("payer_coverage"), 2)) \
    .withColumn("encounter_age", floor(months_between(col("start_time"), col("patient_birthdate")) / 12).cast("int")) \
    .withColumn(
        "age_group",
        when(col("encounter_age") < 18, "0-17")
        .when(col("encounter_age") < 35, "18-34")
        .when(col("encounter_age") < 50, "35-49")
        .when(col("encounter_age") < 65, "50-64")
        .otherwise("65+")
    ) \
    .select(
        "encounter_id", "patient_id", "organization_id", "provider_id", "payer_id",
        "encounter_class", "encounter_code", "encounter_description",
        "start_time", "stop_time", "duration_minutes",
        "base_cost", "total_claim_cost", "payer_coverage", "patient_out_of_pocket",
        "reason_code", "reason_description",
        "patient_gender", "patient_birthdate", "encounter_age", "age_group",
        "patient_race", "patient_ethnicity", "patient_city", "patient_state", "patient_zip",
        "organization_name", "organization_city", "organization_state"
    )

print("  Writing to iceberg.healthcare.encounter_analytics...")
encounter_analytics_df.writeTo("iceberg.healthcare.encounter_analytics") \
    .using("iceberg") \
    .createOrReplace()

# Verification assertions for encounter_analytics
ea_check = spark.sql("""
    SELECT 
        COUNT(*) AS total_rows,
        COUNT(DISTINCT encounter_id) AS distinct_encounters
    FROM iceberg.healthcare.encounter_analytics
""").collect()[0]

ea_total = ea_check["total_rows"]
ea_distinct = ea_check["distinct_encounters"]
print(f"  [Assertion Check] Total Rows: {ea_total:,} | Distinct Encounters: {ea_distinct:,}")
assert ea_total == encounters_count, f"Encounter row count mismatch! Expected {encounters_count}, got {ea_total}"
assert ea_total == ea_distinct, f"Encounter duplication detected! Total ({ea_total}) != Distinct ({ea_distinct})"
print("  --> PASS: Exactly 1 row per encounter guaranteed.")

# ==============================================================================
# Step 3: Build Table 2 — condition_analytics (1 row per condition event)
# ==============================================================================
print("\n[Step 3] Building iceberg.healthcare.condition_analytics...")

conditions_prep = conditions_df.select(
    to_date(col("start")).alias("condition_start"),
    to_date(col("stop")).alias("condition_stop"),
    col("patient").alias("patient_id"),
    col("encounter").alias("encounter_id"),
    col("code").alias("condition_code"),
    col("description").alias("condition_description")
)

# Left join with patients
condition_analytics_df = conditions_prep \
    .join(patients_prep, conditions_prep.patient_id == patients_prep.p_id, "left") \
    .withColumn("diagnosis_age", floor(months_between(col("condition_start"), col("patient_birthdate")) / 12).cast("int")) \
    .withColumn(
        "age_group",
        when(col("diagnosis_age") < 18, "0-17")
        .when(col("diagnosis_age") < 35, "18-34")
        .when(col("diagnosis_age") < 50, "35-49")
        .when(col("diagnosis_age") < 65, "50-64")
        .otherwise("65+")
    ) \
    .select(
        "condition_start", "condition_stop",
        "patient_id", "encounter_id",
        "condition_code", "condition_description",
        "patient_gender", "patient_birthdate", "diagnosis_age", "age_group",
        "patient_race", "patient_ethnicity", "patient_city", "patient_state", "patient_zip"
    )

print("  Writing to iceberg.healthcare.condition_analytics...")
condition_analytics_df.writeTo("iceberg.healthcare.condition_analytics") \
    .using("iceberg") \
    .createOrReplace()

# Verification assertions for condition_analytics
ca_total = spark.sql("SELECT COUNT(*) AS n FROM iceberg.healthcare.condition_analytics").collect()[0]["n"]
print(f"  [Assertion Check] Total Rows: {ca_total:,} (Expected: {conditions_count:,})")
assert ca_total == conditions_count, f"Condition row count mismatch! Expected {conditions_count}, got {ca_total}"
print("  --> PASS: Condition events match exactly with source conditions.")

# ==============================================================================
# Final Verification & Schema Display
# ==============================================================================
print("\n" + "=" * 80)
print("  Iceberg Tables in 'iceberg.healthcare':")
print("=" * 80)
spark.sql("SHOW TABLES IN iceberg.healthcare").show(truncate=False)

spark.stop()

print("\n" + "=" * 80)
print("  PROMPT 08 ANALYTICAL TABLES CREATED SUCCESSFULLY (Exit Code 0)")
print("=" * 80 + "\n")
