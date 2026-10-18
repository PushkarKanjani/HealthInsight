# HealthInsight: Big Data Analytics Platform for Healthcare Data

> *HealthInsight is a local educational prototype for descriptive analytics over synthetic healthcare records.*

---

## 1. Project Purpose & Scope

HealthInsight is an on-premise, distributed Big Data analytics lakehouse platform engineered for descriptive analytics over large-scale synthetic longitudinal healthcare event records.

The platform extracts, cleans, transforms, manages, queries, and visualizes **12,352 synthetic patients, 321,528 clinical encounters, and 114,544 diagnosed condition events**.

### Scope
- Distributed batch ETL and schema enforcement over high-volume healthcare CSV exports.
- ACID lakehouse storage and metadata pruning via Apache Iceberg table format.
- Interactive, sub-second distributed SQL analytics via Trino.
- Operational NoSQL pre-aggregated serving store via MongoDB.
- **v2: AI-powered Clinical Command Center** — glassmorphic web portal with Gemini Text-to-SQL Copilot, JWT authentication, and Three.js fluid cursor animations.

### Non-Goals
- **No Clinical AI Diagnosis:** The Gemini Text-to-SQL engine answers analytical questions about the dataset — it does not perform clinical triage or medical decision making.
- **No Real PHI:** The system does not store or process real human medical records.
- **Not Production Software:** This is an educational engineering prototype.

---

## 2. Dataset Source & Synthetic-Data Notice

- **Source:** Generated using the open-source **MITRE Synthea** patient simulation framework (Massachusetts synthetic healthcare population).
- **Format:** High-volume normalized CSV exports (`patients.csv`, `encounters.csv`, `conditions.csv`, `organizations.csv`).
- **Notice:** All patient identities, clinical diagnoses, and billing values are purely synthetic.

---

## 3. Architecture

### v1 — Lakehouse Pipeline (COMPLETE & FROZEN)
```
Synthea CSVs
    └─► Apache Spark 3.5 (Batch ETL)
            ├─► Apache Iceberg 1.5 (ACID Lakehouse — encounter_analytics, condition_analytics)
            │       └─► Trino 435 (Distributed SQL — 321,528 rows)
            │               └─► Apache Superset 3.1 (BI Dashboard — port 8088)
            └─► MongoDB 7.0 (NoSQL Serving Layer — port 27017)
```

### v2 — AI Clinical Command Center (IN PROGRESS)
```
Browser (Three.js + Glassmorphic UI)
    └─► FastAPI Portal (port 5000, JWT Auth)
            ├─► Gemini 2.0 Flash (Text → SQL translation)
            │       └─► Trino 435 (Executes generated SQL on 321K Iceberg records)
            └─► MongoDB 7.0 (Patient lookups + KPI serving, sub-2ms)
```

### Component Roles

| Component | Architecture Role | Port |
|---|---|---|
| **Apache Spark 3.5** | Distributed Batch ETL Engine | — |
| **Apache Iceberg 1.5** | ACID Open Lakehouse Table Format | — |
| **Trino 435** | Interactive Distributed SQL (MPP) | 8080 |
| **MongoDB 7.0** | NoSQL Operational Serving Store | 27017 |
| **Apache Superset 3.1** | BI Dashboard (v1 UI) | 8088 |
| **FastAPI Portal** | AI Command Center Backend (v2) | 5000 |

> [!IMPORTANT]
> **Apache Superset is NOT one of the 4 Big Data components.** The four core Big Data components are Spark, Iceberg, Trino, and MongoDB.

---

## 4. Team Responsibilities

| Team Member | Roll No. | Primary Subsystem |
|---|---|---|
| **Pushkar Kanjani** | 23BIT153 | Trino distributed SQL, query optimization, Superset integration |
| **Hemang Shreemali** | 23BIT140 | Apache Spark ETL pipeline, joining logic, MongoDB export |
| **Sachi Shah** | 23BIT142 | Apache Iceberg schema, partitions, and metadata management |
| **Yug Thakkar** | 23BIT149 | Apache Superset dashboard, virtual datasets, UX |

---

## 5. Prerequisites & Environment Setup

### System Requirements
- **OS:** Windows 10/11 64-bit with PowerShell 5.1+ / 7+
- **Docker Desktop:** Running with WSL2 backend enabled
- **Python:** 3.10+ (tested on 3.11.9)
- **Java:** OpenJDK 17 LTS

### 1. Clone & Configure
```bash
git clone https://github.com/PushkarKanjani/HealthInsight.git
cd HealthInsight
cp .env.example .env
```

Edit `.env` and set:
```env
JAVA_HOME=C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot
HADOOP_HOME=C:\hadoop
TRINO_HOST=localhost
TRINO_PORT=8080
TRINO_CATALOG=iceberg
TRINO_SCHEMA=healthcare
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=healthinsight

# v2 AI Portal
PORTAL_JWT_SECRET=change-me-to-a-strong-random-secret
GEMINI_API_KEY=your-gemini-api-key-here
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Infrastructure Services
```bash
docker compose up -d trino mongodb superset
```

---

## 6. v1 Pipeline Execution

Run the complete, fail-fast lakehouse pipeline:

### Windows PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_pipeline.ps1
```

### Linux / macOS / Bash:
```bash
bash scripts/run_pipeline.sh
```

### Execution Order:
1. `spark/01_profile_dataset.py` — Profile source CSVs, verify schema integrity.
2. `spark/02_ingest_raw_to_iceberg.py` — Ingest raw CSVs into partitioned Iceberg lakehouse.
3. `spark/03_build_analytics_tables.py` — Build `encounter_analytics` and `condition_analytics`.
4. `spark/04_export_mongodb.py` — Aggregate metrics, populate 6 MongoDB collections.
5. `trino/queries/00_validation.sql` — Automated Trino verification queries.

---

## 7. v2 AI Portal — Clinical Command Center

> [!NOTE]
> The v2 portal layers on top of the frozen v1 infrastructure. No v1 files are modified.

### Start the Portal
```bash
# Ensure Docker services are running first (step 3 above)
python -m uvicorn portal.server:app --port 5000 --reload
```

Open in browser: **[http://localhost:5000](http://localhost:5000)**

### Default Login
```
Username: admin
Password: healthinsight2024
```

### Portal Features
| Feature | Description |
|---|---|
| 🤖 **AI Copilot** | Ask clinical questions in plain English → Gemini translates to Trino SQL → real results in <1s |
| 📊 **Chart.js Visualization** | Auto-selected bar, donut, or line charts from query results |
| 🔍 **Patient Explorer** | Instant MongoDB lookup of any synthetic patient's journey |
| 📡 **Lakehouse Monitor** | Live health status of Trino, Iceberg, MongoDB, and AI engine |
| 🔒 **JWT Authentication** | Stateless 8-hour tokens, all API routes protected |
| 💫 **Three.js Background** | GPU-accelerated liquid cursor animation at 60fps |

### Offline Fallback
The portal works without a Gemini API key. 12 clinical query templates answer common questions entirely from local Trino.

---

## 8. Interactive Verification & Querying

### A. Trino Distributed SQL (v1)
- **Host:** `localhost` | **Port:** `8080` | **Catalog:** `iceberg` | **Schema:** `healthcare`

```sql
SELECT encounter_class, COUNT(*) AS count, ROUND(AVG(total_claim_cost), 2) AS avg_cost
FROM iceberg.healthcare.encounter_analytics
GROUP BY encounter_class ORDER BY count DESC;
```

### B. MongoDB Serving Layer (v1)
```bash
mongosh mongodb://localhost:27017/healthinsight --eval "db.kpis.findOne()"
```

### C. Apache Superset Dashboard (v1)
- **URL:** [http://localhost:8088](http://localhost:8088) | **Credentials:** `admin` / `admin`

### D. AI Command Center Portal (v2)
- **URL:** [http://localhost:5000](http://localhost:5000) | **Credentials:** `admin` / `healthinsight2024`

---

## 9. Data Invariants & Quality Guarantees

1. **Two-Table Separation (Zero Cost Inflation):**
   - `iceberg.healthcare.encounter_analytics` (321,528 rows): 1 row per encounter. Financial sums 100% accurate.
   - `iceberg.healthcare.condition_analytics` (114,544 rows): 1 row per diagnosed condition event.
2. **Event-Time Relative Age Calculation:**
   - Patient age computed at encounter time (`DATEDIFF(encounter_start, patient_birthdate) / 365.25`).
3. **Dual Storage Interoperability:**
   - Windows host Spark and Linux container Trino share the same Iceberg metadata via directory junction.

---

## 10. Troubleshooting

| Problem | Fix |
|---|---|
| Trino cannot find tables | Run `CALL iceberg.system.register_table(...)` after Spark creation |
| Spark Iceberg Jar Error | Ensure `--packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.2` is set |
| Superset Trino Connection | Set URI to `trino://admin@trino:8080/iceberg/healthcare` (container hostname `trino`) |
| Portal 401 Unauthorized | JWT expired — log in again at `http://localhost:5000` |
| Gemini AI unavailable | Portal auto-switches to offline fallback engine — 12 queries still work |

---

## 11. Known Limitations

- **Synthetic Simplicity:** Synthea generates simplified clinical trajectories without ICD-10 hierarchies.
- **Local Single-Node:** Uses Docker containers on local disk, not enterprise HDFS/S3 or multi-node Trino topology.
- **v2 Offline Fallback:** Without a Gemini API key, only 12 pre-built query templates are available.
