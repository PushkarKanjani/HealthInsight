# HealthInsight — Version Lock Record (Prompt 17 Final)

**Last Updated:** October 18, 2026  
**Status:** 100% Locked and Operational  

---

## 1. System & Runtime Version Audit Table

| Component | Installed Version | Required Compatibility | Status | Operational Deployment |
|---|---|---|---|---|
| **Operating System** | Windows 11 Home Single Language (Build 26100) | Windows 10/11 64-bit | **VERIFIED** | Host machine running Spark ETL & client tools |
| **Python** | 3.11.9 | Python 3.10+ | **VERIFIED** | Local Python environment |
| **PowerShell** | 5.1.26100.9711 | PowerShell 5.1+ / 7+ | **VERIFIED** | Native host automation (`scripts/run_pipeline.ps1`) |
| **Docker Engine** | Docker Desktop 4.x (WSL2 Backend) | Docker Engine 24+ | **VERIFIED** | Container orchestration for services |
| **Apache Spark** | 3.5.3 | Spark 3.5.x | **VERIFIED** | Local multi-core execution (`local[*]`) |
| **Scala Binary** | 2.12 | Scala 2.12 | **VERIFIED** | Spark 3.5.3 runtime |
| **Apache Iceberg Runtime** | `org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.2` | Iceberg 1.5.x / 1.8.x | **VERIFIED** | Loaded via Ivy/Maven coordinates |
| **Trino** | 435 | Trino 435+ | **VERIFIED** | Docker container (`healthinsight-trino`, port 8080) |
| **MongoDB** | 7.0 Community | MongoDB 7.0+ | **VERIFIED** | Docker container (`healthinsight-mongodb`, port 27017) |
| **PySpark (pip)** | 3.5.3 | `pyspark==3.5.3` | **VERIFIED** | Local Python environment |
| **PyMongo (pip)** | 4.19.0 | `pymongo>=4.8.0` | **VERIFIED** | Local Python environment |
| **trino-python-client** | 0.340.0 | `trino>=0.330.0` | **VERIFIED** | Host Python & Superset container |
| **Apache Superset** | 3.1.0 | Superset 3.1.x / 4.x | **VERIFIED** | Docker container (`healthinsight-superset`, port 8088) |

---

## 2. Cross-Component Compatibility Verification

- **Iceberg Storage Protocol:** Spark writes tables using `file:/warehouse` resolved via Windows Junction `C:\warehouse -> iceberg\warehouse`. Inside the Trino Docker container, `/warehouse` is mounted directly, ensuring 100% path parity across Windows and Linux.
- **Trino Catalog Type:** Trino 435 connects to Iceberg using `connector.name=iceberg` with `iceberg.catalog.type=TESTING_FILE_METASTORE` and `hive.metastore.catalog.dir=/warehouse`.
- **Superset Trino Driver:** Superset communicates via SQLAlchemy URI `trino://admin@trino:8080/iceberg/healthcare` using the internal Docker bridge network.
- **MongoDB Connector:** MongoDB 7.0 receives pre-aggregated collections exported via PyMongo and Spark without schema locking.
