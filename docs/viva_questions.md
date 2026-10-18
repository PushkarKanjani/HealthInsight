# HealthInsight — 25 Master Viva Questions & Answers
**Focus:** 4th-Year Undergraduate Big Data Analytics Evaluation  
**Audience:** Hemang (Spark), Sachi (Iceberg), Pushkar (Trino), Yug (Superset)  

---

### Q1: What is the core problem HealthInsight solves?
**Answer:** HealthInsight processes high-volume longitudinal healthcare records (321,000+ encounters, 114,000+ conditions) into a high-performance Lakehouse architecture, decoupling analytical SQL querying (Trino + Iceberg) from operational document serving (MongoDB), visualized on a clinical BI dashboard (Superset).

### Q2: Why Apache Spark instead of standard Python/Pandas?
**Answer:** Pandas loads all data into a single process's memory space and is limited by a single CPU core. At 320k encounters, multi-table joins choke single-node memory. Apache Spark provides distributed computing with partitioned memory management, fault-tolerant execution DAGs, and optimized parallel joins across worker cores.

### Q3: Why Apache Iceberg instead of raw Parquet on disk?
**Answer:** Raw Parquet files lack a transactional metadata layer. Without Iceberg, concurrent writes cause file corruption, directory listing overhead degrades query performance, and deleting or updating records requires rewriting entire folders. Iceberg provides ACID transactions, snapshot isolation, hidden partitioning, and schema evolution.

### Q4: Why Trino instead of Spark SQL?
**Answer:** Spark is optimized for high-throughput batch transformations with heavy startup overhead (5–15 seconds per job). Trino is an interactive, memory-pipelined MPP SQL engine designed for sub-second latency (0.5–1.5 seconds) over Iceberg tables, making it ideal for powering live BI dashboards like Superset.

### Q5: Why MongoDB instead of PostgreSQL or MySQL?
**Answer:** 
1. **Curriculum Alignment:** The syllabus requires a NoSQL component. Trino and Iceberg already handle all relational SQL querying.
2. **Operational Serving Decoupling:** Web and mobile applications (like Medisafe) require fast, pre-aggregated JSON documents. Storing pre-computed summaries in MongoDB allows API clients to fetch metrics in 2 milliseconds with zero table joins, shielding the data warehouse from heavy query traffic.

### Q6: Why is Apache Superset not counted as one of the 4 Big Data components?
**Answer:** Superset is an application-tier BI visualization and dashboard tool. It does not store or process Big Data natively; it submits SQL queries to Trino and renders charts. The four Big Data storage and processing components are Spark, Iceberg, Trino, and MongoDB.

### Q7: Why not Hadoop HDFS?
**Answer:** HDFS requires managing heavy NameNode and DataNode daemons, suffers from high resource overhead, and couples compute tightly with physical disks. Iceberg provides modern object-store and local filesystem lakehouse capabilities with superior metadata management without needing a legacy Hadoop cluster.

### Q8: Why not Apache Hive?
**Answer:** Hive relies on high-latency MapReduce/Tez execution and requires an external Hive Metastore (HMS) database. Trino queries Iceberg tables directly without Hive execution overhead, delivering up to 50x faster interactive query speeds.

### Q9: Why not Snowflake?
**Answer:** Snowflake is a proprietary, closed-source commercial cloud service. HealthInsight is an educational on-premise Big Data platform built entirely on open-source Apache foundation software that runs locally without cloud subscription costs or vendor lock-in.

### Q10: Why are there TWO analytical tables instead of one large joined table?
**Answer:** A patient encounter can record multiple diagnosed conditions (a 1-to-many relationship). Joining patients, encounters, and conditions into a single table causes Cartesian row duplication: an encounter with 4 conditions appears 4 times, falsely inflating total visit counts by 400% and quadrupling financial costs. Therefore, we maintain `encounter_analytics` (1 row per encounter) and `condition_analytics` (1 row per condition-encounter pair).

### Q11: How do you mathematically prove that `encounter_analytics` has no duplicate rows?
**Answer:** In Spark and Trino, we execute:
```sql
SELECT COUNT(*), COUNT(DISTINCT encounter_id) FROM iceberg.healthcare.encounter_analytics;
```
Both numbers must be strictly identical. If `COUNT(*) > COUNT(DISTINCT encounter_id)`, row explosion occurred.

### Q12: Why is `current_date()` forbidden when calculating patient age?
**Answer:** In longitudinal healthcare datasets spanning years (e.g. 2018–2024), calculating age relative to today's date produces anachronistic errors—a 5-year-old pediatric patient treated in 2019 would be erroneously categorized as a 12-year-old. Age must strictly be calculated at event time: `FLOOR(MONTHS_BETWEEN(start_time, birthdate) / 12)`.

### Q13: How does Iceberg's metadata tree work?
**Answer:** Iceberg uses a 3-level metadata hierarchy:
1. `metadata.json`: Contains table schema, partition specs, and snapshots.
2. `manifest-list.avro`: Contains the list of manifest files for a specific snapshot.
3. `manifest.avro`: Tracks individual data files, partition values, and column-level min/max statistics for partition pruning.

### Q14: How does Trino read Iceberg tables without querying Spark?
**Answer:** Trino has a native, built-in Iceberg connector. It reads the Iceberg catalog and metadata files directly from disk, identifies which Parquet files contain the requested data, and streams the columnar data into its own worker memory pipelines without involving Spark.

### Q15: How is MongoDB populated?
**Answer:** At the end of the batch pipeline, Apache Spark aggregates metrics from `encounter_analytics` and `condition_analytics`, formats them into BSON documents containing `source_table` and `generated_at` timestamps, and writes them directly into MongoDB collections via the official `mongo-spark-connector`.

### Q16: What happens if MongoDB crashes? Does the platform stop working?
**Answer:** No. Iceberg and Trino remain fully operational. Trino can still execute all SQL queries and Superset can still display live charts. Only operational client API endpoints relying on pre-aggregated MongoDB documents would be temporarily degraded.

### Q17: What happens if Trino crashes?
**Answer:** The Superset interactive dashboard will not be able to execute live SQL queries. However, the data remains safely stored in Iceberg Parquet files, Spark batch ETL can still run, and MongoDB serving collections remain accessible.

### Q18: What visual design standard is used for the dashboard, and why?
**Answer:** We implemented a **Trustworthy Clinical Light Theme** (`#F8FAFC` base, `#FFFFFF` cards, `#0072CE` sapphire blue) inspired by digital health platforms like **Medisafe** and **Jinga Life**. Dark "gaming" themes erode clinical credibility and trust in healthcare informatics.

### Q19: Is this real patient data?
**Answer:** No. It is 100% synthetic longitudinal healthcare data generated by MITRE Synthea. It mimics real-world clinical distributions and HL7 FHIR structures without containing real Protected Health Information (PHI), ensuring full HIPAA compliance.

### Q20: Does HealthInsight perform machine learning or disease diagnosis?
**Answer:** No. HealthInsight is strictly a **descriptive Big Data analytics platform**. It answers what happened (historical volumes, durations, condition prevalence, financial costs) rather than attempting clinical disease prediction, diagnostic scoring, or prescriptive treatment.

### Q21: What is hidden partitioning in Iceberg?
**Answer:** In traditional systems like Hive, partition columns are physical directories (e.g., `/year=2023/month=05/`), requiring users to explicitly include partition columns in SQL queries. In Iceberg, partitioning is a transformation over existing fields (e.g., `years(start)`). Users simply query `WHERE start >= '2023-01-01'` and Iceberg handles file pruning automatically.

### Q22: How are missing or null columns handled in raw CSVs?
**Answer:** During Spark ingestion (`01_profile_dataset.py` and `02_ingest_raw_to_iceberg.py`), null counts are tracked. Columns are strictly typed, and missing values are preserved as standard database `NULL`s without fabricating synthetic defaults (e.g. we never replace a null cost with 0.00).

### Q23: How do we prevent "works on my machine" errors across teammates?
**Answer:**
1. Zero hardcoded absolute paths (all paths are relative or configured via `.env`).
2. Always using forward slashes (`/`) for URI compatibility across Windows and Linux.
3. Providing `docker-compose.yml` so Trino and MongoDB spin up identically on any machine with one command (`docker compose up -d`).
4. Documenting Windows-specific `winutils.exe` setup in `docs/team_setup_guide.md`.

### Q24: What is the role of each team member?
**Answer:**
- **Pushkar (23BIT153):** Trino distributed SQL query architecture, query optimization, and Superset database integration.
- **Hemang (23BIT140):** Apache Spark distributed ETL pipeline, joining logic, and MongoDB document export.
- **Sachi (23BIT142):** Apache Iceberg lakehouse schema definitions, partition specifications, and table metadata management.
- **Yug (23BIT149):** Apache Superset clinical daylight dashboard, virtual datasets, and user experience.

### Q25: What is the future scope for this platform?
**Answer:** Future enhancements could include real-time streaming ingestion via Apache Kafka for live ICU vitals, implementing federated catalog integration with remote cloud catalogs via Apache Polaris, and exposing a FastAPI REST gateway over the MongoDB serving layer.
