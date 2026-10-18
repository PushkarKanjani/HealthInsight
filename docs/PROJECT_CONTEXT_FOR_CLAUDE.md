# HealthInsight — Complete Project Dossier & Context Brief
**Use Case:** Upload this document to Claude / LLMs to provide 100% full context of the project and brainstorm new features, architectural extensions, or presentation strategies.

---

## 1. Project Overview & Philosophy

**Project Name:** HealthInsight — Clinical Big Data Lakehouse & AI Command Center  
**Core Motto:** *"Jo dikhta hai, woh bikta hai"* — A high-performance Big Data backend meets an Apple-grade, high-aesthetic interactive frontend.

HealthInsight is an end-to-end distributed Big Data analytics platform engineered over **321,528 longitudinal healthcare events** from synthetic patient populations (MITRE Synthea). It bridges traditional batch distributed data engineering (Spark, Iceberg, Trino, MongoDB) with a modern AI-powered, glassmorphic clinical command center (Gemini Text-to-SQL, Three.js WebGL liquid cursor physics, JWT security, and sub-second distributed query execution).

---

## 2. System Architecture & Tech Stack

```
                               ┌─────────────────────────────────────────────────────────────┐
                               │                    PRESENTATION TIER                        │
                               │                                                             │
                               │   AI Command Center (Port 5000)      Superset BI (Port 8088) │
                               │   • Apple Glassmorphism UI           • Daylight Clinical     │
                               │   • Three.js WebGL Liquid Flow         Executive Dashboard  │
                               │   • Lenis Silky Smooth Scroll        • Virtual Datasets     │
                               │   • Chart.js Reactive Charts                                │
                               └──────────────────────────────┬──────────────────────────────┘
                                                              │ REST (JWT)
                                                              ▼
                               ┌─────────────────────────────────────────────────────────────┐
                               │                     FASTAPI API GATEWAY                     │
                               │   • JWT Auth (/auth/login)       • Query Validator (SELECT) │
                               │   • Gemini 2.0 Flash Text-to-SQL • 12-Template Fallback     │
                               │   • Telemetry & Health Monitor   • Patient Explorer Engine  │
                               └──────────────┬──────────────────────────────┬───────────────┘
                                              │                              │
                     ┌────────────────────────┴────────┐    ┌────────────────┴──────────────┐
                     ▼                                 ▼    ▼                               ▼
     ┌───────────────────────────────┐ ┌─────────────────────────────┐ ┌─────────────────────────────┐
     │          TRINO 435            │ │         MONGODB 7.0         │ │       APACHE SPARK 3.5      │
     │ Interactive Distributed SQL   │ │ NoSQL Operational Serving   │ │ Distributed Batch ETL       │
     │ • Port 8080                   │ │ • Port 27017                │ │ • Schema enforcement        │
     │ • Memory-pipelined MPP        │ │ • Sub-2ms executive KPIs    │ │ • Ingestion & joining logic │
     │ • Queries Iceberg Parquet     │ │ • 6 pre-aggregated summary  │ │ • Aggregation & Mongo export│
     │ • Scans 321K rows in <500ms   │ │   collections (WiredTiger)  │ │                             │
     └───────────────┬───────────────┘ └─────────────────────────────┘ └──────────────┬──────────────┘
                     │                                                                │
                     └──────────────────────────────┬─────────────────────────────────┘
                                                    ▼
                                    ┌───────────────────────────────┐
                                    │       APACHE ICEBERG 1.5      │
                                    │ Open ACID Lakehouse Format    │
                                    │ • encounter_analytics (321K)  │
                                    │ • condition_analytics (114K)  │
                                    │ • Parquet columnar + metadata │
                                    └───────────────────────────────┘
```

### Component Roles & Justifications:
1. **Apache Spark 3.5 (Distributed ETL):** Cleans, joins, normalizes, and partitions raw Synthea CSVs into curated analytical tables. Enforces two-table separation to guarantee zero billing inflation (`COUNT(*) == COUNT(DISTINCT encounter_id)`).
2. **Apache Iceberg 1.5 (ACID Lakehouse Table Format):** Provides snapshot isolation, schema evolution, and partition pruning over local Parquet storage without needing a heavy Hive Metastore.
3. **Trino 435 (Distributed SQL Query Engine):** Connects directly to the Iceberg warehouse. Executes complex multi-dimension aggregations over 321,528 records in under 500 milliseconds.
4. **MongoDB 7.0 (NoSQL Operational Serving Store):** Stores pre-aggregated analytical collections (`kpis`, `encounter_type_summary`, `condition_summary`, `demographic_summary`, `organization_summary`, `encounter_trends`) for sub-2ms UI rendering.
5. **FastAPI & Uvicorn (Backend Gateway):** Async REST backend powering JWT authentication, SQL safety guards, telemetry, and integration between Trino, MongoDB, and Gemini.
6. **AI Text-to-SQL Engine (Gemini 2.0 Flash + 12-Pattern Fallback):** Converts plain English clinical questions into valid ANSI/Trino SQL queries. Features a zero-dependency deterministic fallback engine so the platform functions 100% offline.
7. **Three.js r160 WebGL Liquid Cursor Animation:** 9,000 GPU particles simulating fluid water displacement wake under the cursor, giving the UI an Apple-grade, high-end feel.
8. **Lenis.js:** Inertial momentum smooth scrolling.
9. **Apache Superset 3.1 (BI Dashboard):** Containerized dashboard for daylight clinical reporting.

---

## 3. Verified Data Scale & Invariants

| Dimension | Exact Count | Description |
|---|---|---|
| **Synthetic Patients** | 12,330 / 12,352 | Longitudinal patient demographics from Massachusetts |
| **Encounter Analytics** | 321,528 rows | 1 row per clinical encounter (`encounter_analytics`) |
| **Condition Events** | 114,544 rows | 1 row per diagnosed condition (`condition_analytics`) |
| **Gross Billed Spend** | $41,384,293.84 | Financial sums 100% verified against raw sources |
| **Avg Claim Cost** | $128.71 | Average cost per clinical encounter |
| **Iceberg Tables** | 6 registered | Registered in Trino under `iceberg.healthcare` |
| **MongoDB Collections** | 6 indexed | Pre-aggregated serving collections in `healthinsight` |

### Key Schema Elements:
- `encounter_analytics`: `encounter_id`, `patient_id`, `encounter_class` ('wellness', 'ambulatory', 'outpatient', 'urgentcare', 'emergency', 'inpatient'), `start_time`, `duration_minutes`, `total_claim_cost`, `payer_coverage`, `patient_out_of_pocket`, `patient_gender`, `patient_birthdate`, `encounter_age`, `age_group`, `patient_city`, `organization_name`.
- `condition_analytics`: `condition_start`, `condition_stop`, `patient_id`, `encounter_id`, `condition_code`, `condition_description` ('Suspected COVID-19', 'Viral sinusitis', 'Hypertension', etc.), `patient_gender`, `diagnosis_age`, `age_group`.

---

## 4. Current Features Working in the Web Portal (`localhost:5000`)

1. **Glassmorphic Login:** Centered frosted glass card over animated Three.js WebGL fluid canvas; JWT issued with 8-hour validity (`admin` / `healthinsight2024`).
2. **Executive KPI Ribbon:** Live metrics from MongoDB (Patients, Encounters, Spend, Avg Claim).
3. **Ask HealthInsight AI Copilot:**
   - Quick-question chips (Top Conditions, Cost by Class, Age Groups, Gender Split, Monthly Trends, Inpatient Admissions, Emergency Volume, Payer vs Out-of-Pocket).
   - Natural language input bar.
   - Text-to-SQL translation with Gemini 2.0 Flash.
   - Sub-second Trino execution telemetry badge (`⚡ 450ms · 10 rows`).
   - One-click **"📋 Copy SQL"** button.
   - Dynamic **Chart.js** auto-selecting bar charts, line trends, or doughnut charts.
   - Interactive Sortable Table View.
   - One-click **"⬇ Export CSV"** button.
4. **Patient Journey Explorer:** Instant lookup of synthetic patient UUIDs showing demographic cards, diagnosed condition tags, and chronological clinical encounter timelines.
5. **Lakehouse Infrastructure Monitor:** Real-time health, ping latency, and catalog statistics for Trino 435, Apache Iceberg 1.5, MongoDB 7.0, and the AI Copilot Engine.
6. **Direct Link to Superset:** One-click navigation to Apache Superset on port 8088.

---

## 5. Potential Directions for Ideation (Prompting Claude)

When sharing this document with Claude, you can explore ideas across several dimensions:

### Category A: Streaming & Real-Time Extensions
- How to introduce **Apache Kafka** or **Apache Flink** to simulate real-time patient vitals / emergency department triage events streaming into Iceberg or MongoDB.
- Real-time alert banners in the UI (e.g., ICU bed capacity alert, sudden spike in respiratory illness cases).

### Category B: Clinical Intelligence & AI Copilot Enhancements
- Multi-turn conversation memory with clinical context retention.
- AI-generated clinical narrative summaries of query results ("What does this spike in COVID-19 cases in March 2020 mean for hospital bed utilization?").
- Predictive cohort risk flags based on demographic and condition co-occurrence.

### Category C: UI/UX & Visualization Enhancements
- 3D Anatomical Body Map / Organ System filter using Three.js (clicking the chest filters conditions to cardiac/respiratory).
- Geospatial Massachusetts hospital density map (Leaflet or Mapbox).
- Dark/Light mode toggle with clinical daylight theme.

### Category D: Lakehouse Engineering & Enterprise Features
- Data version travel (Iceberg time-travel queries: `FOR TIMESTAMP AS OF ...` in the Copilot UI to show how data looked before/after a specific batch).
- Compaction & partition optimization telemetry.
- Automated data quality checks with Great Expectations or custom Trino assertion rules.

---

## 6. Suggested Prompts to Ask Claude

Copy and paste one of these prompts alongside this document:

1. **For Feature Expansion:**
   > *"Here is the complete dossier of my HealthInsight Big Data & AI project. It has Spark, Iceberg, Trino, MongoDB, FastAPI, and an Apple-style Three.js UI. What are 5 novel, practical features I can add to this project that will amaze my professors and elevate it to top-tier industry standards without breaking the working pipeline?"*

2. **For Streaming / Real-Time Integration:**
   > *"Review the HealthInsight architecture in the attached document. How can we integrate Apache Kafka for real-time telemetry (e.g. simulated patient monitor streams or emergency room admissions) into this existing Lakehouse while preserving the current Trino and MongoDB setup?"*

3. **For Presentation & Viva Defense:**
   > *"Based on the attached HealthInsight project brief, what are the top 10 tough viva questions an external examiner or professor could ask about Spark vs Trino, Iceberg metadata vs Hive, and MongoDB vs Iceberg? Provide concise, high-scoring answers."*
