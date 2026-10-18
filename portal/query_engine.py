"""
Trino Query Engine for HealthInsight.
Safely executes validated SELECT queries against Apache Iceberg tables.
"""
import os
import re
import time
from typing import Dict, Any, List
from dotenv import load_dotenv
import trino

load_dotenv()

TRINO_HOST = os.getenv("TRINO_HOST", "localhost")
TRINO_PORT = int(os.getenv("TRINO_PORT", "8080"))
TRINO_CATALOG = os.getenv("TRINO_CATALOG", "iceberg")
TRINO_SCHEMA = os.getenv("TRINO_SCHEMA", "healthcare")
TRINO_USER = os.getenv("TRINO_USER", "admin")

FORBIDDEN_KEYWORDS = [
    r"\bDROP\b",
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bDELETE\b",
    r"\bCREATE\b",
    r"\bALTER\b",
    r"\bTRUNCATE\b",
    r"\bREPLACE\b",
    r"\bCALL\b",
    r"\bGRANT\b",
    r"\bREVOKE\b"
]


class QuerySafetyError(Exception):
    """Raised when unsafe or non-SELECT SQL is detected."""
    pass


def validate_sql(sql: str) -> None:
    """Ensure query is safe, SELECT-only, and contains no destructive statements."""
    cleaned = re.sub(r"--.*$", "", sql, flags=re.MULTILINE)
    cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL).strip()

    if not cleaned:
        raise QuerySafetyError("Empty query provided.")

    if not re.match(r"^(SELECT|WITH)\b", cleaned, re.IGNORECASE):
        raise QuerySafetyError("Only SELECT or WITH (read-only) queries are allowed.")

    for pattern in FORBIDDEN_KEYWORDS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            raise QuerySafetyError(f"Query contains forbidden keyword matching {pattern}")


def get_trino_connection():
    """Create Trino connection with connection pooling/timeout."""
    return trino.dbapi.connect(
        host=TRINO_HOST,
        port=TRINO_PORT,
        user=TRINO_USER,
        catalog=TRINO_CATALOG,
        schema=TRINO_SCHEMA,
        request_timeout=30.0
    )


def execute_trino_query(sql: str) -> Dict[str, Any]:
    """Execute SQL query via Trino and return structured result set with telemetry."""
    validate_sql(sql)

    start_time = time.perf_counter()
    conn = get_trino_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        raw_rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        execution_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # JSON sanitization for dates, timestamps, decimals
        formatted_rows: List[List[Any]] = []
        for row in raw_rows:
            formatted_row = []
            for cell in row:
                if cell is None:
                    formatted_row.append(None)
                elif isinstance(cell, (int, float, str, bool)):
                    formatted_row.append(cell)
                else:
                    formatted_row.append(str(cell))
            formatted_rows.append(formatted_row)

        return {
            "columns": columns,
            "rows": formatted_rows,
            "row_count": len(formatted_rows),
            "execution_ms": execution_ms,
            "sql": sql
        }
    finally:
        conn.close()
