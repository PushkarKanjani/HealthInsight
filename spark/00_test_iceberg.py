"""
spark/00_test_iceberg.py
Phase 3 / Prompt 06 — Minimal Spark and Iceberg Verification Test
=================================================================
Verifies that Apache Spark 3.5 can initialize the Apache Iceberg catalog,
create an Iceberg table on the local warehouse, insert rows, read them,
and cleanly drop the table.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load local environment
load_dotenv()

# Ensure Java and Hadoop paths are synced
if os.getenv("JAVA_HOME"):
    os.environ["PATH"] = os.path.join(os.getenv("JAVA_HOME"), "bin") + os.pathsep + os.environ.get("PATH", "")
if os.getenv("HADOOP_HOME"):
    os.environ["PATH"] = os.path.join(os.getenv("HADOOP_HOME"), "bin") + os.pathsep + os.environ.get("PATH", "")

from pyspark.sql import SparkSession

project_root = Path(__file__).resolve().parent.parent
warehouse_dir = os.getenv("ICEBERG_WAREHOUSE", str(project_root / "iceberg" / "warehouse")).replace("\\", "/")

iceberg_pkg = os.getenv("ICEBERG_PACKAGE", "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.2")

print("\n" + "=" * 80)
print("  HealthInsight — Minimal Apache Iceberg Sanity Test (Prompt 06)")
print("=" * 80)
print(f"Target Warehouse: {warehouse_dir}")
print(f"Iceberg Package:  {iceberg_pkg}")

# Step 1: Initialize Spark with Iceberg extensions & catalog
spark = SparkSession.builder \
    .appName("HealthInsight-Iceberg-SanityTest") \
    .master("local[*]") \
    .config("spark.driver.memory", "2g") \
    .config("spark.jars.packages", iceberg_pkg) \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.iceberg.type", "hadoop") \
    .config("spark.sql.catalog.iceberg.warehouse", warehouse_dir) \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("\n[Proof 1] Iceberg catalog initialized successfully.")

# Step 2: Create healthcare namespace/database in Iceberg catalog
spark.sql("CREATE NAMESPACE IF NOT EXISTS iceberg.healthcare")
print("[Proof 2] Namespace 'iceberg.healthcare' confirmed.")

# Step 3: Create small test Iceberg table
test_table = "iceberg.healthcare.test_iceberg_table"
spark.sql(f"DROP TABLE IF EXISTS {test_table}")
spark.sql(f"""
    CREATE TABLE {test_table} (
        id INT,
        patient_name STRING,
        visit_date STRING
    )
    USING iceberg
""")
print(f"[Proof 3] Test table '{test_table}' created.")

# Step 4: Insert 3 test rows
spark.sql(f"""
    INSERT INTO {test_table} VALUES
    (1, 'Patient Alpha', '2026-10-18'),
    (2, 'Patient Beta',  '2026-10-18'),
    (3, 'Patient Gamma', '2026-10-18')
""")
print("[Proof 4] Test rows written to Iceberg.")

# Step 5: Read the table
read_df = spark.sql(f"SELECT * FROM {test_table} ORDER BY id")
rows = read_df.collect()
print("\n[Proof 5] Test rows read successfully:")
read_df.show(truncate=False)

# Verification assertion
assert len(rows) == 3, f"Expected 3 rows, got {len(rows)}"
assert rows[0]["patient_name"] == "Patient Alpha"
print("Assertion verified: COUNT(*) == 3.")

# Step 6: Drop test table
spark.sql(f"DROP TABLE IF EXISTS {test_table}")
print(f"[Proof 6] Test table '{test_table}' removed.")

spark.stop()

print("\n" + "=" * 80)
print("  PROMPT 06 VERIFICATION COMPLETE: Spark + Iceberg Test PASSED (Exit Code 0)")
print("=" * 80 + "\n")
sys.exit(0)
