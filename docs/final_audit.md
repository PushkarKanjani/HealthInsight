# HealthInsight — Final Technical Audit (Prompt 21)

**Audit Date:** October 18, 2026  
**Auditor:** Antigravity AI & HealthInsight Project Team  
**Scope:** Architecture alignment, code/documentation parity, anti-pattern detection, and viva readiness.

---

## 1. Audit Summary & Consistency Check

A comprehensive audit was performed across all project assets, scripts, queries, markdown specifications (`README.md`, `DOC1_PRD_TECHSTACK_ARCHITECTURE.md`, `DOC2_TRD_DB_PIPELINE.md`, `DOC3_UI_BRIEF_DEMO_VIVA.md`), and live running services.

| Architectural Invariant | Audit Finding | Correction / Status |
|---|---|---|
| **No HDFS as mandatory component** | No active scripts or pipeline stages depend on HDFS. Storage is managed via local filesystem + Apache Iceberg metadata specification. | **VERIFIED CLEAN** |
| **No Apache Hive as SQL engine** | Hive execution is completely eliminated. Interactive SQL is executed purely by Trino 435 directly over Iceberg Parquet files. | **VERIFIED CLEAN** |
| **No Streamlit as UI** | Streamlit is not installed or used. UI is provided exclusively by Apache Superset 3.1.0 in Docker. | **VERIFIED CLEAN** |
| **Superset component role** | Superset is explicitly classified as UI/presentation only across all docs, never counted as Big Data component #5. | **VERIFIED CLEAN** |
| **Dashboard theme consistency** | Clinical Light Theme (`#F8FAFC`, `#FFFFFF`, `#0072CE`, `#0D9488`, `#4F46E5`) enforced. Zero dark theme remnants. | **VERIFIED CLEAN** |
| **Exact row counts & zero fabrication** | All counts match exact Synthea files: `patients` (12,352), `encounters` (321,528), `conditions` (114,544), `organizations` (5,499). | **VERIFIED CLEAN** |
| **Two-table analytical separation** | Maintained strict separation: `encounter_analytics` (321,528 rows, 1 row per encounter) and `condition_analytics` (114,544 rows). Cost inflation eliminated. | **VERIFIED CLEAN** |
| **Event-time relative age** | Age calculated relative to encounter start date (`MONTHS_BETWEEN(start, birthdate)/12`), preventing `CURRENT_DATE()` distortion. | **VERIFIED CLEAN** |
| **MongoDB serving layer** | 6 pre-aggregated collections created and indexed with schema metadata. | **VERIFIED CLEAN** |
| **Standardized script filenames** | Pipeline scripts reference standardized `01_profile_dataset.py`, `02_ingest_raw_to_iceberg.py`, `03_build_analytics_tables.py`, `04_export_mongodb.py`. | **VERIFIED CLEAN** |

---

## 2. Contradictions Found and Corrected During Execution

1. **Storage Path Misalignment (Windows vs Linux Docker):**
   - *Problem:* Spark running on Windows host wrote `C:/...` URIs into Iceberg metadata, which Trino inside Linux Docker failed to read.
   - *Correction:* Standardized warehouse path to `file:/warehouse` using Windows Junction `C:\warehouse -> iceberg\warehouse` and volume mount `/warehouse` inside Docker.
2. **Trino 435 Iceberg Catalog Configuration:**
   - *Problem:* Trino 435 deprecated legacy `hadoop` catalog type.
   - *Correction:* Replaced with `TESTING_FILE_METASTORE` and `hive.metastore.catalog.dir=/warehouse`, with table registration enabled.
3. **Superset Trino Driver Availability:**
   - *Problem:* Base `apache/superset:3.1.0` image lacked `trino` python client.
   - *Correction:* Created `superset/Dockerfile` extending official image to install `trino-0.340.0` and pre-configured database connection.

---

## 3. Unresolved Risks & Operational Mitigation

- **Disk Space Consumption:** Iceberg metadata snapshots and Parquet files accumulate over successive runs. A scheduled snapshot expiration policy (`expire_snapshots`) can be applied in production.
- **Port Conflicts:** Ensure ports `8080` (Trino), `27017` (MongoDB), and `8088` (Superset) remain unoccupied by other background services before startup.

---

## 4. Final Run Status & Demo Readiness

- **Pipeline Execution:** 100% automated via `scripts/run_pipeline.ps1` (Windows) and `scripts/run_pipeline.sh` (Linux).
- **Trino Queries:** Tested, verified sub-second response in DBeaver and CLI.
- **MongoDB Serving:** Verified indexed collections and sub-5ms find queries.
- **Superset Dashboard:** 7 interactive clinical charts loaded with synthetic data notice.
- **Academic Viva Readiness:** 25 questions documented in `docs/viva_questions.md`, 5-minute timed script in `docs/demo_script.md`.

**Final Audit Verdict:** **APPROVED FOR FINAL FREEZE & HANDOVER**
