# HealthInsight — Data Lineage & Entity Transformation Model
**Standard:** HL7 FHIR-derived Synthea Synthetic Clinical Schema  
**ETL Engine:** Apache Spark 3.5  
**Table Format:** Apache Iceberg 1.8  

---

## 1. End-to-End Data Flow Diagram

```
[Raw CSV Tier]
  ├── patients.csv      (12,352 rows)  --> PK: Id
  ├── encounters.csv    (321,528 rows) --> PK: Id, FK: PATIENT, ORGANIZATION
  ├── conditions.csv    (114,544 rows) --> FK: ENCOUNTER, PATIENT
  └── organizations.csv (5,499 rows)   --> PK: Id
             │
             ▼ Spark Ingestion (spark/02_ingest_raw_to_iceberg.py)
[Raw Iceberg Tier]
  ├── healthcare.patients
  ├── healthcare.encounters
  ├── healthcare.conditions
  └── healthcare.organizations
             │
             ▼ Spark Transformation (spark/03_build_analytics_tables.py)
[Analytical Iceberg Tier]
  ├── Table 1: healthcare.encounter_analytics (321,528 rows - Exactly 1 row/encounter)
  └── Table 2: healthcare.condition_analytics (114,544 rows - 1 row/condition-encounter pair)
             │
             ├─────────────────────────────────────────┐
             ▼                                         ▼
   [Trino Distributed SQL Engine]           [MongoDB NoSQL Serving Store]
   (Interactive Queries for Superset)       (Pre-aggregated JSON Collections)
             │                                         │
             ▼                                         ▼
   [Apache Superset Dashboard]              [Operational Microservice API]
```

---

## 2. The Core Architectural Rule: Two-Table Separation

> [!CAUTION]
> **Why One Combined Table is Strictly Prohibited:**
> If you execute a single join: `patients JOIN encounters JOIN conditions`, an encounter with 4 diagnosed conditions produces **4 duplicate encounter rows**. 
> - Encounter count becomes inflated by ~400%.
> - Recorded healthcare costs are multiplied 4x.
> - Average encounter duration becomes mathematically corrupted.

To maintain strict data integrity, HealthInsight separates transformations into **two dedicated analytical tables**:

### Table 1: `healthcare.encounter_analytics`
- **Granularity:** Exactly **1 row per clinical encounter**.
- **Primary Key:** `encounter_id`.
- **Validation Invariant:** `COUNT(*) == COUNT(DISTINCT encounter_id)` (Assertion enforced during build).
- **Source Tables Joined:**
  - `encounters` (base table)
  - `patients` (joined via `encounters.patient == patients.id`)
  - `organizations` (joined via `encounters.organization == organizations.id`)
- **Fields Provided:**
  - `encounter_id`, `patient_id`, `organization_id`, `organization_name`
  - `start_time`, `stop_time`, `encounter_class`, `encounter_code`, `encounter_description`
  - `duration_minutes`, `duration_days`
  - `base_cost`, `total_claim_cost`, `payer_coverage`
  - `patient_gender`, `patient_race`, `patient_ethnicity`, `patient_city`, `patient_state`
  - `patient_age_at_encounter` = `floor(months_between(start_time, birth_date) / 12)`
  - `encounter_year`, `encounter_month`, `encounter_year_month`
- **Permitted Analytical Usage:**
  - Total encounter counts
  - Average duration & duration distributions
  - Total & average costs
  - Organization volume and revenue metrics
  - Time-series and seasonal trends

---

### Table 2: `healthcare.condition_analytics`
- **Granularity:** Exactly **1 row per diagnosed condition event**.
- **Key:** Composite (`encounter_id` + `condition_code` + `condition_start`).
- **Source Tables Joined:**
  - `conditions` (base table)
  - `patients` (joined via `conditions.patient == patients.id`)
  - `encounters` (joined via `conditions.encounter == encounters.id`)
- **Fields Provided:**
  - `condition_code`, `condition_description`, `condition_start`, `condition_stop`
  - `encounter_id`, `encounter_class`
  - `patient_id`, `patient_gender`, `patient_race`, `patient_ethnicity`
  - `patient_age_at_onset` = `floor(months_between(condition_start, birth_date) / 12)`
  - `age_group` (0–17 Pediatric, 18–35 Young Adult, 36–50 Middle Age, 51–64 Senior, 65+ Geriatric)
- **Permitted Analytical Usage:**
  - Top 20 most frequent clinical conditions
  - Condition prevalence split by gender
  - Condition prevalence across age brackets
- **PROHIBITED USAGE:**
  - Never sum encounter costs from this table.
  - Never count total hospital visits from this table.

---

## 3. Date & Age Calculation Protocol

### Why `current_date()` is Forbidden
In longitudinal datasets spanning years (e.g. 2018–2024), calculating a patient's age using `current_date()` or today's year is invalid:
- A pediatric patient who visited a clinic in 2019 at age 5 would be erroneously categorized as a teenager (age 12) if calculated against 2026.
- Deceased patients would continue aging indefinitely.

### Event-Time Relative Age Formula
Age is calculated **relative to the exact date the clinical event took place**:
```sql
FLOOR(MONTHS_BETWEEN(encounter_start, patient_birthdate) / 12)
```

---

## 4. Serving Tier Lineage (MongoDB Collections)

Spark extracts aggregate metrics from the analytical tables and writes to MongoDB:

| MongoDB Collection | Source Analytical Table | Document Schema / Content |
|---|---|---|
| `kpis` | `encounter_analytics` | Pre-computed system metrics: `total_patients`, `total_encounters`, `avg_duration_days`, `avg_claim_cost`, `generated_at`. |
| `condition_summary` | `condition_analytics` | Array of condition documents: `condition_code`, `condition_name`, `frequency`, `pct_of_diagnoses`. |
| `encounter_type_summary`| `encounter_analytics` | Class metrics: `encounter_class`, `encounter_count`, `avg_duration_days`, `avg_claim_cost`. |
| `encounter_trends` | `encounter_analytics` | Monthly time series: `year_month`, `encounter_count`, `total_claim_cost`. |
