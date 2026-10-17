"""
spark/03_transform_healthcare_data.py
Phase 3 — Data Transformation
================================
Reads raw Iceberg tables, cleans and joins them, derives analytical
columns, and writes the canonical healthcare_analytics Iceberg table.

PREREQUISITE: Run 02_create_iceberg_tables.py first.
UPDATE: Adjust column names based on 01_profile_dataset.py output.
        Remove any column reference that does not exist in real CSV files.
"""

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, to_timestamp, to_date, datediff, current_date,
    floor, when, lit, trim, lower
)
from dotenv import load_dotenv

load_dotenv()

ICEBERG_WAREHOUSE = os.getenv("ICEBERG_WAREHOUSE", "iceberg/warehouse")
ICEBERG_JAR       = os.getenv("ICEBERG_JAR", "")
MONGO_JAR         = os.getenv("MONGO_JAR", "")

JARS = ",".join(filter(None, [ICEBERG_JAR, MONGO_JAR]))

spark = SparkSession.builder \
    .appName("HealthInsight-Transform") \
    .master("local[*]") \
    .config("spark.jars", JARS) \
    .config("spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.healthcare",
            "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.healthcare.type", "hadoop") \
    .config("spark.sql.catalog.healthcare.warehouse", ICEBERG_WAREHOUSE) \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print("=== Phase 3: Data Transformation ===")

# ============================================================
# Step 1: Load raw Iceberg tables
# ============================================================
print("\n[1/5] Loading raw Iceberg tables...")
patients_df   = spark.table("healthcare.patients")
encounters_df = spark.table("healthcare.encounters")
conditions_df = spark.table("healthcare.conditions")
orgs_df       = spark.table("healthcare.organizations")

print(f"  patients:      {patients_df.count():,} rows")
print(f"  encounters:    {encounters_df.count():,} rows")
print(f"  conditions:    {conditions_df.count():,} rows")
print(f"  organizations: {orgs_df.count():,} rows")

# ============================================================
# Step 2: Clean patients
# NOTE: Update column names if different from profiling output
# ============================================================
print("\n[2/5] Cleaning patients...")
patients_clean = patients_df.select(
    col("Id").alias("patient_id"),
    trim(col("GENDER")).alias("gender"),
    to_date(col("BIRTHDATE")).alias("birth_date"),
    trim(lower(col("RACE"))).alias("race"),
    trim(lower(col("ETHNICITY"))).alias("ethnicity")
).withColumn(
    "age", floor(datediff(current_date(), col("birth_date")) / 365.25).cast("int")
).withColumn(
    "age_group",
    when(col("age") < 18, "0-17")
    .when(col("age") < 35, "18-34")
    .when(col("age") < 50, "35-49")
    .when(col("age") < 65, "50-64")
    .otherwise("65+")
).dropDuplicates(["patient_id"])

print(f"  Cleaned patients: {patients_clean.count():,} rows")

# ============================================================
# Step 3: Clean encounters
# NOTE: Remove BASE_ENCOUNTER_COST / TOTAL_CLAIM_COST if columns don't exist
# ============================================================
print("\n[3/5] Cleaning encounters...")
encounters_clean = encounters_df.select(
    col("Id").alias("encounter_id"),
    col("PATIENT").alias("patient_id"),
    col("ORGANIZATION").alias("organization_id"),
    trim(lower(col("ENCOUNTERCLASS"))).alias("encounter_type"),
    to_timestamp(col("START")).alias("encounter_start"),
    to_timestamp(col("STOP")).alias("encounter_stop"),
    col("BASE_ENCOUNTER_COST").cast("double").alias("base_cost"),
    col("TOTAL_CLAIM_COST").cast("double").alias("total_claim_cost")
).withColumn(
    "encounter_duration_days",
    (col("encounter_stop").cast("long") - col("encounter_start").cast("long")) / 86400.0
)

print(f"  Cleaned encounters: {encounters_clean.count():,} rows")

# ============================================================
# Step 4: Clean conditions
# ============================================================
print("\n[4/5] Cleaning conditions...")
conditions_clean = conditions_df.select(
    col("PATIENT").alias("patient_id"),
    col("ENCOUNTER").alias("encounter_id"),
    trim(col("DESCRIPTION")).alias("condition_description"),
    col("CODE").alias("condition_code")
)

orgs_clean = orgs_df.select(
    col("Id").alias("organization_id"),
    trim(col("NAME")).alias("organization_name")
).dropDuplicates(["organization_id"])

# ============================================================
# Step 5: Join and write canonical analytics table
# ============================================================
print("\n[5/5] Joining and writing healthcare_analytics...")
analytics_df = encounters_clean \
    .join(patients_clean, "patient_id", "left") \
    .join(conditions_clean, ["patient_id", "encounter_id"], "left") \
    .join(orgs_clean, "organization_id", "left")

final_df = analytics_df.select(
    "patient_id", "encounter_id",
    "gender", "birth_date", "age", "age_group", "race", "ethnicity",
    "encounter_type", "encounter_start", "encounter_stop", "encounter_duration_days",
    "base_cost", "total_claim_cost",
    "condition_description",
    "organization_id", "organization_name"
)

final_df.writeTo("healthcare.healthcare_analytics") \
    .using("iceberg") \
    .createOrReplace()

final_count = spark.sql("SELECT COUNT(*) AS n FROM healthcare.healthcare_analytics").collect()[0]["n"]
print(f"  healthcare_analytics written — {final_count:,} rows")

print("\n=== Schema of healthcare_analytics ===")
final_df.printSchema()

print("\nNEXT STEP: Run 04_export_mongodb.py")

spark.stop()
