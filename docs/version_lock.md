# HealthInsight — Version Lock Record

> Fill this in after actual installation.
> Do not guess. Run `scripts/check_versions.sh` to collect values.
> Record the exact JAR filenames used.

| Component | Installed Version | Notes |
|---|---|---|
| Java | | Required: 17 LTS |
| Python | | Required: 3.10+ |
| Scala binary | | Required: 2.12 (for Spark 3.5.x) |
| Apache Spark | | Target: 3.5.x |
| Iceberg Runtime JAR | | Filename: `iceberg-spark-runtime-3.5_2.12-?.jar` |
| Trino | | Target: 435+ |
| MongoDB | | Target: 7.0+ |
| MongoDB Spark Connector JAR | | Filename: `mongo-spark-connector_2.12-?.jar` |
| PySpark (pip) | | Must match Spark version |
| PyMongo (pip) | | Target: 4.10.x |
| trino (pip) | | Superset env only |
| Apache Superset | | Superset env only |

## JAR Compatibility Rules

- Iceberg runtime JAR must match **Spark minor version** (3.5) and **Scala binary version** (2.12).
- MongoDB Spark Connector must match **Spark 3.x** and **Scala 2.12**.
- If you change Spark version, you must download matching JARs.

## Environment Notes

(fill in after setup)

- Pipeline virtual env path:
- Superset virtual env path:
- Trino installation path:
- MongoDB data directory:
- Iceberg warehouse absolute path:
