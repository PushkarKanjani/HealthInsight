# HealthInsight — Architecture & Component Design
**Project:** HealthInsight Big Data Analytics Platform  
**Type:** 4th-Year Undergraduate Big Data Analytics Capstone  
**Target Architecture:** Distributed Lakehouse & Decoupled Serving Architecture  

---

## 1. System Overview

HealthInsight is an end-to-end, on-premise Big Data platform engineered to process, manage, analyze, and visualize high-volume synthetic longitudinal healthcare data.

The platform processes **12,352 synthetic patients, 321,528 clinical encounters, and 114,544 diagnosed condition events** through a 4-tier pipeline:

```
[Raw CSVs (Synthea 10k)]
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ 1. APACHE SPARK 3.5 (Distributed ETL Engine)           │
│    • Schema-on-read type casting & data sanitation     │
│    • Event-time relative age calculation (non-current) │
│    • Relational joins with entity deduplication        │
└─────────┬────────────────────────────────────┬─────────┘
          │                                    │
          ▼ Writes Parquet + Metadata          ▼ Exports Aggregate JSON
┌────────────────────────────────────┐ ┌────────────────────────────────────┐
│ 2. APACHE ICEBERG 1.8 (Lakehouse)  │ │ 4. MONGODB 7 (NoSQL Serving Layer) │
│    • ACID transactions             │ │    • Pre-aggregated document store │
│    • Hidden partitioning           │ │    • Indexed key-value lookups     │
│    • Snapshot isolation            │ │    • Low-latency (<10ms) app access│
└─────────────────┬──────────────────┘ └────────────────────────────────────┘
                  │
                  ▼ Reads Partitioned Parquet
┌────────────────────────────────────┐
│ 3. TRINO 435+ (Distributed SQL)    │
│    • High-speed distributed SQL    │
│    • Complex multi-table OLAP      │
│    • Sub-second query response     │
└─────────────────┬──────────────────┘
                  │
                  ▼ Connects via SQLAlchemy
┌────────────────────────────────────┐
│ APACHE SUPERSET (UI Layer)         │
│    • Trustworthy Clinical Light UI │
│    • Interactive BI Dashboards     │
│    • Pure visualization role       │
└────────────────────────────────────┘
```

---

## 2. Component Roles & Separation of Concerns

| Component | Architecture Role | Execution Model | Storage Substrate |
|---|---|---|---|
| **Apache Spark** | Distributed Compute (Batch ETL) | Memory-centric Directed Acyclic Graph (DAG) | In-Memory JVM |
| **Apache Iceberg** | Open Lakehouse Table Format | Metadata-driven ACID specification | Columnar Parquet + JSON metadata |
| **Trino** | Interactive Distributed SQL Engine | Memory-pipelined MPP query engine | Stateless (queries Iceberg) |
| **MongoDB** | NoSQL Operational Serving Store | Document / BSON engine | WiredTiger storage engine |
| **Apache Superset** | BI & Dashboard Visualization | Flask / React web application | SQLite / PostgreSQL metadata |

> [!IMPORTANT]
> **Apache Superset is NOT one of the 4 Big Data components.** It is strictly the presentation layer. The four Big Data components are Spark, Iceberg, Trino, and MongoDB.

---

## 3. Storage Layer Architecture: Apache Iceberg

Traditional data lakes (raw CSV or unmanaged Parquet on S3/HDFS) suffer from critical limitations:
1. No ACID transactions (failed writes corrupt datasets).
2. No schema evolution (adding a column breaks old files).
3. Slow file listing operations (reading thousands of directory partitions bottlenecks the query engine).

### Iceberg's 3-Layer Metadata Tree

```
iceberg/warehouse/healthcare.db/encounter_analytics/
├── metadata/
│   ├── v1.metadata.json           <-- Table schema, partition spec, snapshot list
│   ├── snap-48192-1-manifest.avro <-- Manifest list (points to manifest files)
│   └── 48192-m0.avro              <-- Manifest file (tracks individual data files + min/max stats)
└── data/
    └── encounter_class=wellness/
        ├── 00000-1-data.parquet   <-- Columnar compressed encounter rows
        └── 00001-1-data.parquet
```

- **Hidden Partitioning:** Users query `WHERE start >= '2023-01-01'` without knowing internal partition paths. Iceberg prunes unneeded files before Trino reads a single byte.
- **Snapshot Isolation:** Concurrent readers never see partial writes from running Spark batch jobs.

---

## 4. Query Layer Architecture: Trino vs. Spark SQL

A common architectural question: *Why use Trino when Spark already has Spark SQL?*

| Feature | Apache Spark (Spark SQL) | Trino |
|---|---|---|
| **Primary Design Goal** | High-throughput batch computation | Low-latency interactive querying |
| **Execution Architecture** | Starts executors per batch job (5–15s overhead) | Persistent long-running worker daemons |
| **Query Latency** | High (5–30 seconds) | Sub-second (0.3 – 1.5 seconds) |
| **Dashboard Suitability** | Poor (Superset filters lag) | **Ideal (Instant chart updates)** |

Trino bypasses Spark entirely at query time: Trino directly reads Iceberg metadata, identifies the target Parquet files, and streams rows into memory for parallel aggregation.

---

## 5. Serving Layer Architecture: Why MongoDB?

In enterprise healthcare applications (e.g., patient portals like Medisafe or hospital EHRs):
- **OLAP (Analytics):** Business intelligence analysts run large queries across 300,000+ rows. (Handled by **Trino + Iceberg**).
- **OLTP / Operational Serving:** Doctors and mobile apps need immediate access to pre-computed metrics (e.g. top hospital conditions, department KPI cards) in **<10 milliseconds** without launching a distributed SQL cluster. (Handled by **MongoDB**).

Spark pre-calculates analytical summaries and pushes them into MongoDB as structured BSON documents:
- `kpis` (System-wide totals, costs, and durations)
- `condition_summary` (Top conditions with pre-computed counts and percentages)
- `encounter_type_summary` (Volume and average cost per encounter class)
- `encounter_trends` (Monthly timeline aggregates)
