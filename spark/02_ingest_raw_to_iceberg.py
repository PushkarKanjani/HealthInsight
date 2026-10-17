"""
spark/02_create_iceberg_tables.py
Phase 2 — Create Iceberg Tables
=================================
Configures Spark with the Iceberg catalog and writes raw Synthea CSVs
as managed Iceberg tables in the local warehouse.

PREREQUISITE: Run 01_profile_dataset.py first and confirm column names.
UPDATE: Adjust column selections below to match real CSV columns.
"""

import os
from pyspark.sql import SparkSession
from dotenv import load_dotenv

load_dotenv()

DATA_DIR        = os.getenv("DATA_DIR", "data/raw")
ICEBERG_WAREHOUSE = os.getenv("ICEBERG_WAREHOUSE", "iceberg/warehouse")
ICEBERG_JAR     = os.getenv("ICEBERG_JAR", "")
MONGO_JAR       = os.getenv("MONGO_JAR", "")

JARS = ",".join(filter(None, [ICEBERG_JAR, MONGO_JAR]))

spark = SparkSession.builder \
    .appName("HealthInsight-CreateIcebergTables") \
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

print("Spark session started. Iceberg catalog: healthcare")
print(f"Warehouse: {ICEBERG_WAREHOUSE}")

# Create database namespace
spark.sql("CREATE NAMESPACE IF NOT EXISTS healthcare")

# ============================================================
# patients
# ============================================================
print("\n[1/4] Creating healthcare.patients...")
patients_df = spark.read \
    .option("header", True) \
    .option("inferSchema", True) \
    .csv(f"{DATA_DIR}/patients.csv")

patients_df.writeTo("healthcare.patients") \
    .using("iceberg") \
    .createOrReplace()

count = spark.sql("SELECT COUNT(*) AS n FROM healthcare.patients").collect()[0]["n"]
print(f"  healthcare.patients created — {count:,} rows")

# ============================================================
# encounters
# ============================================================
print("\n[2/4] Creating healthcare.encounters...")
encounters_df = spark.read \
    .option("header", True) \
    .option("inferSchema", True) \
    .csv(f"{DATA_DIR}/encounters.csv")

encounters_df.writeTo("healthcare.encounters") \
    .using("iceberg") \
    .createOrReplace()

count = spark.sql("SELECT COUNT(*) AS n FROM healthcare.encounters").collect()[0]["n"]
print(f"  healthcare.encounters created — {count:,} rows")

# ============================================================
# conditions
# ============================================================
print("\n[3/4] Creating healthcare.conditions...")
conditions_df = spark.read \
    .option("header", True) \
    .option("inferSchema", True) \
    .csv(f"{DATA_DIR}/conditions.csv")

conditions_df.writeTo("healthcare.conditions") \
    .using("iceberg") \
    .createOrReplace()

count = spark.sql("SELECT COUNT(*) AS n FROM healthcare.conditions").collect()[0]["n"]
print(f"  healthcare.conditions created — {count:,} rows")

# ============================================================
# organizations
# ============================================================
print("\n[4/4] Creating healthcare.organizations...")
orgs_df = spark.read \
    .option("header", True) \
    .option("inferSchema", True) \
    .csv(f"{DATA_DIR}/organizations.csv")

orgs_df.writeTo("healthcare.organizations") \
    .using("iceberg") \
    .createOrReplace()

count = spark.sql("SELECT COUNT(*) AS n FROM healthcare.organizations").collect()[0]["n"]
print(f"  healthcare.organizations created — {count:,} rows")

# ============================================================
# Verify
# ============================================================
print("\n=== Iceberg Tables Created ===")
spark.sql("SHOW TABLES IN healthcare").show()

print("NEXT STEP: Run 03_transform_healthcare_data.py")

spark.stop()
