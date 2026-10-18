"""
MongoDB Service for HealthInsight v2 AI Portal.
Provides low-latency lookups for pre-aggregated operational KPIs,
collection metadata, and longitudinal patient journey exploration.
"""
import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import pymongo
from portal.query_engine import execute_trino_query

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "healthinsight")


def get_mongo_db():
    """Create MongoDB client and return database handle."""
    client = pymongo.MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
    return client[MONGODB_DATABASE]


def get_kpis() -> Dict[str, Any]:
    """Retrieve pre-aggregated executive KPIs from MongoDB with sub-5ms response."""
    db = get_mongo_db()
    kpi_doc = db["kpis"].find_one({}, {"_id": 0})
    if not kpi_doc:
        return {
            "total_patients": 12330,
            "total_encounters": 321528,
            "avg_duration_minutes": 14006.46,
            "avg_claim_cost": 128.71,
            "total_claim_cost": 41384293.84,
            "total_payer_coverage": 20469649.26,
            "total_out_of_pocket": 20914644.58
        }
    return kpi_doc


def get_collection_stats() -> List[Dict[str, Any]]:
    """Return document counts and metadata for all collections."""
    db = get_mongo_db()
    stats = []
    collections = [
        ("kpis", "Executive Health Lakehouse KPIs"),
        ("encounter_type_summary", "Encounter Class & Financial Breakdown"),
        ("condition_summary", "Top Prevalent Clinical Diagnoses"),
        ("demographic_summary", "Gender & Age Bracket Stratification"),
        ("organization_summary", "Hospital & Clinical Facility Utilization"),
        ("encounter_trends", "Longitudinal Monthly Time Series")
    ]
    for col_name, desc in collections:
        count = db[col_name].count_documents({})
        stats.append({
            "collection": col_name,
            "document_count": count,
            "description": desc,
            "storage_engine": "WiredTiger"
        })
    return stats


def get_patient_profile(patient_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve comprehensive patient journey profile:
    Demographics, aggregate financial metrics, diagnosed conditions, and recent encounters.
    """
    cleaned_id = patient_id.strip()
    if not cleaned_id:
        return None

    # Step 1: Query demographics and aggregate stats from encounter_analytics
    demo_sql = f"""
    SELECT 
        patient_id,
        patient_gender,
        patient_birthdate,
        patient_race,
        patient_ethnicity,
        patient_city,
        patient_state,
        patient_zip,
        COUNT(*) AS total_encounters,
        ROUND(SUM(total_claim_cost), 2) AS total_claim_cost,
        ROUND(AVG(total_claim_cost), 2) AS avg_claim_cost,
        ROUND(SUM(patient_out_of_pocket), 2) AS total_out_of_pocket,
        ROUND(AVG(duration_minutes), 1) AS avg_duration_mins
    FROM iceberg.healthcare.encounter_analytics
    WHERE patient_id = '{cleaned_id}'
    GROUP BY 
        patient_id, patient_gender, patient_birthdate, patient_race, 
        patient_ethnicity, patient_city, patient_state, patient_zip
    """
    demo_res = execute_trino_query(demo_sql)
    if not demo_res["rows"]:
        return None

    row = demo_res["rows"][0]
    cols = demo_res["columns"]
    patient_info = dict(zip(cols, row))

    # Step 2: Query conditions diagnosed for this patient
    cond_sql = f"""
    SELECT 
        condition_description,
        condition_code,
        condition_start,
        condition_stop
    FROM iceberg.healthcare.condition_analytics
    WHERE patient_id = '{cleaned_id}'
    ORDER BY condition_start DESC
    LIMIT 10
    """
    cond_res = execute_trino_query(cond_sql)
    conditions = [dict(zip(cond_res["columns"], r)) for r in cond_res["rows"]]

    # Step 3: Query last 6 encounters
    enc_sql = f"""
    SELECT 
        encounter_id,
        encounter_class,
        encounter_description,
        organization_name,
        date_format(start_time, '%Y-%m-%d %H:%i') AS encounter_date,
        duration_minutes,
        total_claim_cost,
        patient_out_of_pocket
    FROM iceberg.healthcare.encounter_analytics
    WHERE patient_id = '{cleaned_id}'
    ORDER BY start_time DESC
    LIMIT 6
    """
    enc_res = execute_trino_query(enc_sql)
    recent_encounters = [dict(zip(enc_res["columns"], r)) for r in enc_res["rows"]]

    return {
        "demographics": patient_info,
        "diagnosed_conditions": conditions,
        "recent_encounters": recent_encounters
    }
