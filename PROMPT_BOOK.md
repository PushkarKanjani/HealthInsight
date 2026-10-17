# HealthInsight Prompt Book

## Purpose
This document is the controlled instruction book for building, testing, documenting, and presenting the HealthInsight project.
Antigravity must execute the prompts in order. Do not skip a phase, silently assume missing information, fabricate results, or generate later-phase code before earlier phases are verified.

The human project owner must:
1. Run or approve each prompt.
2. Review the verification output.
3. Confirm that the phase is complete.
4. Only then continue to the next prompt.

---

## Project Identity
- **Project:** HealthInsight: Big Data Analytics Platform for Healthcare Data
- **Type:** Fourth-year undergraduate Big Data Analytics project
- **Location:** `C:\MyDrive\SEM-7\BigData\BDA_PROJECT\HealthInsight`
- **Scope:** Descriptive healthcare analytics using synthetic Synthea records.

### Explicitly excluded:
- Machine learning.
- Disease prediction.
- Diagnosis.
- Clinical recommendations.
- Risk scoring.
- Real-time streaming.
- Kafka.
- Flink.
- Snowflake.
- Cloud deployment.
- Docker orchestration.
- Kubernetes.
- Authentication.
- External APIs.
- Streamlit.

---

## Team

| Member | Roll No. | Responsibility |
|---|---|---|
| Hemang Shreemali | 23BIT140 | Spark pipeline |
| Sachi Shah | 23BIT142 | Iceberg and data layer |
| Yug Thakkar | 23BIT149 | Superset dashboard |
| Pushkar Kanjani | 23BIT153 | Trino SQL analytics |

*Every team member must understand the complete architecture.*

---

## Final Technology Stack

### Big Data components
- **Apache Spark** — distributed ETL and processing.
- **Apache Iceberg** — lakehouse table format and metadata layer.
- **Trino** — distributed SQL query engine.
- **MongoDB** — NoSQL document and aggregation store.

### UI layer
- **Apache Superset** — visualization and dashboard layer. It is not counted as one of the four Big Data components.

### Core data flow
```
Synthea CSV files 
       ↓ 
Apache Spark 
       ↓ 
Apache Iceberg raw tables 
       ↓ 
Apache Spark analytical transformations 
       ↓ 
Apache Iceberg analytical tables 
       ↓ 
Trino SQL analytics 
       ↓ 
Apache Superset dashboard 

(Apache Spark also exports aggregate results to MongoDB)
```

---

## Non-Negotiable Rules
1. Inspect actual files before writing transformations.
2. Never fabricate columns, row counts, metrics, results, or screenshots.
3. Never silently ignore an error.
4. Never use a missing source column.
5. Do not install Superset into the main PySpark environment.
6. Do not calculate encounter-level metrics from a condition-expanded join.
7. Use one row per encounter for cost, duration, encounter, and organization metrics.
8. Use condition-level rows only for condition analytics.
9. Calculate age at encounter or condition time, not using the current date.
10. Do not create optional MongoDB collections when their source fields are unavailable.
11. Keep raw input immutable.
12. Save actual versions in `docs/version_lock.md`.
13. Do not proceed to the next phase until the current phase passes verification.
14. Use absolute paths consistently for Spark and Trino warehouse configuration.
15. Treat Synthea data as synthetic and clearly label it in the dashboard and report.
16. Do not claim the project is production healthcare software.
17. Do not expose real personal health information.
18. Prefer a smaller working pipeline over a large incomplete system.

---

## Expected Project Structure
```
HealthInsight/
├── README.md
├── PROMPT_BOOK.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── data/
│   ├── raw/
│   └── sample/
│
├── iceberg/
│   ├── warehouse/
│   └── catalog/
│
├── spark/
│   ├── 01_profile_dataset.py
│   ├── 02_ingest_raw_to_iceberg.py
│   ├── 03_build_analytics_tables.py
│   └── 04_export_mongodb.py
│
├── trino/
│   ├── catalog/
│   │   └── iceberg.properties
│   └── queries/
│       ├── 01_kpis.sql
│       ├── 02_conditions.sql
│       ├── 03_demographics.sql
│       ├── 04_encounters.sql
│       └── 05_trends.sql
│
├── mongodb/
│   ├── indexes.js
│   └── validation_queries.js
│
├── superset/
│   ├── requirements-superset.txt
│   ├── connection_setup.md
│   ├── dashboard_setup.md
│   ├── dataset_queries.sql
│   └── screenshots/
│
├── scripts/
│   ├── verify_services.sh
│   ├── check_versions.sh
│   ├── run_pipeline.sh
│   └── refresh_all.sh
│
├── docs/
│   ├── dataset_dictionary.md
│   ├── architecture.md
│   ├── data_lineage.md
│   ├── version_lock.md
│   ├── demo_script.md
│   └── viva_questions.md
│
└── screenshots/
```

---

## Prompt 00 — Project Context Confirmation

### Instruction to Antigravity
Read the current project files and confirm:
1. Current directory structure.
2. Existing files.
3. Duplicate or obsolete files.
4. Whether the current filenames match this Prompt Book.
5. Whether any documents still describe HDFS, Hive, Streamlit, or a dark dashboard as the final architecture.

Do not modify code yet.

**Produce:** `docs/project_audit.md`  
Include:
- Current state.
- Required corrections.
- Files needing renaming.
- Files needing content updates.
- Missing files.
- Risks before implementation.

### Human verification
Confirm that:
- HDFS and Hive are not presented as final tools.
- Streamlit is not present as the dashboard.
- Superset is clearly UI-only.
- Spark, Iceberg, Trino, and MongoDB are the four core components.

---

## Prompt 01 — Environment and Version Audit

### Instruction to Antigravity
Ask the project owner to provide:
```powershell
$PSVersionTable
java -version
python --version
spark-submit --version
trino --version
mongod --version
mongosh --version
```
If a command is unavailable, report it as unavailable. Do not invent a version.

Check:
- Operating system.
- Java version.
- Python version.
- Spark version.
- Scala binary version if available.
- Trino version.
- MongoDB version.
- PySpark version.
- PyMongo version.
- Trino Python client version.
- Superset version.

**Create or update:** `docs/version_lock.md`

Use this table:
| Component | Installed version | Required compatibility | Status |
|---|---|---|---|
| Operating system | | | |
| Java | | | |
| Python | | | |
| Apache Spark | | | |
| Scala binary version | | | |
| Apache Iceberg runtime | | | |
| Trino | | | |
| MongoDB | | | |
| MongoDB Spark Connector | | | |
| PySpark | | | |
| PyMongo | | | |
| trino-python-client | | | |
| Apache Superset | | | |

### Stop condition
Do not proceed if the Spark, Java, Iceberg runtime, or MongoDB connector combination is unknown.

---

## Prompt 02 — Dataset Acquisition and Inspection

### Instruction to Antigravity
Inspect `data/raw/`. List all files and file sizes.  
Identify whether the following exist:
- `patients.csv`
- `encounters.csv`
- `conditions.csv`
- `organizations.csv`

Also inspect, but do not require:
- `medications.csv`
- `procedures.csv`
- `observations.csv`

Do not create assumed files.  
If files are missing, ask the project owner to place them into `data/raw/`.  
Do not generate transformation code yet.

---

## Prompt 03 — Dataset Profiler

### Instruction to Antigravity
Implement or correct `spark/01_profile_dataset.py`.  
The script must:
1. Read every relevant CSV in `data/raw/`.
2. Print the full path.
3. Print headers.
4. Print inferred Spark schema.
5. Print row count.
6. Print null count per column.
7. Display five sample rows.
8. Record actual columns and types.

**Generate:** `docs/dataset_dictionary.md`

The profiler must not:
- Join data.
- Rename source columns permanently.
- Derive analytics.
- Fabricate missing fields.
- Continue silently after a file-read error.

### Verification commands
```bash
python spark/01_profile_dataset.py
# or:
spark-submit spark/01_profile_dataset.py
```

### Human verification
Check:
- The dataset is genuinely synthetic.
- Required source columns are known.
- Unsupported analytics are marked unsupported.
- Row counts come from actual execution.
- The generated data dictionary matches the CSV headers.

---

## Prompt 04 — Analytics Support Matrix

### Instruction to Antigravity
Using only the generated dataset dictionary, create `docs/analytics_support_matrix.md`.

Use this structure:
| Analytic | Required fields | Supported? | Reason |
|---|---|---|---|
| Total patients | Patient identifier | | |
| Total encounters | Encounter identifier | | |
| Condition frequency | Condition description/code | | |
| Condition by gender | Patient gender + condition relationship | | |
| Condition by age group | Birth date + event date | | |
| Encounter count by type | Encounter type | | |
| Monthly trend | Encounter start date | | |
| Organization counts | Organization identifier/name | | |
| Average duration | Start and stop timestamps | | |
| Average cost | Cost column | | |

If a field is missing, mark the analytic as unsupported.  
Do not add fallback fabricated fields.

---

## Prompt 05 — Configuration and Dependency Files

### Instruction to Antigravity
Create or correct:
- `.env.example`
- `requirements.txt`
- `superset/requirements-superset.txt`
- `.gitignore`
- `scripts/check_versions.sh`
- `scripts/verify_services.sh`

The main `requirements.txt` must not install Apache Superset.

Use environment variables for:
- `DATA_DIR`
- `ICEBERG_WAREHOUSE`
- `MONGODB_URI`
- `MONGODB_DATABASE`
- `TRINO_HOST`
- `TRINO_PORT`
- `TRINO_CATALOG`
- `TRINO_SCHEMA`
- `SPARK_HOME`
- `ICEBERG_JAR`
- `MONGO_JAR`

Do not commit:
- `.env`
- Raw healthcare data.
- Iceberg warehouse data.
- MongoDB secrets.
- Generated logs.
- Superset metadata databases.

The `.gitignore` must include:
```
.env
__pycache__/
*.pyc
iceberg/warehouse/*
data/raw/*
*.log
superset_home/
```
Keep `.gitkeep` files if required for empty directories.

---

## Prompt 06 — Minimal Spark and Iceberg Test

### Instruction to Antigravity
Before building the full pipeline, implement a minimal test.  
The test must:
1. Start a Spark session with Iceberg support.
2. Create the healthcare catalog.
3. Create a small test Iceberg table.
4. Insert three test rows.
5. Read the table.
6. Print the result.
7. Drop the test table after successful verification.

Use the actual installed Iceberg runtime and Spark version.  
**Create:** `spark/00_test_iceberg.py`

### Verification
The command must exit with code 0.  
Expected proof:
- Iceberg catalog initialized
- Test table created
- Test rows written
- Test rows read successfully
- Test table removed

### Stop condition
Do not proceed if the minimal Spark–Iceberg test fails.

---

## Prompt 07 — Raw CSV to Iceberg Ingestion

### Instruction to Antigravity
Implement `spark/02_ingest_raw_to_iceberg.py`.  
The script must:
1. Read confirmed CSV files.
2. Normalize column names to lowercase.
3. Preserve source-to-normalized name mappings.
4. Write raw Iceberg tables.
5. Use actual schemas.
6. Avoid unsupported columns.
7. Print table names and row counts.
8. Be rerunnable without corrupting tables.

Expected tables, conditional on file availability:
- `healthcare.patients`
- `healthcare.encounters`
- `healthcare.conditions`
- `healthcare.organizations`

Do not call this data “cleaned” yet. These are raw-ingested tables.

---

## Prompt 08 — Analytical Table Construction

### Instruction to Antigravity
Implement `spark/03_build_analytics_tables.py`.

Create two analytical tables:

#### Table 1: Encounter analytics (`healthcare.encounter_analytics`)
It must contain exactly one row per encounter.  
Use it for:
- Encounter count.
- Encounter type.
- Duration.
- Cost.
- Organization.
- Monthly trends.
- Patient-level encounter metrics.

#### Table 2: Condition analytics (`healthcare.condition_analytics`)
It may contain multiple rows per encounter.  
Use it for:
- Condition frequency.
- Condition by gender.
- Condition by age group.
- Condition and demographic analysis.

### Required rules
- Join patients to encounters using confirmed identifiers.
- Join organizations only when organization fields exist.
- Join conditions separately.
- Use event-time age.
- Do not use `current_date()` for age.
- Parse dates safely.
- Convert numeric cost fields only when confirmed.
- Handle nulls without fabricating replacements.
- Print row counts before and after joins.
- Print duplicate checks.
- Print final schemas.

### Verification
- For `encounter_analytics`: `COUNT(*)` must equal `COUNT(DISTINCT encounter_id)`. If not, stop and fix the join.
- For `condition_analytics`: multiple rows per encounter are allowed.
- Document this difference in `docs/data_lineage.md`.

---

## Prompt 09 — Trino Configuration and Validation

### Instruction to Antigravity
Configure `trino/catalog/iceberg.properties`.  
The Trino warehouse path must exactly match the Spark Iceberg warehouse path.  
Verify the correct Trino property names for the installed version. Do not assume that properties from another Trino release are valid.

Create validation instructions: `trino/queries/00_validation.sql`  
Include:
```sql
SHOW CATALOGS;
SHOW SCHEMAS FROM iceberg;
SHOW TABLES FROM iceberg.healthcare;
SELECT COUNT(*) FROM iceberg.healthcare.encounter_analytics;
SELECT COUNT(*) FROM iceberg.healthcare.condition_analytics;
```

### Stop condition
Stop if Trino cannot see tables created by Spark.

---

## Prompt 10 — Trino Analytics Queries

### Instruction to Antigravity
Create or correct:
- `trino/queries/01_kpis.sql`
- `trino/queries/02_conditions.sql`
- `trino/queries/03_demographics.sql`
- `trino/queries/04_encounters.sql`
- `trino/queries/05_trends.sql`

Use the correct table for each metric:
- **KPIs:** Use `encounter_analytics` for distinct patients, total encounters, average duration, average cost, total cost.
- **Conditions:** Use `condition_analytics` for condition frequency, condition by gender, condition by age group.
- **Demographics:** Avoid counting condition rows as patients. Use distinct patient counts where appropriate.
- **Encounters:** Use `encounter_analytics` for encounter type, average duration by type, organization counts, cost by type.
- **Trends:** Use `encounter_analytics` for monthly trends.

Every query must be executable against actual columns.

---

## Prompt 11 — MongoDB Export

### Instruction to Antigravity
Implement `spark/04_export_mongodb.py`.  
Export real aggregate results.

- **Required collections when supported:** `kpis`, `condition_summary`, `encounter_type_summary`, `encounter_trends`
- **Optional collections:** `demographic_summary`, `organization_summary`

Rules:
- Use `encounter_analytics` for encounter-level metrics.
- Use `condition_analytics` for condition-level metrics.
- Every document must include: `generated_at`, `source_table`.
- Do not use example values from documentation as real data.

Create or correct:
- `mongodb/indexes.js`
- `mongodb/validation_queries.js`

### Verification
Verify in mongosh:
```javascript
show dbs
use healthinsight
show collections
db.kpis.findOne()
db.condition_summary.find().limit(3)
db.encounter_type_summary.find().limit(3)
db.encounter_trends.find().limit(3)
```
Record actual collection counts in `docs/mongodb_verification.md`.

---

## Prompt 12 — Superset Connection

### Instruction to Antigravity
Do not install Superset into the main project Python environment.  
Use `superset/requirements-superset.txt`.

Configure Superset to connect to Trino.  
The connection pattern is:
```
trino://USERNAME@HOST:PORT/CATALOG
```
The exact URI must match the installed Trino and Superset configuration.

Verify:
1. Superset starts.
2. Trino connection test succeeds.
3. `healthcare` schema is visible.
4. `encounter_analytics` is visible.
5. `condition_analytics` is visible.
6. A test chart returns actual data.

Superset requires the Trino driver and SQLAlchemy integration for the connection.  
Create `superset/connection_setup.md` with the actual commands used.

---

## Prompt 13 — Superset Dashboard

### Instruction to Antigravity
Create the dashboard: **HealthInsight Healthcare Analytics**  
Use a clinical light visual system:
- Background: `#F8FAFC`
- Card: `#FFFFFF`
- Primary blue: `#0072CE`
- Teal: `#0D9488`
- Indigo: `#4F46E5`
- Primary text: `#0F172A`
- Secondary text: `#475569`
- Border: `#E2E8F0`

### Dashboard sections:
1. Overview.
2. Conditions.
3. Demographics.
4. Encounters.
5. Organizations.
6. Trends.
7. Data Lineage.

### Rules:
- Use only actual data.
- Do not display unsupported metrics.
- Label costs as synthetic recorded costs.
- Display a visible note: “Synthetic data — descriptive analytics only.”
- Avoid 3D charts.
- Avoid medical alerts.
- Avoid diagnosis language.
- Use accessible text contrast.
- Use charts that match the data type.

---

## Prompt 14 — UI Quality Review

### Instruction to Antigravity
Review the Superset dashboard for:
- Clinical light theme consistency.
- Readability.
- Correct labels.
- No dark theme remnants.
- No fake values.
- No unsupported charts.
- Correct filters.
- Correct chart titles.
- Visible synthetic-data disclaimer.
- Proper spacing.
- No unnecessary visual effects.

**Create:** `docs/ui_review.md`  
Include:
- Passed checks.
- Failed checks.
- Corrections made.
- Remaining limitations.

---

## Prompt 15 — Full Pipeline Script

### Instruction to Antigravity
Create or correct `scripts/run_pipeline.sh` and `scripts/refresh_all.sh`.  
The pipeline order must be:
1. Profile source data
2. Ingest raw CSV files into Iceberg
3. Build encounter and condition analytical tables
4. Export MongoDB aggregates
5. Verify Trino visibility
6. Print completion status

Use fail-fast behavior:
```bash
set -euo pipefail
```
The pipeline must stop when any stage fails. Do not allow a failed stage to produce a success message.  
For Windows, also provide `scripts/run_pipeline.ps1` with equivalent behavior.

---

## Prompt 16 — End-to-End Verification

### Instruction to Antigravity
Run the entire project from a clean terminal.  
Verify:
- Source files exist.
- Spark profiler succeeds.
- Raw Iceberg tables exist.
- Analytical Iceberg tables exist.
- Encounter analytics has one row per encounter.
- Condition analytics has valid condition relationships.
- Trino can query all required tables.
- MongoDB contains real aggregate documents.
- Superset connects to Trino.
- Dashboard charts load.
- No fabricated outputs exist.
- README commands work.

**Create:** `docs/end_to_end_verification.md`  
Use this table:
| Check | Command or evidence | Result | Status |
|---|---|---|---|
| Dataset present | | | |
| Spark profiler | | | |
| Raw Iceberg tables | | | |
| Encounter analytics | | | |
| Condition analytics | | | |
| Trino queries | | | |
| MongoDB export | | | |
| Superset connection | | | |
| Dashboard charts | | | |
| Full refresh | | | |

---

## Prompt 17 — Documentation

### Instruction to Antigravity
Update:
- `README.md`
- `docs/architecture.md`
- `docs/data_lineage.md`
- `docs/version_lock.md`
- `docs/demo_script.md`
- `docs/viva_questions.md`

README must include:
- Project purpose.
- Scope.
- Non-goals.
- Dataset source and synthetic-data notice.
- Component roles.
- Architecture.
- Installation.
- Environment variables.
- Pipeline commands.
- Verification commands.
- Troubleshooting.
- Known limitations.
- Team responsibilities.

Do not state that the system is production clinical software.  
Use the wording:
> *HealthInsight is a local educational prototype for descriptive analytics over synthetic healthcare records.*

---

## Prompt 18 — Screenshot Checklist

### Instruction to Antigravity
Create a checklist in `docs/screenshot_checklist.md`.  
Required screenshots:
- Project folder structure.
- Dataset profiler output.
- Spark version.
- Iceberg test success.
- Iceberg table listing.
- Spark analytical table schema.
- Trino table listing.
- Trino KPI query result.
- Trino condition query result.
- MongoDB collection listing.
- MongoDB document example.
- Superset Trino connection success.
- Overview dashboard.
- Conditions dashboard.
- Demographics dashboard.
- Trends dashboard.
- Data lineage section.

Every screenshot must show real output from the project.

---

## Prompt 19 — Five-Minute Demonstration

### Instruction to Antigravity
Create `docs/demo_script.md`.

Use this order:
- **Minute 1 — Problem and scope:** Explain healthcare CSV files are difficult to analyse manually. Synthea is synthetic. The system is descriptive only.
- **Minute 2 — Spark and Iceberg:** Show profiling, raw Iceberg tables, analytical tables, one row per encounter rule.
- **Minute 3 — Trino:** Run `SELECT COUNT(*) FROM iceberg.healthcare.encounter_analytics;` then show one condition and one trend query.
- **Minute 4 — MongoDB:** Show `show collections` and `db.kpis.findOne()`. Explain that Spark generated the documents.
- **Minute 5 — Superset:** Show dashboard, filters, charts, data lineage, synthetic-data notice.

*Do not spend the entire demonstration on UI styling. The data pipeline is the project.*

---

## Prompt 20 — Viva Preparation

### Instruction to Antigravity
Create at least 25 viva questions and accurate answers in `docs/viva_questions.md`.  
Must include:
1. Why Spark?
2. Why Iceberg?
3. Why Trino?
4. Why MongoDB?
5. Why Superset?
6. Why not HDFS?
7. Why not Hive?
8. Why not Snowflake?
9. Difference between Spark and Trino.
10. Difference between Iceberg and Parquet.
11. Why two analytical tables?
12. How was many-to-many inflation avoided?
13. How is age calculated?
14. How are missing columns handled?
15. How is MongoDB populated?
16. What is the data lineage?
17. Is this real patient data?
18. Is this an AI system?
19. What are the limitations?
20. What would be future scope?
21. What happens if MongoDB is unavailable?
22. What happens if Trino cannot see Iceberg?
23. How are costs interpreted?
24. How is reproducibility maintained?
25. What is the role of Superset?

All answers must match the actual implemented project.

---

## Prompt 21 — Final Technical Audit

### Instruction to Antigravity
Perform a final audit.  
Check every statement in:
- `README.md`
- `DOC1_PRD_TECHSTACK_ARCHITECTURE.md`
- `DOC2_TRD_DB_PIPELINE.md`
- `DOC3_UI_BRIEF_DEMO_VIVA.md`

Correct contradictions such as:
- HDFS listed as a required component.
- Hive listed as the SQL layer.
- Streamlit listed as the UI.
- Superset counted as a Big Data component.
- Dark dashboard colors.
- Fixed fabricated row counts.
- Six MongoDB collections guaranteed despite optional fields.
- One joined table being used for all metrics.
- Age calculated from the current date.
- Incorrect or unverified version claims.
- Apache Superset installed in the main requirements file.

**Create:** `docs/final_audit.md`  
Include:
- Contradictions found.
- Corrections made.
- Unresolved risks.
- Final run status.
- Final demo readiness.

---

## Prompt 22 — Freeze and Handover

### Instruction to Antigravity
Do not add new features.  
Freeze the project after:
- Full pipeline passes.
- Trino queries pass.
- MongoDB verification passes.
- Superset dashboard loads.
- Documentation is complete.
- Screenshots are captured.
- Demo script is tested.

**Create:** `docs/final_handover.md`  
Include:
- Final architecture.
- Installed versions.
- Start commands.
- Pipeline command.
- Dashboard URL.
- Known limitations.
- Team contributions.
- Exact evidence files.
- Final viva wording.

*The final project must remain simple, reproducible, and explainable.*

---

## Human Verification Protocol

After every prompt, the project owner must ask Antigravity:
1. What did you change?
2. What command proves it works?
3. What was the actual output?
4. What limitations remain?
5. Is the phase ready for approval?

*The owner should not approve a phase based only on file creation. A file existing does not prove that its code works.*

---

## Definition of “Complete”

HealthInsight is complete only when all of the following are true:
1. Actual Synthea files were inspected.
2. Dataset columns are documented.
3. Actual versions are recorded.
4. Spark profiling succeeds.
5. Spark writes Iceberg tables.
6. Trino reads those Iceberg tables.
7. Encounter-level and condition-level analytics are separated.
8. MongoDB receives real aggregate documents.
9. Superset connects to Trino.
10. Dashboard charts load from actual data.
11. The full pipeline can be rerun.
12. The README is accurate.
13. Screenshots show real execution.
14. Each team member can explain the full data flow.
15. No unsupported medical or AI claims appear anywhere.

---

## Current Next Prompt
Run **Prompt 00 — Project Context Confirmation** first.  
Do not ask Antigravity to build additional features until the audit is complete.
