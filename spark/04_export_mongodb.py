"""
spark/04_export_mongodb.py
Phase 4 — Export to MongoDB
=============================
Reads the canonical healthcare_analytics Iceberg table, computes
aggregate DataFrames, and writes them to MongoDB collections using
the official MongoDB Spark Connector.

PREREQUISITE: Run 03_transform_healthcare_data.py first.
PREREQUISITE: MongoDB must be running (mongod).
"""

import os
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, countDistinct, avg, sum as spark_sum,
    month, year, lit, round as spark_round
)
from dotenv import load_dotenv

load_dotenv()

ICEBERG_WAREHOUSE = os.getenv("ICEBERG_WAREHOUSE", "iceberg/warehouse")
MONGODB_URI       = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DATABASE  = os.getenv("MONGODB_DATABASE", "healthinsight")
ICEBERG_JAR       = os.getenv("ICEBERG_JAR", "")
MONGO_JAR         = os.getenv("MONGO_JAR", "")

JARS = ",".join(filter(None, [ICEBERG_JAR, MONGO_JAR]))
NOW  = str(datetime.now().isoformat())

spark = SparkSession.builder \
    .appName("HealthInsight-ExportMongoDB") \
    .master("local[*]") \
    .config("spark.jars", JARS) \
    .config("spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.healthcare",
            "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.healthcare.type", "hadoop") \
    .config("spark.sql.catalog.healthcare.warehouse", ICEBERG_WAREHOUSE) \
    .config("spark.mongodb.write.connection.uri", MONGODB_URI) \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print("=== Phase 4: MongoDB Export ===")
print(f"MongoDB URI: {MONGODB_URI}")
print(f"Database: {MONGODB_DATABASE}")

def write_to_mongo(df, collection):
    """Write a DataFrame to MongoDB, overwriting the collection."""
    df.write \
      .format("mongodb") \
      .mode("overwrite") \
      .option("database", MONGODB_DATABASE) \
      .option("collection", collection) \
      .save()
    print(f"  Written: {MONGODB_DATABASE}.{collection} ({df.count():,} documents)")

# Load canonical table
analytics_df = spark.table("healthcare.healthcare_analytics")
total_rows = analytics_df.count()
print(f"\nSource table: healthcare.healthcare_analytics ({total_rows:,} rows)")

# ============================================================
# 1. KPIs (single aggregate document)
# ============================================================
print("\n[1/6] Exporting KPIs...")
kpis_df = analytics_df.agg(
    countDistinct("patient_id").alias("total_patients"),
    count("encounter_id").alias("total_encounters"),
    spark_round(avg("encounter_duration_days"), 2).alias("avg_duration_days"),
    spark_round(avg("total_claim_cost"), 2).alias("avg_claim_cost"),
    spark_round(spark_sum("total_claim_cost"), 2).alias("total_cost")
).withColumn("generated_at", lit(NOW)) \
 .withColumn("source_table", lit("healthcare.healthcare_analytics"))

write_to_mongo(kpis_df, "kpis")

# ============================================================
# 2. Condition Summary
# ============================================================
print("\n[2/6] Exporting condition_summary...")
condition_df = analytics_df \
    .filter(col("condition_description").isNotNull()) \
    .groupBy("condition_description") \
    .agg(count("*").alias("frequency")) \
    .withColumn("generated_at", lit(NOW)) \
    .withColumn("source_table", lit("healthcare.healthcare_analytics")) \
    .orderBy(col("frequency").desc())

write_to_mongo(condition_df, "condition_summary")

# ============================================================
# 3. Demographic Summary
# ============================================================
print("\n[3/6] Exporting demographic_summary...")
demo_df = analytics_df \
    .groupBy("gender", "age_group", "race", "ethnicity") \
    .agg(count("*").alias("encounter_count")) \
    .withColumn("generated_at", lit(NOW))

write_to_mongo(demo_df, "demographic_summary")

# ============================================================
# 4. Encounter Type Summary
# ============================================================
print("\n[4/6] Exporting encounter_type_summary...")
enc_type_df = analytics_df \
    .filter(col("encounter_type").isNotNull()) \
    .groupBy("encounter_type") \
    .agg(
        count("*").alias("encounter_count"),
        spark_round(avg("encounter_duration_days"), 2).alias("avg_duration_days"),
        spark_round(avg("total_claim_cost"), 2).alias("avg_claim_cost")
    ) \
    .withColumn("generated_at", lit(NOW))

write_to_mongo(enc_type_df, "encounter_type_summary")

# ============================================================
# 5. Encounter Trends (monthly)
# ============================================================
print("\n[5/6] Exporting encounter_trends...")
trends_df = analytics_df \
    .filter(col("encounter_start").isNotNull()) \
    .withColumn("year", year("encounter_start")) \
    .withColumn("month", month("encounter_start")) \
    .groupBy("year", "month") \
    .agg(count("*").alias("encounter_count")) \
    .withColumn("generated_at", lit(NOW)) \
    .orderBy("year", "month")

write_to_mongo(trends_df, "encounter_trends")

# ============================================================
# 6. Organization Summary
# ============================================================
print("\n[6/6] Exporting organization_summary...")
org_df = analytics_df \
    .filter(col("organization_name").isNotNull()) \
    .groupBy("organization_id", "organization_name") \
    .agg(
        count("encounter_id").alias("total_encounters"),
        spark_round(avg("total_claim_cost"), 2).alias("avg_cost")
    ) \
    .withColumn("generated_at", lit(NOW)) \
    .orderBy(col("total_encounters").desc())

write_to_mongo(org_df, "organization_summary")

print("\n=== MongoDB Export Complete ===")
print(f"All collections written to database: {MONGODB_DATABASE}")
print("\nNEXT STEP: Run mongodb/indexes.js to create indexes.")
print("           Then run mongodb/validation_queries.js to verify.")

spark.stop()
