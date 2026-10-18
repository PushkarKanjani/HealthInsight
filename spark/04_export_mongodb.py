"""
spark/04_export_mongodb.py
Prompt 11 — Export Analytics Aggregates to MongoDB
===================================================
Reads canonical Iceberg analytics tables:
  - iceberg.healthcare.encounter_analytics
  - iceberg.healthcare.condition_analytics
  - iceberg.healthcare.patients

Computes aggregated analytics collections and exports them to MongoDB:
  1. kpis                   (High-level operational and financial KPIs)
  2. condition_summary      (Condition diagnosis frequencies)
  3. encounter_type_summary (Encounter class breakdown, duration, and billing)
  4. encounter_trends       (Monthly longitudinal visit and financial trends)
  5. demographic_summary    (Demographic distributions by age group & gender)
  6. organization_summary   (Hospital and clinic visit volumes and billing)

Mandatory Rule:
  Every document includes `generated_at` and `source_table`.
"""

import os
import sys
from datetime import datetime, timezone
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
    col, count, countDistinct, avg, sum as spark_sum,
    month, year, round as spark_round, when
)
import pymongo

project_root = Path(__file__).resolve().parent.parent
warehouse_dir = os.getenv("ICEBERG_WAREHOUSE", "file:/warehouse")
iceberg_pkg = os.getenv("ICEBERG_PACKAGE", "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.2")
mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
mongo_db_name = os.getenv("MONGODB_DATABASE", "healthinsight")

now_iso = datetime.now(timezone.utc).isoformat()

print("\n" + "=" * 80)
print("  HealthInsight — Export Aggregates to MongoDB (Prompt 11)")
print("=" * 80)
print(f"Iceberg Warehouse: {warehouse_dir}")
print(f"MongoDB Target:    {mongo_uri}/{mongo_db_name}")

# Connect to MongoDB client
try:
    mongo_client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    mongo_client.server_info()
    db = mongo_client[mongo_db_name]
    print("MongoDB connection verified successfully.")
except Exception as e:
    print(f"ERROR: Cannot connect to MongoDB at {mongo_uri}: {e}")
    sys.exit(1)

# Initialize Spark with Iceberg catalog
spark = SparkSession.builder \
    .appName("HealthInsight-ExportMongoDB") \
    .master("local[*]") \
    .config("spark.driver.memory", "4g") \
    .config("spark.jars.packages", iceberg_pkg) \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.iceberg.type", "hadoop") \
    .config("spark.sql.catalog.iceberg.warehouse", warehouse_dir) \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

def save_to_mongo(spark_df, collection_name, indexes=None):
    """Converts a Spark DataFrame to Python dictionaries and writes to MongoDB."""
    records = [row.asDict() for row in spark_df.collect()]
    coll = db[collection_name]
    coll.drop()  # Idempotent overwrite
    if records:
        coll.insert_many(records)
    if indexes:
        for idx in indexes:
            coll.create_index(idx)
    count = coll.count_documents({})
    print(f"  -> Written to MongoDB collection '{collection_name}': {count:,} documents")
    return count

# Load canonical analytics tables
encounter_analytics_df = spark.table("iceberg.healthcare.encounter_analytics")
condition_analytics_df = spark.table("iceberg.healthcare.condition_analytics")
patients_df            = spark.table("iceberg.healthcare.patients")

# ==============================================================================
# 1. KPIs Collection
# ==============================================================================
print("\n[1/6] Computing & Exporting 'kpis'...")
kpis_df = encounter_analytics_df.agg(
    countDistinct("patient_id").alias("total_patients"),
    count("encounter_id").alias("total_encounters"),
    spark_round(avg("duration_minutes"), 2).alias("avg_duration_minutes"),
    spark_round(avg("total_claim_cost"), 2).alias("avg_claim_cost"),
    spark_round(spark_sum("total_claim_cost"), 2).alias("total_claim_cost"),
    spark_round(spark_sum("payer_coverage"), 2).alias("total_payer_coverage"),
    spark_round(spark_sum("patient_out_of_pocket"), 2).alias("total_out_of_pocket")
).withColumn("source_table", col("total_patients") * 0 + 1) \
 .select(
     col("total_patients"),
     col("total_encounters"),
     col("avg_duration_minutes"),
     col("avg_claim_cost"),
     col("total_claim_cost"),
     col("total_payer_coverage"),
     col("total_out_of_pocket")
 )

kpi_dict = kpis_df.collect()[0].asDict()
kpi_dict["source_table"] = "iceberg.healthcare.encounter_analytics"
kpi_dict["generated_at"] = now_iso

db.kpis.drop()
db.kpis.insert_one(kpi_dict)
print(f"  -> Written to MongoDB collection 'kpis': 1 document")
print(f"     Patients: {kpi_dict['total_patients']:,} | Encounters: {kpi_dict['total_encounters']:,} | Billing: ${kpi_dict['total_claim_cost']:,.2f}")

# ==============================================================================
# 2. Condition Summary Collection
# ==============================================================================
print("\n[2/6] Computing & Exporting 'condition_summary'...")
condition_summary_df = condition_analytics_df \
    .filter(col("condition_description").isNotNull()) \
    .groupBy("condition_code", "condition_description") \
    .agg(count("*").alias("frequency")) \
    .orderBy(col("frequency").desc())

condition_records = []
for row in condition_summary_df.collect():
    d = row.asDict()
    d["source_table"] = "iceberg.healthcare.condition_analytics"
    d["generated_at"] = now_iso
    condition_records.append(d)

db.condition_summary.drop()
if condition_records:
    db.condition_summary.insert_many(condition_records)
db.condition_summary.create_index([("condition_description", pymongo.ASCENDING)])
db.condition_summary.create_index([("frequency", pymongo.DESCENDING)])
print(f"  -> Written to MongoDB collection 'condition_summary': {len(condition_records):,} documents")

# ==============================================================================
# 3. Encounter Type Summary Collection
# ==============================================================================
print("\n[3/6] Computing & Exporting 'encounter_type_summary'...")
enc_type_df = encounter_analytics_df \
    .filter(col("encounter_class").isNotNull()) \
    .groupBy("encounter_class") \
    .agg(
        count("*").alias("encounter_count"),
        spark_round(avg("duration_minutes"), 2).alias("avg_duration_minutes"),
        spark_round(avg("total_claim_cost"), 2).alias("avg_claim_cost"),
        spark_round(spark_sum("total_claim_cost"), 2).alias("total_claim_cost"),
        spark_round(spark_sum("payer_coverage"), 2).alias("total_payer_coverage"),
        spark_round(spark_sum("patient_out_of_pocket"), 2).alias("total_out_of_pocket")
    ).orderBy(col("encounter_count").desc())

enc_type_records = []
for row in enc_type_df.collect():
    d = row.asDict()
    d["source_table"] = "iceberg.healthcare.encounter_analytics"
    d["generated_at"] = now_iso
    enc_type_records.append(d)

db.encounter_type_summary.drop()
if enc_type_records:
    db.encounter_type_summary.insert_many(enc_type_records)
db.encounter_type_summary.create_index([("encounter_class", pymongo.ASCENDING)])
db.encounter_type_summary.create_index([("encounter_count", pymongo.DESCENDING)])
print(f"  -> Written to MongoDB collection 'encounter_type_summary': {len(enc_type_records):,} documents")

# ==============================================================================
# 4. Encounter Trends Collection
# ==============================================================================
print("\n[4/6] Computing & Exporting 'encounter_trends'...")
trends_df = encounter_analytics_df \
    .filter(col("start_time").isNotNull()) \
    .withColumn("year", year("start_time")) \
    .withColumn("month", month("start_time")) \
    .groupBy("year", "month") \
    .agg(
        count("*").alias("encounter_count"),
        spark_round(spark_sum("total_claim_cost"), 2).alias("total_claim_cost"),
        spark_round(avg("total_claim_cost"), 2).alias("avg_claim_cost")
    ).orderBy("year", "month")

trends_records = []
for row in trends_df.collect():
    d = row.asDict()
    d["source_table"] = "iceberg.healthcare.encounter_analytics"
    d["generated_at"] = now_iso
    trends_records.append(d)

db.encounter_trends.drop()
if trends_records:
    db.encounter_trends.insert_many(trends_records)
db.encounter_trends.create_index([("year", pymongo.ASCENDING), ("month", pymongo.ASCENDING)])
print(f"  -> Written to MongoDB collection 'encounter_trends': {len(trends_records):,} documents")

# ==============================================================================
# 5. Demographic Summary Collection
# ==============================================================================
print("\n[5/6] Computing & Exporting 'demographic_summary'...")
demo_df = encounter_analytics_df \
    .filter(col("age_group").isNotNull()) \
    .groupBy("patient_gender", "age_group", "patient_race", "patient_ethnicity") \
    .agg(
        countDistinct("patient_id").alias("distinct_patients"),
        count("encounter_id").alias("encounter_count"),
        spark_round(spark_sum("total_claim_cost"), 2).alias("total_claim_cost")
    ).orderBy(col("encounter_count").desc())

demo_records = []
for row in demo_df.collect():
    d = row.asDict()
    d["source_table"] = "iceberg.healthcare.encounter_analytics"
    d["generated_at"] = now_iso
    demo_records.append(d)

db.demographic_summary.drop()
if demo_records:
    db.demographic_summary.insert_many(demo_records)
db.demographic_summary.create_index([("patient_gender", pymongo.ASCENDING), ("age_group", pymongo.ASCENDING)])
print(f"  -> Written to MongoDB collection 'demographic_summary': {len(demo_records):,} documents")

# ==============================================================================
# 6. Organization Summary Collection
# ==============================================================================
print("\n[6/6] Computing & Exporting 'organization_summary'...")
org_df = encounter_analytics_df \
    .filter(col("organization_name").isNotNull()) \
    .groupBy("organization_id", "organization_name", "organization_city", "organization_state") \
    .agg(
        count("encounter_id").alias("total_encounters"),
        spark_round(spark_sum("total_claim_cost"), 2).alias("total_billing"),
        spark_round(avg("total_claim_cost"), 2).alias("avg_cost")
    ).orderBy(col("total_encounters").desc())

org_records = []
for row in org_df.collect():
    d = row.asDict()
    d["source_table"] = "iceberg.healthcare.encounter_analytics"
    d["generated_at"] = now_iso
    org_records.append(d)

db.organization_summary.drop()
if org_records:
    db.organization_summary.insert_many(org_records)
db.organization_summary.create_index([("organization_name", pymongo.ASCENDING)])
db.organization_summary.create_index([("total_encounters", pymongo.DESCENDING)])
print(f"  -> Written to MongoDB collection 'organization_summary': {len(org_records):,} documents")

print("\n" + "=" * 80)
print("  MongoDB Collections in 'healthinsight':")
print("=" * 80)
for c in db.list_collection_names():
    print(f"  - {c}: {db[c].count_documents({}):,} documents")

spark.stop()

print("\n" + "=" * 80)
print("  PROMPT 11 MONGODB EXPORT COMPLETE (Exit Code 0)")
print("=" * 80 + "\n")
