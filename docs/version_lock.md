# HealthInsight — Version Lock Record (Prompt 01)
**Last Updated:** 2026-10-18  
**Audit Executed by:** Prompt 01 Automated Environment Audit  

> **Non-Negotiable Rule:** Never invent a version. If a command or tool is unavailable, it is documented as unavailable.

---

## 1. System & Runtime Version Audit Table

| Component | Installed Version | Required Compatibility | Status | Action Required |
|---|---|---|---|---|
| **Operating System** | Windows 11 Home Single Language (Build 26100) | Windows 10/11 64-bit | **VERIFIED** | Host OS ready. |
| **PowerShell** | 5.1.26100.9711 | PowerShell 5.1+ / 7+ | **VERIFIED** | Native scripting ready. |
| **Python** | Python 3.11.9 | Python 3.10+ | **VERIFIED** | Compatible with PySpark 3.5 & Pandas. |
| **Java** | *Not found in PATH* | Java 17 LTS (Temurin/OpenJDK) | ⚠️ **PENDING** | Install OpenJDK 17 & set `JAVA_HOME`. |
| **Apache Spark** | *Not found in PATH* | Spark 3.5.x (pre-built for Hadoop 3) | ⚠️ **PENDING** | Install Spark 3.5 & set `SPARK_HOME`. |
| **Scala Binary** | Target: 2.12 | Scala 2.12 (matching Spark 3.5) | ⚠️ **PENDING** | Locked to 2.12 for runtime JARs. |
| **Iceberg Runtime JAR** | Target: `iceberg-spark-runtime-3.5_2.12-1.8.1.jar` | Iceberg 1.8.x for Spark 3.5_2.12 | ⚠️ **PENDING** | Download JAR to local jars folder. |
| **Trino** | *Not found in PATH* | Trino 435+ (Server & CLI) | ⚠️ **PENDING** | Install Trino server or run container. |
| **MongoDB** | *Not found in PATH* | MongoDB Community 7.0+ | ⚠️ **PENDING** | Install MongoDB Community Server. |
| **MongoDB Shell** | *Not found in PATH* | mongosh 2.x | ⚠️ **PENDING** | Install MongoDB Shell (`mongosh`). |
| **MongoDB Spark Connector** | Target: `mongo-spark-connector_2.12-10.4.0.jar` | Mongo Spark Connector for 3.5_2.12 | ⚠️ **PENDING** | Download JAR to local jars folder. |
| **PySpark (pip)** | `3.5.3` | `pyspark==3.5.3` | **VERIFIED** | Core distributed computing library installed. |
| **PyMongo (pip)** | `4.19.0` | `pymongo>=4.8.0` | **VERIFIED** | MongoDB Python client installed. |
| **trino-python-client** | `0.340.0` | `trino>=0.330.0` | **VERIFIED** | Trino Python client & SQLAlchemy dialect installed. |
| **Apache Superset** | *Isolated venv required* | Superset 4.0+ in `venv-superset` | ⚠️ **PENDING** | Setup in isolated `venv-superset`. |

---

## 2. JAR Compatibility Lock Matrix

| Engine | Compatible Scala | Required Iceberg JAR | Required Mongo Connector JAR |
|---|---|---|---|
| **Spark 3.5.x** | **Scala 2.12** | `iceberg-spark-runtime-3.5_2.12-1.8.1.jar` | `mongo-spark-connector_2.12-10.4.0.jar` |

> [!WARNING]
> If Spark 3.4 or 3.3 is used instead of 3.5, or if Scala 2.13 is used instead of 2.12, the Iceberg and Mongo JARs will throw `ClassNotFoundException` or `NoSuchMethodError` during execution. These versions must remain locked together.

---

## 3. Audit Verification Evidence

- Executed `scripts/check_versions.ps1` on Windows host.
- Python 3.11.9 confirmed at `C:\Program Files\Python311\python.exe`.
- Java, Spark, Trino, and MongoDB are currently absent from the system `PATH`.
