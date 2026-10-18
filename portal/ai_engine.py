"""
AI Text-to-SQL Engine for HealthInsight.
Translates plain clinical questions to Trino SQL via Gemini 2.0 Flash,
with a robust 12-pattern deterministic offline fallback engine.
"""
import os
import re
from typing import Dict, Any, Tuple
from dotenv import load_dotenv
from portal.schema_context import SCHEMA_PROMPT
from portal.query_engine import execute_trino_query

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# 12 Deterministic Fallback Queries Grounded in Exact Iceberg Schema
FALLBACK_QUERIES = [
    {
        "keywords": ["top condition", "most common condition", "prevalent", "disease", "illness", "diagnos"],
        "sql": """SELECT condition_description AS condition_name, COUNT(*) AS case_count 
FROM iceberg.healthcare.condition_analytics 
GROUP BY condition_description 
ORDER BY case_count DESC 
LIMIT 10""",
        "explanation": "Identifies the 10 most frequent clinical conditions across 114,544 diagnosed patient events.",
        "chart": "bar"
    },
    {
        "keywords": ["cost", "claim", "expensive", "bill", "financial"],
        "sql": """SELECT encounter_class, 
       COUNT(*) AS total_encounters, 
       ROUND(AVG(total_claim_cost), 2) AS avg_claim_cost,
       ROUND(AVG(payer_coverage), 2) AS avg_payer_paid,
       ROUND(AVG(patient_out_of_pocket), 2) AS avg_out_of_pocket
FROM iceberg.healthcare.encounter_analytics 
GROUP BY encounter_class 
ORDER BY avg_claim_cost DESC""",
        "explanation": "Summarizes financial cost metrics (average claim cost, payer coverage, out-of-pocket) by encounter class.",
        "chart": "bar"
    },
    {
        "keywords": ["age group", "age bracket", "elderly", "pediatric", "demographic", "distribution by age"],
        "sql": """SELECT age_group, 
       COUNT(*) AS encounter_count, 
       ROUND(AVG(total_claim_cost), 2) AS avg_cost,
       ROUND(AVG(duration_minutes), 1) AS avg_duration_mins
FROM iceberg.healthcare.encounter_analytics 
GROUP BY age_group 
ORDER BY age_group""",
        "explanation": "Breaks down healthcare encounter volume, claim costs, and encounter duration across standardized age brackets.",
        "chart": "bar"
    },
    {
        "keywords": ["gender", "male", "female", "sex"],
        "sql": """SELECT patient_gender, 
       COUNT(*) AS encounter_count, 
       ROUND(AVG(total_claim_cost), 2) AS avg_cost,
       ROUND(SUM(total_claim_cost), 2) AS total_spend
FROM iceberg.healthcare.encounter_analytics 
GROUP BY patient_gender 
ORDER BY encounter_count DESC""",
        "explanation": "Analyzes encounter frequency and medical spend split by patient gender.",
        "chart": "doughnut"
    },
    {
        "keywords": ["trend", "month", "timeline", "over time", "longitudinal"],
        "sql": """SELECT date_format(start_time, '%Y-%m') AS encounter_month, 
       COUNT(*) AS encounter_volume 
FROM iceberg.healthcare.encounter_analytics 
WHERE start_time >= TIMESTAMP '2019-01-01 00:00:00'
GROUP BY date_format(start_time, '%Y-%m') 
ORDER BY encounter_month ASC 
LIMIT 36""",
        "explanation": "Tracks monthly encounter volume trajectories to identify longitudinal healthcare demand patterns.",
        "chart": "line"
    },
    {
        "keywords": ["inpatient", "hospital stay", "admi"],
        "sql": """SELECT patient_city, 
       COUNT(*) AS inpatient_admissions, 
       ROUND(AVG(duration_minutes) / 60.0, 1) AS avg_stay_hours,
       ROUND(AVG(total_claim_cost), 2) AS avg_admission_cost
FROM iceberg.healthcare.encounter_analytics 
WHERE encounter_class = 'inpatient' 
GROUP BY patient_city 
ORDER BY inpatient_admissions DESC 
LIMIT 10""",
        "explanation": "Examines inpatient hospitalizations, stay durations (in hours), and admission costs across top patient cities.",
        "chart": "bar"
    },
    {
        "keywords": ["duration", "length of visit", "how long", "time spent", "minutes"],
        "sql": """SELECT encounter_class, 
       ROUND(AVG(duration_minutes), 1) AS avg_duration_mins, 
       ROUND(MIN(duration_minutes), 1) AS min_duration_mins,
       ROUND(MAX(duration_minutes), 1) AS max_duration_mins
FROM iceberg.healthcare.encounter_analytics 
GROUP BY encounter_class 
ORDER BY avg_duration_mins DESC""",
        "explanation": "Calculates clinical duration ranges and averages in minutes across encounter types.",
        "chart": "bar"
    },
    {
        "keywords": ["wellness", "preventive", "checkup", "routine"],
        "sql": """SELECT age_group, 
       COUNT(*) AS wellness_encounters, 
       ROUND(AVG(total_claim_cost), 2) AS avg_cost 
FROM iceberg.healthcare.encounter_analytics 
WHERE encounter_class = 'wellness' 
GROUP BY age_group 
ORDER BY wellness_encounters DESC""",
        "explanation": "Assesses preventive and wellness checkup utilization across age groups.",
        "chart": "bar"
    },
    {
        "keywords": ["emergency", "er", "urgent", "acute"],
        "sql": """SELECT organization_name, 
       COUNT(*) AS emergency_encounters,
       ROUND(AVG(total_claim_cost), 2) AS avg_emergency_cost 
FROM iceberg.healthcare.encounter_analytics 
WHERE encounter_class = 'emergency' 
GROUP BY organization_name 
ORDER BY emergency_encounters DESC 
LIMIT 8""",
        "explanation": "Ranks healthcare organizations by emergency department encounter volume and average costs.",
        "chart": "bar"
    },
    {
        "keywords": ["hospital", "organization", "facility", "provider", "clinic"],
        "sql": """SELECT organization_name, 
       organization_city, 
       COUNT(*) AS total_encounters, 
       ROUND(SUM(total_claim_cost), 2) AS total_billed 
FROM iceberg.healthcare.encounter_analytics 
GROUP BY organization_name, organization_city 
ORDER BY total_encounters DESC 
LIMIT 10""",
        "explanation": "Ranks top healthcare delivery organizations by total patient encounter volume and gross billing.",
        "chart": "bar"
    },
    {
        "keywords": ["payer", "insurance", "coverage", "out of pocket", "patient paid"],
        "sql": """SELECT encounter_class, 
       ROUND(SUM(payer_coverage), 2) AS total_insurance_paid, 
       ROUND(SUM(patient_out_of_pocket), 2) AS total_patient_paid,
       ROUND(SUM(payer_coverage) * 100.0 / NULLIF(SUM(total_claim_cost), 0), 1) AS coverage_pct
FROM iceberg.healthcare.encounter_analytics 
GROUP BY encounter_class 
ORDER BY total_insurance_paid DESC""",
        "explanation": "Compares insurance payer coverage vs. out-of-pocket costs with payer absorption percentage.",
        "chart": "bar"
    },
    {
        "keywords": ["year", "annual", "patient count", "volume by year"],
        "sql": """SELECT YEAR(start_time) AS encounter_year, 
       COUNT(DISTINCT patient_id) AS active_patients, 
       COUNT(*) AS total_encounters,
       ROUND(SUM(total_claim_cost), 2) AS annual_claims
FROM iceberg.healthcare.encounter_analytics 
GROUP BY YEAR(start_time) 
ORDER BY encounter_year DESC 
LIMIT 10""",
        "explanation": "Summarizes longitudinal yearly cohort metrics: unique active patients, total visits, and annual spend.",
        "chart": "line"
    }
]


def match_deterministic_fallback(question: str) -> Dict[str, Any]:
    """Find best matching fallback template based on question keywords."""
    lower_q = question.lower()
    
    best_match = None
    max_score = 0

    for item in FALLBACK_QUERIES:
        score = sum(1 for kw in item["keywords"] if kw in lower_q)
        if score > max_score:
            max_score = score
            best_match = item

    if not best_match:
        # Default fallback to encounter class distribution
        best_match = {
            "sql": """SELECT encounter_class, 
       COUNT(*) AS count, 
       ROUND(AVG(total_claim_cost), 2) AS avg_cost 
FROM iceberg.healthcare.encounter_analytics 
GROUP BY encounter_class 
ORDER BY count DESC""",
            "explanation": "Displays breakdown of clinical encounters by class with average claim costs.",
            "chart": "bar"
        }

    return best_match


def determine_chart_type(columns: list, rows: list) -> str:
    """Infer optimal chart type based on column semantics and row structure."""
    if len(columns) < 2 or not rows:
        return "table"
    
    first_col = str(columns[0]).lower()
    if any(k in first_col for k in ["gender", "sex", "status"]):
        return "doughnut"
    if any(k in first_col for k in ["month", "year", "date", "time"]):
        return "line"
    return "bar"


def generate_sql_with_gemini(question: str) -> Tuple[str, str]:
    """Invoke Google Gemini 2.0 Flash to synthesize Trino SQL from natural language."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured.")

    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""{SCHEMA_PROMPT}

USER CLINICAL QUESTION:
"{question}"

Generate the single optimal Trino SQL query to answer this question.
Respond strictly in this format:
```sql
<YOUR SQL QUERY HERE>
```
EXPLANATION: <One sentence explanation of what the query calculates.>
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    text = response.text or ""

    # Extract SQL
    sql_match = re.search(r"```sql\s*(.*?)\s*```", text, re.DOTALL)
    if sql_match:
        generated_sql = sql_match.group(1).strip()
    else:
        select_match = re.search(r"(SELECT\b.*)", text, re.DOTALL | re.IGNORECASE)
        if select_match:
            generated_sql = select_match.group(1).strip()
        else:
            raise ValueError("No valid SQL block found in Gemini response.")

    # Extract explanation
    exp_match = re.search(r"EXPLANATION:\s*(.*)", text)
    explanation = exp_match.group(1).strip() if exp_match else "Synthesized Trino SQL query for clinical analytics."

    return generated_sql, explanation


def process_clinical_question(question: str) -> Dict[str, Any]:
    """End-to-end question answering pipeline: Gemini → Fallback → Trino execution."""
    cleaned_q = question.strip()
    if not cleaned_q:
        raise ValueError("Question cannot be empty.")

    engine_used = "gemini-2.0-flash"
    sql = ""
    explanation = ""
    chart_hint = "bar"

    # Try Gemini if key is present
    if GEMINI_API_KEY:
        try:
            sql, explanation = generate_sql_with_gemini(cleaned_q)
        except Exception:
            fallback = match_deterministic_fallback(cleaned_q)
            sql = fallback["sql"]
            explanation = fallback["explanation"]
            chart_hint = fallback["chart"]
            engine_used = "deterministic-fallback"
    else:
        fallback = match_deterministic_fallback(cleaned_q)
        sql = fallback["sql"]
        explanation = fallback["explanation"]
        chart_hint = fallback["chart"]
        engine_used = "deterministic-fallback"

    # Execute against Trino
    query_result = execute_trino_query(sql)

    # Determine recommended visualization
    final_chart = chart_hint if chart_hint != "table" else determine_chart_type(query_result["columns"], query_result["rows"])

    return {
        "question": cleaned_q,
        "engine": engine_used,
        "explanation": explanation,
        "sql": sql,
        "columns": query_result["columns"],
        "rows": query_result["rows"],
        "row_count": query_result["row_count"],
        "execution_ms": query_result["execution_ms"],
        "chart_type": final_chart
    }
