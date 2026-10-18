#!/usr/bin/env bash
set -eo pipefail

echo "========================================="
echo " HealthInsight Environment & Version Audit"
echo "========================================="

echo -e "\n[1] OS Kernel:"
uname -a 2>/dev/null || echo "uname not available"

echo -e "\n[2] Python Version:"
python3 --version 2>/dev/null || python --version 2>/dev/null || echo "Python not found"

echo -e "\n[3] Java Version:"
java -version 2>&1 || echo "Java not found"

echo -e "\n[4] Apache Spark (spark-submit):"
spark-submit --version 2>&1 || echo "spark-submit not found"

echo -e "\n[5] Trino CLI:"
trino --version 2>&1 || echo "trino not found"

echo -e "\n[6] MongoDB Server (mongod):"
mongod --version 2>&1 || echo "mongod not found"

echo -e "\n[7] MongoDB Shell (mongosh):"
mongosh --version 2>&1 || echo "mongosh not found"

echo -e "\n========================================="
