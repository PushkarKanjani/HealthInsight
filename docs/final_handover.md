# HealthInsight — Final Project Handover & Freeze Record (Prompt 22)

**Handover Date:** October 18, 2026  
**Project State:** **FROZEN (Implementation Complete)**  
**Version:** 1.0.0-final  

---

## 1. Final Architecture

HealthInsight implements a 4-tier decoupled Big Data Lakehouse architecture:

```
[Synthea CSV Tier] (12,352 patients, 321,528 encounters, 114,544 conditions, 5,499 orgs)
         │
         ▼
[1. Apache Spark 3.5] (Batch Distributed ETL, Schema Enforcement, Age Derivation, Cost Integrity)
         ├──► [2. Apache Iceberg 1.5] (Lakehouse Storage Format, Parquet + Metadata Pruning)
         │           │
         │           ▼
         │    [3. Trino 435] (Distributed Interactive SQL Engine, Sub-Second OLAP)
         │           │
         │           ▼
         │    [Apache Superset 3.1] (Presentation BI UI: Clinical Daylight Dashboard)
         │
         └──► [4. MongoDB 7.0] (NoSQL Operational Serving Store: 6 Pre-Aggregated Collections)
```

---

## 2. Verified Installed Versions

- **Host OS:** Windows 11 Home Single Language (Build 26100)
- **Container Runtime:** Docker Desktop (WSL2 Backend)
- **Python:** 3.11.9
- **Apache Spark:** 3.5.3 (PySpark 3.5.3)
- **Apache Iceberg:** 1.5.2 (`iceberg-spark-runtime-3.5_2.12:1.5.2`)
- **Trino:** 435 (Docker image `trinodb/trino:435`)
- **MongoDB:** 7.0 Community (Docker image `mongo:7.0`)
- **Apache Superset:** 3.1.0 with `trino-0.340.0` (Docker image `healthinsight-superset:latest`)

---

## 3. Quick Start & Execution Commands

### Step 1: Start Container Services
```bash
docker compose up -d trino mongodb superset
```

### Step 2: Run Automated End-to-End Pipeline
On Windows PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_pipeline.ps1
```
On Linux / macOS:
```bash
bash scripts/run_pipeline.sh
```

### Step 3: Interactive Verification Interfaces
- **Apache Superset Dashboard:** [http://localhost:8088](http://localhost:8088) (Username: `admin` | Password: `admin`)
- **Trino Distributed SQL:** Connect via DBeaver Community or Trino CLI at `localhost:8080` (Catalog: `iceberg`, Schema: `healthcare`, User: `admin`).
- **MongoDB NoSQL Shell:** `mongosh mongodb://localhost:27017/healthinsight`

---

## 4. Key Evidence & Documentation Index

| Documentation / Artifact | Description | File Link |
|---|---|---|
| **System Architecture** | Full architectural blueprints and component breakdowns | [docs/architecture.md](file:///c:/MyDrive/SEM-7/BigData/BDA_PROJECT/HealthInsight/docs/architecture.md) |
| **Data Lineage** | Ingestion-to-visualization field and transformation tracking | [docs/data_lineage.md](file:///c:/MyDrive/SEM-7/BigData/BDA_PROJECT/HealthInsight/docs/data_lineage.md) |
| **Dataset Dictionary** | Profiled column types, null counts, and value distributions | [docs/dataset_dictionary.md](file:///c:/MyDrive/SEM-7/BigData/BDA_PROJECT/HealthInsight/docs/dataset_dictionary.md) |
| **Version Lock** | Pinned runtime dependencies and JAR compatibility table | [docs/version_lock.md](file:///c:/MyDrive/SEM-7/BigData/BDA_PROJECT/HealthInsight/docs/version_lock.md) |
| **End-to-End Verification** | Proof matrix of 10 verification checks across all tiers | [docs/end_to_end_verification.md](file:///c:/MyDrive/SEM-7/BigData/BDA_PROJECT/HealthInsight/docs/end_to_end_verification.md) |
| **Screenshot Checklist** | Step-by-step checklist of 17 viva presentation screenshots | [docs/screenshot_checklist.md](file:///c:/MyDrive/SEM-7/BigData/BDA_PROJECT/HealthInsight/docs/screenshot_checklist.md) |
| **5-Minute Demo Script** | Timed presentation script for the viva panel | [docs/demo_script.md](file:///c:/MyDrive/SEM-7/BigData/BDA_PROJECT/HealthInsight/docs/demo_script.md) |
| **Viva Questions (25 Q&A)** | Master oral defense questions and comprehensive answers | [docs/viva_questions.md](file:///c:/MyDrive/SEM-7/BigData/BDA_PROJECT/HealthInsight/docs/viva_questions.md) |
| **Final Technical Audit** | Architectural consistency and anti-pattern clearance record | [docs/final_audit.md](file:///c:/MyDrive/SEM-7/BigData/BDA_PROJECT/HealthInsight/docs/final_audit.md) |

---

## 5. Team Contributions & Subsystem Ownership

- **Pushkar Kanjani (23BIT153):** Trino distributed SQL query architecture, query optimization, DBeaver validation, and Superset database connector integration.
- **Hemang Shreemali (23BIT140):** Apache Spark distributed ETL pipeline, deduplication joins, and MongoDB pre-aggregated document export.
- **Sachi Shah (23BIT142):** Apache Iceberg lakehouse schema definitions, partition specifications, table registration, and storage path alignment.
- **Yug Thakkar (23BIT149):** Apache Superset clinical daylight dashboard, virtual datasets, charts layout, and presentation layer.

---

## 6. Official Viva Disclaimer & Final Framing

When opening the presentation, the team must use the exact standardized wording:

> *"HealthInsight is a local educational prototype for descriptive analytics over synthetic healthcare records."*

All technical and architectural questions must be answered according to the principles documented in [docs/viva_questions.md](file:///c:/MyDrive/SEM-7/BigData/BDA_PROJECT/HealthInsight/docs/viva_questions.md).
