# HealthInsight — 5-Minute Demonstration Script
**Target Audience:** Academic Evaluation Panel & External Viva Examiners  
**Team Allocation:** Pushkar (Trino), Hemang (Spark), Sachi (Iceberg), Yug (Superset)  
**Total Demonstration Time:** Exactly 5 Minutes  

---

## Minute 1: Problem Statement, Scope & Big Data Architecture
**Presenter:** Team Lead / Pushkar & Sachi  
**Visual Screen:** Show `docs/architecture.md` diagram and `data/raw/` file listing.

### Spoken Script:
> *"Good morning, respected professors. Today we present **HealthInsight**, an on-premise Big Data analytics platform built for high-scale descriptive healthcare analytics. 
> 
> Healthcare systems handle massive longitudinal event streams. In our raw tier, we have extracted over **321,000 patient encounters and 114,000 diagnosed clinical conditions** from the synthetic Synthea dataset. 
> 
> To process this scale, we designed a modern Lakehouse architecture using four distinct Big Data components:
> 1. **Apache Spark** for distributed ETL and deduplication.
> 2. **Apache Iceberg** as our open lakehouse table format for ACID transactions and partition pruning.
> 3. **Trino** as our distributed SQL engine for interactive, sub-second queries.
> 4. **MongoDB** as our operational serving layer for fast document lookups.
> 
> Apache Superset provides our clinical daylight dashboard. Let's look at the pipeline execution."*

---

## Minute 2: Spark Processing & Iceberg Table Separation
**Presenter:** Hemang (Spark) & Sachi (Iceberg)  
**Visual Screen:** Terminal running `python spark/03_build_analytics_tables.py` and showing `iceberg/warehouse/` directory.

### Spoken Script:
> *"In our distributed ETL layer, Apache Spark solves a critical healthcare data integrity problem: **many-to-many Cartesian explosion**.
> 
> If an encounter records four distinct diagnoses (such as Hypertension and Diabetes), joining them into a single table inflates visit counts and quadruples financial costs.
> 
> Therefore, we strictly separate data into **two analytical Iceberg tables**:
> - `healthcare.encounter_analytics`: Exactly **1 row per encounter** for calculating accurate visit counts, average durations, and costs. Here, `COUNT(*)` strictly equals `COUNT(DISTINCT encounter_id)`.
> - `healthcare.condition_analytics`: Exactly **1 row per condition-encounter event**, used exclusively for disease prevalence and demographic breakdowns.
> 
> Furthermore, all patient ages are calculated relative to event time—never using `current_date()`—guaranteeing historical accuracy."*

---

## Minute 3: Trino Distributed SQL Analytics
**Presenter:** Pushkar (Trino)  
**Visual Screen:** Trino CLI or SQL terminal running `SELECT * FROM iceberg.healthcare.encounter_analytics LIMIT 5;`.

### Spoken Script:
> *"Here, Trino connects directly to our Iceberg catalog. Notice that Trino does not launch heavy MapReduce jobs or Spark driver tasks—it executes memory-pipelined distributed SQL directly over Iceberg's columnar Parquet files.
> 
> When we run:
> ```sql
> SELECT encounter_class, COUNT(*) AS visits, ROUND(AVG(total_claim_cost), 2) AS avg_cost
> FROM iceberg.healthcare.encounter_analytics
> GROUP BY encounter_class ORDER BY visits DESC;
> ```
> Trino leverages Iceberg manifest files for partition pruning, returning results over 320,000 records in **under 1 second**."*

---

## Minute 4: MongoDB Serving Layer & Decoupled Architecture
**Presenter:** Hemang & Sachi  
**Visual Screen:** MongoDB Shell (`mongosh`) running `use healthinsight; db.kpis.findOne(); db.condition_summary.find().limit(3)`.

### Spoken Script:
> *"Next is our NoSQL serving layer in MongoDB. In a real-world hospital portal like Medisafe, doctors and mobile apps should not fire heavy distributed SQL queries at our lakehouse for basic summary cards.
> 
> Spark pre-aggregates key metrics and exports structured BSON documents into MongoDB collections: `kpis`, `condition_summary`, `encounter_type_summary`, and `encounter_trends`. 
> 
> As you can see, querying `db.kpis.findOne()` returns the pre-computed hospital KPIs in **2 milliseconds with zero joins**, decoupling our analytical warehouse from operational client apps."*

---

## Minute 5: Superset Dashboard & Clinical Visual Experience
**Presenter:** Yug (Superset)  
**Visual Screen:** Web Browser at `http://localhost:8088` showing the **HealthInsight Healthcare Analytics** dashboard.

### Spoken Script:
> *"Finally, we present our Apache Superset dashboard, styled in a **trustworthy clinical daylight theme** inspired by healthcare leaders like Medisafe and Jinga Life. We deliberately avoided dark 'gaming' themes to maintain clinical credibility.
> 
> - **Overview Tab:** Displays big-number KPI cards ($432 average cost, 321k total visits) and monthly encounter trends.
> - **Conditions Tab:** Shows the horizontal frequency breakdown of diagnosed conditions, headed by respiratory infections and hypertension.
> - **Demographics Tab:** Shows population pyramids across pediatric, adult, and geriatric cohorts.
> - **Data Lineage Tab:** Transparently presents the complete pipeline lineage with our synthetic data disclaimer.
> 
> Every chart queries Trino live or reads MongoDB summaries with zero fabricated data. Thank you, and we welcome your questions."*
