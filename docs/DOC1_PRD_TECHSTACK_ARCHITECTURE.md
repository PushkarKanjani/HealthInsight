# HealthInsight — Document 1 of 3
## Product Requirements · Technology Stack · System Architecture

> **Project:** HealthInsight: Big Data Analytics Platform for Healthcare Data
> **Type:** Fourth-year Undergraduate Big Data Project (BDA)
> **Date:** October 2026
> **Scope:** Descriptive healthcare analytics only — no diagnosis, prediction, ML, or clinical recommendations.
> **Dataset:** Synthea synthetic patient records — not real patient data.

---

## 1. Team

| Name | Roll No. | Responsibility |
|---|---|---|
| Hemang Shreemali | 23BIT140 | Spark pipeline lead |
| Sachi Shah | 23BIT142 | Iceberg and data layer |
| Yug Thakkar | 23BIT149 | Superset dashboard |
| Pushkar Kanjani | 23BIT153 | Trino SQL analytics |

---

## 2. Product Requirements Document (PRD)

### 2.1 What the Application Does

HealthInsight answers descriptive questions about synthetic healthcare records:

- How many patients and encounters are recorded?
- Which conditions occur most frequently?
- How do conditions vary by age group or gender?
- Which encounter types are most common?
- How do encounters change over time?
- Which organizations have the most encounters?
- What are the average recorded durations and costs?

### 2.2 What the Application Does NOT Do

- Diagnose conditions or diseases.
- Predict future outcomes or risk scores.
- Make clinical recommendations.
- Process real patient data.
- Provide ML or AI features.

> **Viva answer:** "HealthInsight is a lightweight educational healthcare data analytics platform that demonstrates an end-to-end Big Data pipeline using synthetic healthcare records."

### 2.3 Non-Goals (Explicitly Excluded)

- ML, classification, regression, clustering, or risk scoring.
- Real-time streaming (Kafka, Flink).
- Cloud deployment (AWS, GCP, Azure, Snowflake, Databricks).
- Docker orchestration or Kubernetes.
- Authentication or authorization systems.
- External APIs or microservices.
- Streamlit.
- HDFS (unless faculty explicitly requires it).
- Hive (replaced by Trino for SQL analytics).
- Any fabricated or assumed data.

### 2.4 Success Criteria

| Criterion | How to Verify |
|---|---|
| Spark pipeline runs without errors | All 4 scripts exit with code 0 |
| Iceberg raw tables created | `SHOW TABLES IN healthcare` in Trino |
| `encounter_analytics` has 1 row per encounter | `COUNT(*) = COUNT(DISTINCT encounter_id)` |
| `condition_analytics` is separate | Separate row count from encounter_analytics |
| Trino SQL executes against Iceberg | 5 query files return real results |
| MongoDB has >=4 required collections | Visible in mongosh/Compass |
| Superset dashboard live on Trino | Charts render from real data |
| End-to-end demo reproducible from README | Single script triggers full pipeline |

### 2.5 Dataset

**Source:** Synthea Synthetic Patient Generator (open-source).

**Primary files (inspect before coding):**
- `patients.csv`
- `encounters.csv`
- `conditions.csv`
- `organizations.csv`

**Optional (inspect if present, do not assume):**
- `medications.csv`, `procedures.csv`, `observations.csv`

**Hard rule:** Run `01_profile_dataset.py` first. Confirm every column name before writing any transformation code. Document findings in `docs/dataset_dictionary.md`.

### 2.6 Supported Analytics (Conditional on Source Columns)

| Analytic | Source Table | Required Columns |
|---|---|---|
| Total distinct patients | encounter_analytics | patient_id |
| Total encounters | encounter_analytics | encounter_id |
| Avg encounter duration | encounter_analytics | encounter_start, encounter_stop |
| Avg / total recorded cost | encounter_analytics | base_cost or total_claim_cost |
| Encounter count by type | encounter_analytics | encounter_type |
| Monthly encounter trend | encounter_analytics | encounter_start |
| Organization encounter counts | encounter_analytics | organization_id, organization_name |
| Condition frequency | condition_analytics | condition_description |
| Condition by gender | condition_analytics | gender, condition_description |
| Condition by age group | condition_analytics | age_group, condition_description |

**Rule:** If a column does not exist in the real file, remove the analytic — do not fabricate it.

---

## 3. Technology Stack

### 3.1 The Four Big Data Components

```
+----------------+-----------------+--------------+-----------------+
| Apache Spark   | Apache Iceberg  |    Trino     |    MongoDB      |
| Distributed    | Open Lakehouse  | Distributed  | NoSQL Document  |
| ETL Engine     | Table Format    | SQL Engine   | & Agg. Store    |
+----------------+-----------------+--------------+-----------------+
                         UI Layer (not a Big Data component)
                       +--------------------------+
                       |     Apache Superset      |
                       |  BI Dashboard & Charts   |
                       +--------------------------+
```

### 3.2 Accurate Component Roles

| Component | Accurate Role | What It Is NOT |
|---|---|---|
| **Apache Spark** | Distributed ETL and processing engine | Not a storage system |
| **Apache Iceberg** | Open lakehouse table format and metadata layer | Not an execution engine or database |
| **Trino** | Distributed SQL query engine | Not a storage system |
| **MongoDB** | NoSQL document and aggregation store | Not automatically distributed unless configured as replica set/sharded |
| **Apache Superset** | BI dashboard and visualization UI only | Not a Big Data component |

> **Critical wording:** Iceberg is a **table format**, not a processing engine. Spark and Trino read and write Iceberg tables through their respective integrations. Iceberg manages the metadata, schema, and Parquet data files — it does not execute queries.

### 3.3 Why These Tools

| Alternative | Why Not Used |
|---|---|
| HDFS | Adds NameNode/DataNode setup complexity; Iceberg provides lakehouse management without a Hadoop cluster |
| Hive | Adds Metastore config; Trino gives a cleaner SQL-analytics separation |
| Snowflake | Requires cloud account and billing; not locally reproducible |
| Databricks | Bundles too many services; hides individual component roles |
| Delta Lake | Valid alternative, but tied to Databricks ecosystem; Iceberg integrates cleanly with Spark and Trino without vendor lock-in |
| Streamlit | Not a BI tool; Superset is the correct choice |
| PostgreSQL/MySQL | Relational databases, not lakehouse or distributed SQL architecture |

### 3.4 Compatibility Matrix (Target — Verify Before Installing)

> Record actual installed versions in `docs/version_lock.md`.

| Component | Target | Notes |
|---|---|---|
| Java | 17 LTS | Required by Spark 3.5.x and Trino |
| Python | 3.10+ | For PySpark scripts |
| Scala binary | 2.12 | Required by Spark 3.5.x |
| Apache Spark | 3.5.x | Latest stable 3.x |
| Iceberg Runtime JAR | iceberg-spark-runtime-3.5_2.12:1.8.1 | Must match Spark minor version AND Scala binary |
| Trino | 435+ | Stable release with Iceberg connector |
| MongoDB | 7.0+ Community Edition | Latest stable |
| MongoDB Spark Connector | mongo-spark-connector_2.12:10.4.0 | Must match Spark 3.5 and Scala 2.12 |
| Apache Superset | 3.1.x or 4.x | Installed in its own separate Python env |
| trino-python-client | 0.336.0+ | Installed in Superset env only |

### 3.5 Python Dependencies — Two Separate Environments

#### `requirements.txt` — Pipeline dependencies only

```
# Pipeline and Spark dependencies
# Do NOT mix with Superset — dependency conflicts will occur
pyspark==3.5.3
pymongo==4.10.1
trino==0.336.0
pandas==2.2.3
pyarrow==17.0.0
python-dotenv==1.0.1
```

> Update pin numbers from actual installation. Record in `docs/version_lock.md`.

#### `superset/requirements-superset.txt` — Superset (separate env)

```
apache-superset
trino
```

> Superset MUST be installed in its own virtual environment.

### 3.6 JAR Files

```
iceberg-spark-runtime-3.5_2.12-1.8.1.jar
mongo-spark-connector_2.12-10.4.0.jar
```

Pass via `spark-submit --jars`:

```bash
spark-submit \
  --jars "$ICEBERG_JAR,$MONGO_JAR" \
  spark/03_build_analytics_tables.py
```

Do not use `.config("spark.jars", ...)` inside individual scripts — fragile and path-sensitive.

---

## 4. System Architecture

### 4.1 Full Data Flow

```
Synthea CSV files (data/raw/)
         |
         v
[Apache Spark] 01_profile_dataset.py
  - Print file names, headers, schemas
  - Print row counts, null counts
  - Print 5 sample rows per file
  -> docs/dataset_dictionary.md
         |
  STOP HERE — confirm columns before proceeding
         |
         v
[Apache Spark] 02_ingest_raw_to_iceberg.py
  - Normalize column names to lowercase
  - Write Iceberg raw tables:
    healthcare.patients
    healthcare.encounters
    healthcare.conditions
    healthcare.organizations
         |
         v
[Apache Spark] 03_build_analytics_tables.py
  |
  +-- Path A — encounter_analytics:
  |   patients + encounters + organizations
  |   -> 1 row per encounter
  |   -> age_at_encounter (relative to encounter_start)
  |   -> encounter_duration_days
  |   -> costs (if columns exist)
  |
  +-- Path B — condition_analytics:
      conditions + patients + encounters
      -> 1 row per encounter-condition pair
      -> age_at_condition (relative to condition_start)
      -> demographic context
         |
         v
[Apache Iceberg] iceberg/warehouse/healthcare.db/
  - patients/
  - encounters/
  - conditions/
  - organizations/
  - encounter_analytics/   <- 1 row per encounter
  - condition_analytics/   <- 1 row per enc-cond pair
         |
    +----+----+
    |         |
    v         v
[Spark]    [Trino]
04_export  - Reads Iceberg via catalog
_mongodb   - 01_kpis.sql
           - 02_conditions.sql
           - 03_demographics.sql
           - 04_encounters.sql
           - 05_trends.sql
    |          |
    v          v
[MongoDB]  [Superset]
healthin-  Connected to Trino
sight DB   HealthInsight Dashboard
```

### 4.2 The Two-Table Rule

> The most important architectural decision. Wrong joins inflate encounter counts and costs.

```
WRONG — single joined table:
  patients + encounters + conditions
  = many rows per encounter (one per condition)
  = COUNT(encounters) is inflated
  = SUM(cost) is inflated

CORRECT — two separate tables:

  encounter_analytics:
    patients + encounters + organizations
    -> exactly 1 row per encounter
    -> used for: encounter counts, costs, duration,
                 org totals, time trends

  condition_analytics:
    conditions + patients + encounters
    -> 1 row per (encounter, condition) pair
    -> used for: condition frequency,
                 condition-by-demographic
    -> NEVER used for cost or encounter-count aggregation
```

### 4.3 Iceberg Warehouse Layout

```
iceberg/warehouse/
+-- healthcare.db/
    +-- patients/
    +-- encounters/
    +-- conditions/
    +-- organizations/
    +-- encounter_analytics/
    +-- condition_analytics/
```

> Internal subdirectory structure (Parquet files, metadata JSON) is managed by Iceberg and varies by version. Do not document exact internal paths as a contract.

### 4.4 Spark Session Config (Iceberg)

```python
spark = SparkSession.builder \
    .appName("HealthInsight") \
    .config("spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.healthcare",
            "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.healthcare.type", "hadoop") \
    .config("spark.sql.catalog.healthcare.warehouse",
            os.getenv("ICEBERG_WAREHOUSE")) \
    .getOrCreate()
```

### 4.5 Trino Iceberg Catalog

```properties
connector.name=iceberg
iceberg.catalog.type=hadoop
iceberg.catalog.warehouse=/absolute/path/to/HealthInsight/iceberg/warehouse
```

> Warehouse path must match the value set in Spark.

### 4.6 Superset → Trino Connection

```
SQLAlchemy URI: trino://admin@localhost:8080/iceberg
```

> Username and authentication depend on your Trino server config. Requires `trino` package in Superset env.

---

## 5. Environment Variables (`.env.example`)

```bash
DATA_DIR=/absolute/path/to/HealthInsight/data/raw
ICEBERG_WAREHOUSE=/absolute/path/to/HealthInsight/iceberg/warehouse
ICEBERG_JAR=/absolute/path/to/lib/iceberg-spark-runtime-3.5_2.12-1.8.1.jar
MONGO_JAR=/absolute/path/to/lib/mongo-spark-connector_2.12-10.4.0.jar
TRINO_HOST=localhost
TRINO_PORT=8080
TRINO_CATALOG=iceberg
TRINO_SCHEMA=healthcare
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=healthinsight
SPARK_HOME=/path/to/spark-3.5.x-bin-hadoop3
JAVA_HOME=/path/to/java17
```

---

## 6. Project Structure

```
HealthInsight/
+-- README.md
+-- requirements.txt              <- pipeline deps only
+-- .env.example
+-- .gitignore
+-- data/raw/                     <- Synthea CSVs
+-- iceberg/warehouse/            <- managed by Iceberg
+-- spark/
|   +-- 01_profile_dataset.py
|   +-- 02_ingest_raw_to_iceberg.py
|   +-- 03_build_analytics_tables.py
|   +-- 04_export_mongodb.py
+-- trino/
|   +-- catalog/iceberg.properties
|   +-- queries/(01-05).sql
+-- mongodb/
|   +-- indexes.js
|   +-- validation_queries.js
+-- superset/
|   +-- requirements-superset.txt <- separate env
|   +-- connection_setup.md
|   +-- dashboard_setup.md
|   +-- dataset_queries.sql
+-- scripts/
|   +-- verify_services.sh
|   +-- run_pipeline.sh
|   +-- check_versions.sh
+-- docs/
|   +-- dataset_dictionary.md    <- Phase 1 output
|   +-- architecture.md
|   +-- data_lineage.md
|   +-- version_lock.md          <- fill after install
|   +-- demo_script.md
|   +-- viva_questions.md
+-- screenshots/
```

---

## 7. Phase Plan

| Phase | Focus | Key Output | Stop If |
|---|---|---|---|
| 1 | Dataset inspection | `dataset_dictionary.md` | Missing CSVs or unreadable headers |
| 2 | Env + verification | `.env`, all services pass | Any service fails |
| 3 | Spark + Iceberg test | One table created, readable via Trino | Table creation fails |
| 4 | Ingestion + analytics | `encounter_analytics`, `condition_analytics` | Wrong row counts |
| 5 | Trino SQL | 5 query files with real results | Trino cannot reach warehouse |
| 6 | MongoDB export | >=4 required collections | MongoDB unreachable |
| 7 | Superset dashboard | Charts rendering from Trino | Cannot connect |
| 8 | Docs + viva | README, demo, Q&A, screenshots | — |

---

## 8. Hard Rules

1. Never fabricate row counts, column names, metrics, or results.
2. Never use Snowflake — local Iceberg warehouse only.
3. Never count Superset as one of the four Big Data components.
4. Never install Superset in the main PySpark virtual environment.
5. Never use Streamlit.
6. Never calculate costs from `condition_analytics` — use `encounter_analytics` only.
7. Never use `current_date()` for age — use the event date.
8. Stop on failure — capture the full error, resolve before continuing.
9. Prefer a small working pipeline over an ambitious incomplete one.
10. Describe Iceberg accurately — it is an open table format, not a processing engine.
