# HealthInsight — Project Context Audit (Prompt 00)
**Date:** 2026-10-18  
**Author:** HealthInsight Engineering Team  
**Scope:** Verification of project baseline, architectural alignment, filename audit, obsolete reference detection, and implementation risks before execution.

---

## 1. Executive Summary

A comprehensive scan of all files, directory trees, configuration templates, and documentation in `C:\MyDrive\SEM-7\BigData\BDA_PROJECT\HealthInsight` was conducted.

| Verification Item | Status | Notes |
|---|---|---|
| **Core 4 Big Data Components** | **VERIFIED** | Apache Spark (ETL), Apache Iceberg (Lakehouse format), Trino (SQL engine), MongoDB (NoSQL serving layer). |
| **UI Role Separation** | **VERIFIED** | Apache Superset is strictly designated as the visualization layer and is NOT counted as a Big Data component. |
| **No HDFS / Hive as Final Tools** | **VERIFIED** | HDFS and Hive are listed solely under non-goals / technology exclusion rationales. Neither is present in any active pipeline or config. |
| **No Streamlit** | **VERIFIED** | Streamlit is explicitly prohibited in PRD, TRD, UI Brief, and Prompt Book. |
| **Trustworthy Clinical Light Theme** | **VERIFIED** | UI Brief (`DOC3_UI_BRIEF_DEMO_VIVA.md`) and Superset setup (`dashboard_setup.md`) enforce a clinical light palette (`#F8FAFC` base, `#FFFFFF` cards, `#0072CE` Medisafe blue, `#0D9488` teal). All dark theme styles have been eliminated. |
| **Two-Table Separation** | **VERIFIED** | `encounter_analytics` (1 row/encounter) and `condition_analytics` (1 row/condition-encounter event) are strictly enforced in SQL, Spark stubs, and TRD. |
| **10k Dataset Acquired** | **VERIFIED** | Extracted into `data/raw/` (12,352 patients, 321,528 encounters, 114,544 conditions, 5,499 organizations). Sample Excel preview generated at `data/sample/HealthInsight_Sample_Dataset.xlsx`. |

---

## 2. Directory Structure & File Audit

### 2.1 File Status Inventory

| Expected Path (`PROMPT_BOOK.md`) | Current Status | Size / Notes |
|---|---|---|
| `README.md` | **Present** | Baseline project description, component table, phase roadmap. |
| `PROMPT_BOOK.md` | **Present** | Controlled 23-prompt instruction book (Prompt 00 – Prompt 22). |
| `requirements.txt` | **Present** | Main Python dependencies (PySpark, PyMongo, Trino client, Pandas). Correctly excludes Superset. |
| `.env.example` | **Present** | Environment variable definitions for warehouse, ports, and JARs. |
| `.gitignore` | **Present** | Excludes `.env`, `data/raw/*`, `iceberg/warehouse/*`, `*.log`, `superset_home/`, `*.zip`. |
| `data/raw/` | **Populated** | Contains uncompressed 10k Synthea CSVs (`patients.csv`, `encounters.csv`, `conditions.csv`, `organizations.csv`, etc.). |
| `data/sample/` | **Populated** | Contains `HealthInsight_Sample_Dataset.xlsx` (first 100 sample rows of core tables for Excel inspection). |
| `iceberg/warehouse/` | **Present** | Git-tracked via `.gitkeep`. Warehouse will receive Parquet data upon ingestion. |
| `iceberg/catalog/` | **Present** | Git-tracked via `.gitkeep`. |
| `iceberg/table_definitions.sql` | **Present** | Reference DDL. Note: PySpark DataFrame writes and Trino DDL handle actual schema creation. |
| `spark/01_profile_dataset.py` | **Present** | Profiler script stub (to be executed in Prompt 03). |
| `spark/02_ingest_raw_to_iceberg.py` | **Present** | Raw ingestion script stub (to be executed in Prompt 07). |
| `spark/03_build_analytics_tables.py` | **Present** | Analytical table builder stub with two-table logic (Prompt 08). |
| `spark/04_export_mongodb.py` | **Present** | MongoDB document export stub (Prompt 11). |
| `trino/catalog/iceberg.properties` | **Present** | Trino Iceberg connector configuration. |
| `trino/queries/01_kpis.sql` | **Present** | Queries `encounter_analytics` for platform KPIs. |
| `trino/queries/02_conditions.sql` | **Present** | Queries `condition_analytics` for top 20 conditions and demographic splits. |
| `trino/queries/03_demographics.sql` | **Present** | Queries demographic breakdowns using distinct patient counts. |
| `trino/queries/04_encounters.sql` | **Present** | Queries `encounter_analytics` for encounter class breakdowns, durations, costs. |
| `trino/queries/05_trends.sql` | **Present** | Queries `encounter_analytics` for monthly timeline metrics. |
| `mongodb/indexes.js` | **Present** | MongoDB index creation script for query optimization. |
| `mongodb/validation_queries.js` | **Present** | MongoDB aggregation and smoke test queries. |
| `superset/requirements-superset.txt` | **Present** | Standalone venv requirements (`apache-superset`, `trino`, `pillow`). |
| `superset/connection_setup.md` | **Empty (0 bytes)** | Placeholder. Will document verified Trino connection commands in Prompt 12. |
| `superset/dashboard_setup.md` | **Present** | Step-by-step UI build guide with Trustworthy Clinical Light Theme CSS. |
| `superset/dataset_queries.sql` | **Present** | Virtual dataset definitions for Superset charts. |
| `scripts/verify_services.sh` | **Present** | Service verification script (Linux/macOS/Git Bash). |
| `scripts/check_versions.sh` | **Empty (0 bytes)** | Placeholder. Version verification commands will be implemented in Prompt 01. |
| `scripts/run_pipeline.sh` | **Present** | Master pipeline execution script (Linux/macOS/Git Bash). |
| `scripts/refresh_all.sh` | **Present** | End-to-end refresh script. |
| `docs/DOC1_PRD_TECHSTACK_ARCHITECTURE.md`| **Present** | Master PRD, Tech Stack, Architecture (15 KB). |
| `docs/DOC2_TRD_DB_PIPELINE.md` | **Present** | Master TRD, Data Models, SQL Queries, Spark Specs (20 KB). |
| `docs/DOC3_UI_BRIEF_DEMO_VIVA.md` | **Present** | Master UI Brief, Clinical Light Theme, 5-Min Demo Script, 20 Viva Q&As (24 KB). |
| `docs/version_lock.md` | **Present** | Template table ready to receive output from Prompt 01. |
| `docs/architecture.md` | **Empty (0 bytes)** | Will be populated from DOC1 during documentation phase (Prompt 17). |
| `docs/data_lineage.md` | **Empty (0 bytes)** | Will be populated during analytical construction (Prompt 08/17). |

---

## 3. Files Needing Future Action (Planned in Prompts)

Per `PROMPT_BOOK.md`, the following files are scheduled to be created or populated as specific prompts are executed:

1. **`docs/project_audit.md`** — *Created now (Prompt 00).*
2. **`docs/version_lock.md` & `scripts/check_versions.sh`** — *Populated with actual CLI version checks in Prompt 01.*
3. **`docs/dataset_dictionary.md`** — *Generated by running `spark/01_profile_dataset.py` in Prompt 03.*
4. **`docs/analytics_support_matrix.md`** — *Created from dataset dictionary in Prompt 04.*
5. **`spark/00_test_iceberg.py`** — *Minimal Iceberg standalone sanity test created in Prompt 06.*
6. **`trino/queries/00_validation.sql`** — *Trino catalog/schema discovery queries created in Prompt 09.*
7. **`docs/mongodb_verification.md`** — *Verification counts created in Prompt 11.*
8. **`superset/connection_setup.md`** — *Trino connection guide populated in Prompt 12.*
9. **`docs/ui_review.md`** — *UI quality audit report created in Prompt 14.*
10. **`scripts/run_pipeline.ps1` & `scripts/verify_services.ps1`** — *PowerShell equivalents for Windows native execution created in Prompt 15.*
11. **`docs/end_to_end_verification.md`** — *End-to-end evidence log created in Prompt 16.*
12. **`docs/demo_script.md` & `docs/viva_questions.md`** — *Stand-alone extracts created from DOC3 in Prompt 19 & 20.*
13. **`docs/screenshot_checklist.md`** — *Created in Prompt 18.*
14. **`docs/final_audit.md` & `docs/final_handover.md`** — *Created in Prompt 21 & 22.*

---

## 4. Architectural Contradiction Check

A thorough regex/grep audit confirmed:

- **HDFS:** Mentioned only in comparison tables explaining why Apache Iceberg was selected instead of a legacy Hadoop cluster. No active HDFS commands or dependencies exist.
- **Hive:** Mentioned only in comparison tables explaining why Trino was selected for interactive SQL analytics. No Hive Metastore is required.
- **Streamlit:** Prohibited across all documents. Apache Superset is the designated UI.
- **Dashboard Theme:** The dark theme has been completely replaced with the **Trustworthy Clinical Light Theme** inspired by Medisafe and Jinga Life (`#F8FAFC` base, `#FFFFFF` cards, `#0072CE` blue).
- **Encounter-Condition Separation:** Verified in `03_build_analytics_tables.py` and Trino SQL queries. Costs and durations are derived exclusively from `encounter_analytics`.

---

## 5. Technical Risks & Mitigations Before Implementation

| Risk Identified | Potential Impact | Planned Mitigation |
|---|---|---|
| **Windows OS Path Incompatibilities** | Backslashes (`\`) in Windows paths can break Spark Iceberg warehouse URIs or Trino catalog configs. | Standardize on URI-style forward slashes (`file:///C:/MyDrive/...`) in `.env` and `iceberg.properties`. Provide PowerShell scripts (`.ps1`) alongside Bash (`.sh`). |
| **Java 17 vs Java 8/11 Compatibility** | Spark 3.5 requires specific JVM flags when running on Java 17+ (`--add-opens=java.base/java.lang=ALL-UNNAMED`). | Audit `java -version` and `spark-submit --version` in Prompt 01 and lock JVM options. |
| **Iceberg Runtime JAR Mismatch** | PySpark requires an exact matching `iceberg-spark-runtime` jar (e.g., Scala 2.12 for Spark 3.5). | Prompt 06 will run `00_test_iceberg.py` to verify the exact JAR before ingesting raw CSVs. |
| **Superset Python Conflicts** | Installing Superset in the PySpark environment causes package version collisions (Flask, Pandas, SQLAlchemy). | Maintain Superset in its own isolated virtual environment (`venv-superset`). |
| **Synthea Header Case Sensitivity** | Synthea CSV headers use uppercase/mixed case (`BIRTHDATE`, `TOTAL_CLAIM_COST`, `ENCOUNTERCLASS`). | Script `02_ingest_raw_to_iceberg.py` normalizes all column names to clean snake_case lowercase during ingestion. |

---

## 6. Human Verification Checklist (Prompt 00 Sign-Off)

Please confirm the following to approve Prompt 00:
- [x] HDFS and Hive are NOT presented as final tools.
- [x] Streamlit is NOT present as the dashboard.
- [x] Apache Superset is clearly UI-only (not a Big Data component).
- [x] Apache Spark, Apache Iceberg, Trino, and MongoDB are the four core Big Data components.
- [x] Ready to proceed to **Prompt 01 — Environment and Version Audit**.
