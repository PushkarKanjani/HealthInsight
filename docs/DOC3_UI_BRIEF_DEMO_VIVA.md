# HealthInsight — Document 3 of 3
## UI Brief · Dashboard Design · Demo Script · Viva Q&A

> **Covers:** Superset visual design system, dashboard layout, chart specifications, 5-minute demo script, viva questions and answers with corrected technical explanations.

---

## 1. Dashboard UI Brief

### 1.1 Design System (Trustworthy Clinical Light Theme)

> **Inspiration:** Designed following healthcare benchmarks like **Medisafe** and **Jinga Life**. Replaces dark "terminal/gaming" aesthetics with a sterile, daylight clinical palette that builds user trust, medical credibility, and accessibility.

#### Color Palette

| Token | Hex | Usage |
|---|---|---|
| `--bg-base` | `#F8FAFC` | Page background — clean medical slate-white |
| `--bg-card` | `#FFFFFF` | Card/panel surface — crisp pure white |
| `--bg-card-hover` | `#F1F5F9` | Card hover state & table alternate row |
| `--accent-primary` | `#0072CE` | Medisafe sapphire blue — primary KPIs, key action buttons, brand |
| `--accent-teal` | `#0D9488` | Jinga vitality teal/mint — recovery metrics, health indicators, chart fill 2 |
| `--accent-indigo` | `#4F46E5` | Deep clinical indigo — secondary metrics, demographic breakdowns, chart fill 3 |
| `--accent-warning` | `#D97706` | Amber — pending encounters, observation status |
| `--accent-danger` | `#DC2626` | Medical red — critical alerts only (never generic chart fills) |
| `--text-primary` | `#0F172A` | Slate 900 — headings, primary metrics, high contrast readability |
| `--text-secondary` | `#475569` | Slate 600 — subheadings, axis labels, field descriptions |
| `--text-muted` | `#94A3B8` | Slate 400 — timestamps, unit indicators, borders |
| `--border` | `#E2E8F0` | Subtle, clean border line for elevated cards |
| `--badge-bg` | `#E0F2FE` | Soft blue pill badge background |
| `--badge-text` | `#0369A1` | Pill badge text |

#### Typography

- **Dashboard title:** 24px, weight 700, `--text-primary` (`#0F172A`)
- **Section heading:** 16px, weight 600, `--text-primary`
- **KPI value:** 36px, weight 800, `--accent-primary` (`#0072CE`)
- **KPI label:** 12px, weight 600, `--text-secondary` (`#475569`), uppercase tracking +0.05em
- **Chart axis & table labels:** 11px–12px, weight 500, `--text-secondary`

#### Card Style (Custom CSS)

```css
.dashboard-component-chart-holder {
  background: #FFFFFF !important;
  border: 1px solid #E2E8F0 !important;
  border-radius: 12px !important;
  box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04), 0 6px 16px -2px rgba(15, 23, 42, 0.03) !important;
  transition: all 0.2s ease-in-out !important;
}
.dashboard-component-chart-holder:hover {
  border-color: #CBD5E1 !important;
  box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.06), 0 12px 20px -3px rgba(15, 23, 42, 0.05) !important;
}
body, .dashboard {
  background-color: #F8FAFC !important;
  color: #0F172A !important;
}
```

#### Prohibited Design Elements

- **No dark mode or developer-terminal palettes:** Dark themes look like hacker/gaming apps and undermine clinical trust.
- **No pure un-styled white or harsh gray borders:** Use clinical slate `#F8FAFC` canvas and `#E2E8F0` borders with soft shadows.
- **No neon, high-saturation, or psychedelic colors.**
- **No 3D chart effects or distracting bouncing animations.**
- **No stock clipart or cartoon placeholders.**
- **No Streamlit.**

---

### 1.2 Dashboard Layout

**Title:** `HealthInsight Healthcare Analytics`

**Tabs:**
```
[ Overview ] [ Conditions ] [ Demographics ] [ Encounters ] [ Organizations ] [ Trends ] [ Data Lineage ]
```

---

#### Tab 1: Overview

```
+-----------------------------------------------------------------------+
| HealthInsight Healthcare Analytics              [Last Refreshed: ...]  |
+----------+----------+-----------------+------------+-----------------+
| PATIENTS |ENCOUNTERS| AVG DURATION    | AVG COST   | TOTAL COST      |
|  1,000   |  15,234  |  0.5 days       | $432.12    | $6.58M          |
|  (teal)  |  (blue)  |  (purple)       | (teal)     | (blue)          |
+----------+----------+-----------------+------------+-----------------+
|    [Filter: Encounter Type v]  [Filter: Age Group v]                  |
+--------------------------------+--------------------------------------+
| Condition Frequency (top 10)   | Encounter Types                      |
| Horizontal bar, teal           | Donut: teal + blue + purple          |
| Source: condition_analytics    | Source: encounter_analytics          |
+--------------------------------+--------------------------------------+
```

---

#### Tab 2: Conditions

```
+-----------------------------------------------------------------------+
| Top 20 Conditions by Frequency (full width horizontal bar)            |
| Source: condition_analytics                                           |
+-----------------------------------+-----------------------------------+
| Conditions by Gender              | Conditions by Age Group           |
| Grouped bar: F=teal, M=blue       | Stacked bar: age groups on X      |
| Source: condition_analytics       | Source: condition_analytics        |
+-----------------------------------+-----------------------------------+
```

---

#### Tab 3: Demographics

```
+----------------------+----------------------+----------------------+
| Gender Distribution  | Age Group Dist.      | Race Distribution    |
| Donut: F=teal, M=blue| Vertical bar: teal   | Horizontal bar: teal |
| enc_analytics        | enc_analytics        | enc_analytics        |
+----------------------+----------------------+----------------------+
| Ethnicity (bar or pie — one row)                                    |
| Source: encounter_analytics                                         |
+---------------------------------------------------------------------+
```

---

#### Tab 4: Encounters

```
+------------------------------------+------------------------------------+
| Encounter Count by Type            | Avg Duration by Encounter Type     |
| Vertical bar, teal                 | Horizontal bar, blue               |
| Source: encounter_analytics        | Source: encounter_analytics        |
+------------------------------------+------------------------------------+
| Avg Cost by Encounter Type (only if cost columns confirmed)           |
| Horizontal bar, purple                                                |
| Source: encounter_analytics                                           |
+-----------------------------------------------------------------------+
```

---

#### Tab 5: Organizations

```
+-----------------------------------------------------------------------+
| Top 20 Organizations by Encounter Count (full width horizontal bar)   |
| Source: encounter_analytics                                           |
+------------------------------------+----------------------------------+
| Avg Cost by Organization           | Table: all org data (sortable)   |
| Bar chart, blue                    | Source: encounter_analytics       |
+------------------------------------+----------------------------------+
```

---

#### Tab 6: Trends

```
+-----------------------------------------------------------------------+
| Monthly Encounter Trend (full width line chart)                       |
| X: Month/Year, Y: encounter_count                                     |
| Teal line + area fill (opacity 0.15)                                  |
| Source: encounter_analytics                                           |
+-----------------------------------------------------------------------+
| Year-over-year comparison (multi-line, one line per year)             |
| Source: encounter_analytics                                           |
+-----------------------------------------------------------------------+
```

---

#### Tab 7: Data Lineage

```
+-----------------------------------------------------------------------+
| Data Lineage & Architecture                                           |
|                                                                       |
| Synthea CSV -> Spark -> Iceberg -> Trino -> Superset                  |
|                              |                                        |
|                           MongoDB                                     |
|                                                                       |
| Component    | Role                   | Version                       |
| Spark        | Distributed ETL        | 3.5.x                         |
| Iceberg      | Lakehouse table format | 1.8.x                         |
| Trino        | Distributed SQL        | 435+                          |
| MongoDB      | NoSQL agg. store       | 7.x                           |
+-----------------------------------------------------------------------+
```

---

### 1.3 Superset Setup (Separate Python Environment)

#### Step 1: Create Superset virtual environment

```bash
python3 -m venv venv-superset
source venv-superset/bin/activate
pip install -r superset/requirements-superset.txt
```

#### Step 2: Add Trino database in Superset

```
Settings -> Database Connections -> + Database
Engine: Trino
SQLAlchemy URI: trino://admin@localhost:8080/iceberg
Display Name: HealthInsight Trino
```

> Test the connection before saving. Username and auth depend on your Trino config.

#### Step 3: Create virtual datasets

| Dataset Name | Source SQL file |
|---|---|
| kpi_overview | `trino/queries/01_kpis.sql` |
| condition_frequency | `trino/queries/02_conditions.sql` (first query) |
| demographic_distribution | `trino/queries/03_demographics.sql` |
| encounter_analytics | `trino/queries/04_encounters.sql` |
| monthly_trends | `trino/queries/05_trends.sql` |

#### Step 4: Build charts

- KPI cards: Big Number chart type, one per metric
- Condition bars: Bar Chart (horizontal), source: condition_analytics
- Trend line: Line Chart, X=month, Y=encounter_count
- Donut charts: Pie Chart for gender, race distributions
- Tables: Table chart for org summaries

#### Step 5: Apply Trustworthy Clinical Light Theme CSS in dashboard edit mode

In Superset: **Edit Dashboard -> ... -> Edit CSS**

```css
/* HealthInsight Clinical Light Theme (Inspired by Medisafe & Jinga Life) */
body, .dashboard {
  background-color: #F8FAFC !important;
  color: #0F172A !important;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
}

/* Clinical elevated white cards */
.dashboard-component-chart-holder {
  background: #FFFFFF !important;
  border: 1px solid #E2E8F0 !important;
  border-radius: 12px !important;
  box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04), 0 6px 16px -2px rgba(15, 23, 42, 0.03) !important;
  transition: all 0.2s ease-in-out !important;
}

.dashboard-component-chart-holder:hover {
  border-color: #CBD5E1 !important;
  box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.06), 0 12px 20px -3px rgba(15, 23, 42, 0.05) !important;
}

/* Header & navigation bar */
.header-with-controls, .dashboard-header {
  background: #FFFFFF !important;
  border-bottom: 1px solid #E2E8F0 !important;
  box-shadow: 0 1px 2px 0 rgba(15, 23, 42, 0.03) !important;
}

.chart-header .header-title {
  color: #0F172A !important;
  font-weight: 600 !important;
  font-size: 15px !important;
}

/* Big Number / KPI values */
.dashboard-component-chart-holder .superset-legacy-chart-big-number text {
  fill: #0072CE !important;
  font-weight: 800 !important;
}

/* Filter bar & tab active indicators */
.ant-tabs-ink-bar {
  background: #0072CE !important;
}
.ant-tabs-tab-active .ant-tabs-tab-btn {
  color: #0072CE !important;
  font-weight: 600 !important;
}
```

---

## 2. Demo Script (5-Minute Viva Walkthrough)

### 2.1 Opening Statement (30 seconds)

> "HealthInsight is a local Big Data analytics platform built on four genuine distributed data components: Apache Spark for ETL, Apache Iceberg as the lakehouse table format, Trino as the distributed SQL query engine, and MongoDB as the NoSQL aggregation store. Apache Superset provides the interactive dashboard, connected to Trino. The dataset is Synthea synthetic healthcare data — not real patient records."

---

### 2.2 Step-by-Step Demo Flow

| Step | Action | What to Show | Expected Output |
|---|---|---|---|
| 1 | Terminal | `bash scripts/verify_services.sh` | Spark, Trino, MongoDB all running |
| 2 | Raw data | `ls data/raw/` + `head -n 3 patients.csv` | CSV files with confirmed headers |
| 3 | Data dict | Open `docs/dataset_dictionary.md` | Real columns, row counts, null counts |
| 4 | Run pipeline | `bash scripts/run_pipeline.sh` | 4 scripts complete |
| 5 | Iceberg tables | Trino CLI: `SHOW TABLES FROM iceberg.healthcare;` | 6 Iceberg tables listed |
| 6 | Row count check | Trino: `SELECT COUNT(*), COUNT(DISTINCT encounter_id) FROM iceberg.healthcare.encounter_analytics;` | Both numbers must match |
| 7 | Conditions | Trino: run `02_conditions.sql` | Top conditions with frequency |
| 8 | MongoDB | `mongosh`: `db.condition_summary.findOne()` | Aggregate document with generated_at |
| 9 | Superset | Browser -> Superset dashboard | KPI cards and charts loaded from Trino |
| 10 | Refresh | Place updated CSV, `bash scripts/run_pipeline.sh` | New snapshot, updated counts |

---

### 2.3 Screenshot Checklist

Before the viva:

- [ ] `01_profile_dataset.py` console output — schema, row counts, nulls
- [ ] `02_ingest_raw_to_iceberg.py` — `SHOW TABLES` output
- [ ] `03_build_analytics_tables.py` — row count equality assertion passes
- [ ] `04_export_mongodb.py` — collection write confirmations
- [ ] Trino CLI: `SHOW CATALOGS` and `SHOW TABLES`
- [ ] Trino CLI: condition frequency query result
- [ ] Trino CLI: KPI query result
- [ ] MongoDB: `db.kpis.findOne()` and `db.condition_summary.find().limit(3)`
- [ ] Superset: Overview tab with KPI cards
- [ ] Superset: Conditions tab with top-20 bar chart
- [ ] Superset: Trends tab with monthly line chart
- [ ] Architecture diagram on screen

---

## 3. Viva Questions & Answers

### 3.1 Architecture

**Q: What problem does your project solve?**
> "Healthcare records are distributed across multiple related datasets and are difficult to inspect manually. HealthInsight provides a reproducible pipeline that cleans, joins, stores, queries, and visualizes synthetic healthcare records for descriptive analysis."

**Q: What is your complete data flow?**
> "Synthea CSV files go into Spark, which profiles and then ingests them as Iceberg raw tables. Spark then transforms those into two analytical tables — encounter_analytics and condition_analytics. Trino runs SQL queries over those Iceberg tables. Spark also exports aggregate DataFrames to MongoDB. Superset connects to Trino and renders the dashboard."

**Q: Why did you choose this specific stack?**
> "Each component plays a different role. Spark processes data. Iceberg manages the table format and storage layer. Trino provides distributed SQL analytics. MongoDB serves pre-computed aggregate documents. They are not four random databases — each solves a distinct problem in the pipeline."

---

### 3.2 Apache Spark

**Q: Why Spark?**
> "Spark is a distributed ETL engine. It reads multiple CSV files, cleans inconsistent values, normalizes column names, joins patients, encounters, conditions, and organizations, derives age groups and encounter duration, and writes the results as Iceberg tables. It also exports summary aggregates to MongoDB using the official MongoDB Spark Connector."

**Q: How did you configure Spark for Iceberg?**
> "We added the IcebergSparkSessionExtensions and configured a SparkCatalog of type hadoop, pointing to our local warehouse directory. We also passed the Iceberg runtime JAR via spark-submit --jars. The JAR filename must match the Spark minor version and Scala binary version — for Spark 3.5.x with Scala 2.12, we use `iceberg-spark-runtime-3.5_2.12`."

**Q: How does Spark connect to MongoDB?**
> "Using the official MongoDB Spark Connector. We pass the connector JAR at submission time and set the MongoDB connection URI in the Spark session config. DataFrames are written using `df.write.format('mongodb')` with the database and collection specified as options."

---

### 3.3 Apache Iceberg

**Q: What is Apache Iceberg?**
> "Apache Iceberg is an open table format for large analytical datasets. It stores data as Parquet files and maintains a separate metadata layer that tracks the table schema, partitioning information, and snapshots. It supports schema evolution and ACID writes. Importantly, Iceberg is not a query engine — it is a table format that allows Spark and Trino to share the same tables reliably."

**Q: Why Iceberg instead of just writing Parquet files?**
> "If we wrote raw Parquet files, we would have no table metadata, no schema management, no snapshots, and no reliable concurrent reads. Iceberg adds all of those. It also allows two different engines — Spark and Trino — to work with the same tables without coordination problems."

**Q: What does Iceberg store in the warehouse?**
> "Each table in the warehouse contains Iceberg-managed Parquet data files and metadata JSON files. The metadata tracks every schema version and snapshot. The exact internal structure is managed by Iceberg itself. What we care about as engineers is that the table is queryable by both Spark and Trino through the same warehouse path."

**Q: Is Iceberg distributed?**
> "Iceberg is a table format, not an execution engine. It does not distribute or execute anything. The distribution happens in Spark and Trino, which are the engines that read and write Iceberg tables in parallel."

---

### 3.4 Trino

**Q: Why Trino if Spark can already run SQL?**
> "Spark SQL is useful during data processing, but Trino provides a separate distributed SQL query layer. This separation is intentional: Spark transforms and prepares the data, Trino queries the prepared data. Trino also has a direct Iceberg connector and integrates cleanly with Superset, making it the right analytical data source for the dashboard."

**Q: How does Trino connect to Iceberg?**
> "Trino has a built-in Iceberg connector. We create a catalog configuration file that specifies the connector name as `iceberg`, the catalog type as `hadoop`, and the same warehouse path used in Spark. Trino reads the Iceberg metadata directly from that path and plans queries over the Parquet files."

**Q: What SQL analytics does Trino run?**
> "We have five categories: KPI aggregates over encounter_analytics, condition frequency and demographic breakdown over condition_analytics, encounter type analysis over encounter_analytics, monthly trend analysis over encounter_analytics, and organization summaries over encounter_analytics."

---

### 3.5 MongoDB

**Q: What does MongoDB store?**
> "MongoDB stores six pre-computed aggregate collections: KPIs, condition summaries, encounter type summaries, monthly encounter trends, and optionally demographic and organization summaries. Every document was written by Spark using real pipeline results — no fabricated data."

**Q: Why MongoDB if Trino can answer all the same queries?**
> "MongoDB demonstrates a different data serving pattern — document-oriented, schema-flexible storage for pre-computed results. This is a real pattern in analytics architectures where a fast document store reduces dashboard query latency. MongoDB also satisfies the project requirement for a NoSQL Big Data component with a meaningfully different role from the Iceberg tables."

**Q: Which MongoDB collections come from which source tables?**
> "KPIs, encounter type summaries, trends, and organization summaries all come from encounter_analytics. Condition summaries come from condition_analytics. This matters because if you used condition_analytics as the source for encounter counts, each encounter with multiple conditions would be counted multiple times."

**Q: Is MongoDB distributed?**
> "In this project, MongoDB runs as a single Community Edition instance — it is not configured as a distributed system. In production, MongoDB can be deployed as a replica set or sharded cluster. For this educational project, the key value is the document model and aggregation capabilities, not horizontal distribution."

---

### 3.6 The Two-Table Design

**Q: Why do you have two analytical tables — encounter_analytics and condition_analytics?**
> "One patient encounter can have multiple recorded conditions. If we join conditions directly into the encounter table, we get multiple rows per encounter. That means COUNT(encounters) is wrong and SUM(cost) is inflated. We prevent this by keeping the tables separate. encounter_analytics has exactly one row per encounter and is used for all encounter-level metrics. condition_analytics has one row per encounter-condition pair and is only used for condition-level analytics."

**Q: How do you verify encounter_analytics has exactly one row per encounter?**
> "We run an assertion in the Spark script: `COUNT(*) must equal COUNT(DISTINCT encounter_id)`. If they differ, the pipeline stops and reports the failure."

---

### 3.7 Age Calculation

**Q: How did you calculate age?**
> "We calculate age relative to the event date — encounter_start for encounter_analytics and condition_start for condition_analytics. We use `floor(months_between(event_date, birth_date) / 12)`. We do not use `current_date()` because that would make historical age values change every time the pipeline runs, making results non-reproducible."

---

### 3.8 Data and Ethics

**Q: Is this real patient data?**
> "No. All records are generated by Synthea, an open-source synthetic patient generator developed by MITRE Corporation. The records are statistically realistic but entirely synthetic. There are no real patient identities, diagnoses, or medical histories."

**Q: Who are your competitors?**
> "Commercial healthcare analytics platforms include Microsoft Cloud for Healthcare, Google Cloud Healthcare Data Engine, AWS healthcare services, Databricks Lakehouse, Snowflake healthcare solutions, Palantir Foundry, and SAS. Our project does not compete with them in scale, security, or clinical usefulness. We are implementing a smaller reproducible version to demonstrate the architecture and integration of Big Data tools."

**Q: Why build this if competitors exist?**
> "We are not trying to replace enterprise healthcare products. We are implementing a smaller, reproducible version to understand how Big Data tools — Spark, Iceberg, Trino, and MongoDB — work together in a pipeline, using healthcare data as a realistic, multi-table domain."

---

### 3.9 One-Sentence Architecture Summary

> "Apache Iceberg provides the open table format and metadata layer. Apache Spark performs distributed ETL — reading CSVs, transforming data, writing Iceberg tables, and exporting MongoDB aggregates. Trino provides distributed SQL analytics over the Iceberg tables. MongoDB serves pre-computed aggregate documents. Apache Superset connects to Trino to render the interactive dashboard."

---

## 4. Docs Checklist

| File | Content | Owner |
|---|---|---|
| `docs/architecture.md` | Full architecture diagram + component roles | Hemang |
| `docs/dataset_dictionary.md` | Auto-generated by `01_profile_dataset.py` | Sachi |
| `docs/data_lineage.md` | Step-by-step data flow with table names and source columns | Sachi |
| `docs/version_lock.md` | Actual installed versions — fill after install | Hemang |
| `docs/demo_script.md` | Section 2 of this document | Yug |
| `docs/viva_questions.md` | Section 3 of this document | Pushkar |
| `README.md` | Setup steps, run commands, version lock reference | Hemang |
| `superset/connection_setup.md` | Superset env, Trino connection, dataset steps | Yug |
| `superset/dashboard_setup.md` | Chart-by-chart build guide | Yug |
