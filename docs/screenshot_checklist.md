# HealthInsight — Screenshot Verification Checklist (Prompt 18)

This checklist provides the exact commands, execution outputs, and UI locations for capturing evidence screenshots for the project submission and viva presentation.

---

## Required Screenshots Checklist

| # | Item | Exact Command / UI Location | What to Capture in Screenshot | Verified Status |
|---|---|---|---|---|
| **1** | **Project Folder Structure** | VS Code / IDE File Explorer | Root structure showing `spark/`, `trino/`, `superset/`, `scripts/`, `docs/`, `data/`, `docker-compose.yml`. | [x] Ready |
| **2** | **Dataset Profiler Output** | `python spark/01_profile_dataset.py` | Terminal output showing row counts: `patients.csv` (12,352), `encounters.csv` (321,528), `conditions.csv` (114,544), `organizations.csv` (5,499). | [x] Ready |
| **3** | **Spark Version & Environment** | `spark-submit --version` | Terminal output displaying Apache Spark `3.5.0` (or `3.5.x`), Scala `2.12.x`, and OpenJDK Runtime `17`. | [x] Ready |
| **4** | **Iceberg Runtime Test** | `python spark/00_test_iceberg.py` | Terminal showing successful creation, write, read, and drop of test Iceberg table with exit code 0. | [x] Ready |
| **5** | **Iceberg Warehouse Listing** | PowerShell: `Get-ChildItem iceberg\warehouse\healthcare` | Windows file explorer or terminal showing directories: `patients/`, `encounters/`, `conditions/`, `organizations/`, `encounter_analytics/`, `condition_analytics/`. | [x] Ready |
| **6** | **Spark Analytical Table Schema** | `python spark/03_build_analytics_tables.py` | Terminal output displaying schema of `encounter_analytics` (29 columns) and `condition_analytics` (15 columns). | [x] Ready |
| **7** | **Trino Table Listing** | DBeaver GUI or `docker exec healthinsight-trino trino --execute "SHOW TABLES FROM iceberg.healthcare;"` | Table listing showing all 6 registered tables under catalog `iceberg`, schema `healthcare`. | [x] Ready |
| **8** | **Trino KPI Query Result** | DBeaver GUI or Trino CLI running `trino/queries/01_kpis.sql` | Query result grid showing total patients (`12,352`), total encounters (`321,528`), and total claim cost (`$362,817,769.96`). | [x] Ready |
| **9** | **Trino Condition Query Result** | DBeaver GUI or Trino CLI running `trino/queries/02_conditions.sql` | Query result showing top diagnosed conditions (Acute bronchitis, Viral sinusitis, Normal pregnancy, etc.). | [x] Ready |
| **10** | **MongoDB Collection Listing** | Terminal: `mongosh --eval "use healthinsight; show collections"` | Output showing 6 collections: `condition_summary`, `demographic_summary`, `encounter_trends`, `encounter_type_summary`, `kpis`, `organization_summary`. | [x] Ready |
| **11** | **MongoDB Document Example** | Terminal: `mongosh --eval "use healthinsight; db.kpis.findOne()"` | JSON output showing pre-aggregated document with timestamps and `source_table: "encounter_analytics"`. | [x] Ready |
| **12** | **Superset Trino Connection Success** | Superset UI -> Settings -> Data -> Databases -> Edit "HealthInsight Trino Lakehouse" | Modal showing Test Connection button with green confirmation badge `"Connection looks good!"`. | [x] Ready |
| **13** | **Overview Dashboard** | Superset UI: `http://localhost:8088/superset/dashboard/1/` | Big Number cards for Total Encounters (`321,528`), Distinct Patients (`12,352`), Avg Claim Cost, and synthetic data disclaimer. | [x] Ready |
| **14** | **Conditions Section** | Superset Dashboard | Horizontal bar chart of Top 10 Diagnosed Conditions. | [x] Ready |
| **15** | **Demographics Section** | Superset Dashboard | Charts for Encounters by Age Group and Patient Gender Distribution. | [x] Ready |
| **16** | **Encounters Section** | Superset Dashboard | Encounters by Class bar chart (wellness, ambulatory, outpatient, inpatient, emergency, urgentcare). | [x] Ready |
| **17** | **Data Lineage Section** | Markdown panel in Superset Dashboard or `docs/data_lineage.md` | Flow diagram illustrating Synthea CSVs -> Spark ETL -> Iceberg Warehouse -> Trino MPP -> Superset UI & MongoDB Serving. | [x] Ready |

---

## Instructions for Taking Screenshots
1. **Resolution:** Minimum 1280x720, recommended 1920x1080.
2. **Terminal:** Clear the terminal before running each command so the command and output are both fully visible in a single frame.
3. **Naming Convention:** Save captured files to the `screenshots/` directory using filenames matching the checklist:
   - `01_project_structure.png`
   - `02_dataset_profiler.png`
   - `03_spark_version.png`
   - `04_iceberg_test.png`
   - `05_iceberg_warehouse.png`
   - `06_spark_analytical_schema.png`
   - `07_trino_table_listing.png`
   - `08_trino_kpis_query.png`
   - `09_trino_conditions_query.png`
   - `10_mongodb_collections.png`
   - `11_mongodb_document.png`
   - `12_superset_trino_connection.png`
   - `13_superset_overview_dashboard.png`
   - `14_superset_conditions.png`
   - `15_superset_demographics.png`
   - `16_superset_encounters.png`
   - `17_data_lineage.png`
