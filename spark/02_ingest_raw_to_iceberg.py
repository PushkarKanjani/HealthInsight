"""
spark/02_ingest_raw_to_iceberg.py
Prompt 07 — Raw CSV to Apache Iceberg Ingestion
=================================================
Reads confirmed Synthea CSV files from data/raw/,
normalizes column names to lowercase,
preserves source-to-target schema mappings,
and creates managed Iceberg tables in the local warehouse.

Expected tables:
- iceberg.healthcare.patients      (12,352 rows)
- iceberg.healthcare.encounters    (321,528 rows)
- iceberg.healthcare.conditions    (114,544 rows)
- iceberg.healthcare.organizations (5,499 rows)

Rerunnable: uses createOrReplace() to allow safe, idempotent re-runs.
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

project_root = Path(__file__).resolve().parent.parent
data_dir = os.getenv("DATA_DIR", str(project_root / "data" / "raw")).replace("\\", "/")
warehouse_dir = os.getenv("ICEBERG_WAREHOUSE", "file:/warehouse")
iceberg_pkg = os.getenv("ICEBERG_PACKAGE", "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.2")

print("\n" + "=" * 80)
print("  HealthInsight — Raw CSV to Iceberg Ingestion (Prompt 07)")
print("=" * 80)
print(f"Source Data:      {data_dir}")
print(f"Iceberg Warehouse:{warehouse_dir}")
print(f"Iceberg Package:  {iceberg_pkg}")

# Initialize Spark with Iceberg catalog
spark = SparkSession.builder \
    .appName("HealthInsight-IngestRawToIceberg") \
    .master("local[*]") \
    .config("spark.driver.memory", "4g") \
    .config("spark.jars.packages", iceberg_pkg) \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.iceberg.type", "hadoop") \
    .config("spark.sql.catalog.iceberg.warehouse", warehouse_dir) \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Create namespace
spark.sql("CREATE NAMESPACE IF NOT EXISTS iceberg.healthcare")
print("\nNamespace 'iceberg.healthcare' confirmed.")

def ingest_table(csv_filename, table_name, expected_count):
    csv_path = f"{data_dir}/{csv_filename}"
    if not os.path.exists(csv_path):
        print(f"ERROR: {csv_path} does not exist!")
        sys.exit(1)
        
    print(f"\n---> Ingesting {csv_filename} into iceberg.healthcare.{table_name}...")
    raw_df = spark.read \
        .option("header", True) \
        .option("inferSchema", True) \
        .csv(csv_path)
    
    # Normalize column names to lowercase and strip whitespace
    col_mappings = {}
    normalized_df = raw_df
    for col in raw_df.columns:
        clean_col = col.strip().lower()
        col_mappings[col] = clean_col
        if col != clean_col:
            normalized_df = normalized_df.withColumnRenamed(col, clean_col)
            
    print(f"     Source columns: {len(raw_df.columns)}")
    print(f"     Normalized to:  {', '.join(normalized_df.columns[:5])}... ({len(normalized_df.columns)} total)")
    
    # Write to Iceberg
    target_table = f"iceberg.healthcare.{table_name}"
    normalized_df.writeTo(target_table) \
        .using("iceberg") \
        .createOrReplace()
        
    actual_count = spark.sql(f"SELECT COUNT(*) AS n FROM {target_table}").collect()[0]["n"]
    print(f"     Target Table:   {target_table}")
    print(f"     Ingested Rows:  {actual_count:,} (Expected: {expected_count:,})")
    
    assert actual_count == expected_count, f"Row count mismatch for {target_table}! Got {actual_count}, expected {expected_count}"
    return actual_count, col_mappings

# Ingest core datasets
results = {}
results["patients"] = ingest_table("patients.csv", "patients", 12352)
results["encounters"] = ingest_table("encounters.csv", "encounters", 321528)
results["conditions"] = ingest_table("conditions.csv", "conditions", 114544)
results["organizations"] = ingest_table("organizations.csv", "organizations", 5499)

print("\n" + "=" * 80)
print("  Iceberg Tables in 'iceberg.healthcare':")
print("=" * 80)
spark.sql("SHOW TABLES IN iceberg.healthcare").show(truncate=False)

print("\nIngestion Summary:")
for tbl, (cnt, _) in results.items():
    print(f"  - iceberg.healthcare.{tbl}: {cnt:,} rows")

spark.stop()

print("\n" + "=" * 80)
print("  PROMPT 07 INGESTION COMPLETE (Exit Code 0)")
print("=" * 80 + "\n")
