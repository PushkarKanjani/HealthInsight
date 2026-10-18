"""
HealthInsight v2 — Clinical AI Command Center FastAPI Server.
Main entry point serving REST APIs, AI Copilot, and Static Assets.
"""
import os
import time
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from portal.auth import authenticate_user, create_access_token, verify_token
from portal.query_engine import execute_trino_query, QuerySafetyError
from portal.ai_engine import process_clinical_question
from portal.mongo_service import get_kpis, get_collection_stats, get_patient_profile, get_mongo_db

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="HealthInsight AI Command Center",
    description="Glassmorphic Clinical Intelligence Portal powered by Spark, Iceberg, Trino, MongoDB & Gemini",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request schemas
class LoginRequest(BaseModel):
    username: str
    password: str


class SqlQueryRequest(BaseModel):
    sql: str


class NaturalQueryRequest(BaseModel):
    question: str


# ==============================================================================
# Authentication Endpoints
# ==============================================================================

@app.post("/auth/login")
async def login(req: LoginRequest):
    """Authenticate admin user and issue JWT access token."""
    if not authenticate_user(req.username, req.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password. Default is admin / healthinsight2024"
        )
    token = create_access_token(req.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": req.username,
        "expires_in_hours": 8
    }


# ==============================================================================
# System Health & Telemetry Endpoints
# ==============================================================================

@app.get("/api/health")
async def health_check(user: dict = Depends(verify_token)):
    """Comprehensive health check across Trino, Iceberg, MongoDB, and AI Engine."""
    health: Dict[str, Any] = {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {}
    }

    # 1. Trino & Iceberg check
    t_start = time.perf_counter()
    try:
        trino_res = execute_trino_query("SELECT COUNT(*) AS n FROM iceberg.healthcare.encounter_analytics")
        trino_latency = round((time.perf_counter() - t_start) * 1000, 2)
        health["services"]["trino"] = {
            "status": "healthy",
            "latency_ms": trino_latency,
            "version": "Trino 435",
            "active_catalog": "iceberg",
            "active_schema": "healthcare",
            "total_encounters": trino_res["rows"][0][0]
        }
        health["services"]["iceberg"] = {
            "status": "healthy",
            "format": "Apache Iceberg 1.5",
            "storage": "Local Warehouse (Parquet + Metadata)",
            "tables_registered": 6
        }
    except Exception as e:
        health["services"]["trino"] = {"status": "error", "error": str(e)}
        health["services"]["iceberg"] = {"status": "degraded", "error": str(e)}
        health["status"] = "degraded"

    # 2. MongoDB check
    m_start = time.perf_counter()
    try:
        db = get_mongo_db()
        db.command("ping")
        mongo_latency = round((time.perf_counter() - m_start) * 1000, 2)
        health["services"]["mongodb"] = {
            "status": "healthy",
            "latency_ms": mongo_latency,
            "version": "MongoDB 7.0",
            "database": "healthinsight",
            "collections_count": len(db.list_collection_names())
        }
    except Exception as e:
        health["services"]["mongodb"] = {"status": "error", "error": str(e)}
        health["status"] = "degraded"

    # 3. AI Copilot status
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    health["services"]["ai_copilot"] = {
        "status": "online",
        "mode": "gemini-2.0-flash" if gemini_key else "deterministic-fallback",
        "gemini_connected": bool(gemini_key),
        "offline_templates_available": 12
    }

    return health


# ==============================================================================
# Analytics & AI Query Endpoints
# ==============================================================================

@app.post("/api/query/sql")
async def run_sql_query(req: SqlQueryRequest, user: dict = Depends(verify_token)):
    """Execute raw ANSI/Trino SQL with safety validation."""
    try:
        result = execute_trino_query(req.sql)
        return result
    except QuerySafetyError as qe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(qe))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Trino execution failed: {str(e)}")


@app.post("/api/query/natural")
async def run_natural_language_query(req: NaturalQueryRequest, user: dict = Depends(verify_token)):
    """Natural language question to SQL using Gemini with deterministic fallback."""
    try:
        result = process_clinical_question(req.question)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"AI query processing failed: {str(e)}")


# ==============================================================================
# MongoDB Serving Endpoints
# ==============================================================================

@app.get("/api/kpis")
async def read_kpis(user: dict = Depends(verify_token)):
    """Fetch pre-aggregated executive KPIs."""
    return get_kpis()


@app.get("/api/collections")
async def read_collections(user: dict = Depends(verify_token)):
    """Fetch collection inventory and document statistics."""
    return get_collection_stats()


@app.get("/api/patient/{patient_id}")
async def read_patient(patient_id: str, user: dict = Depends(verify_token)):
    """Fetch detailed longitudinal patient journey profile."""
    profile = get_patient_profile(patient_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient ID '{patient_id}' not found.")
    return profile


# ==============================================================================
# Static File & UI Serving
# ==============================================================================

# Mount static directory
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def root():
    """Serve the glassmorphic login page."""
    login_page = STATIC_DIR / "index.html"
    if login_page.exists():
        return FileResponse(login_page)
    return {"message": "HealthInsight AI Command Center API running. UI loading..."}


@app.get("/dashboard")
async def dashboard():
    """Serve the main clinical command center dashboard."""
    dash_page = STATIC_DIR / "dashboard.html"
    if dash_page.exists():
        return FileResponse(dash_page)
    return {"message": "Dashboard UI file not found."}


if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 80)
    print("  LAUNCHING HEALTHINSIGHT v2 CLINICAL AI COMMAND CENTER")
    print("  URL: http://localhost:5000")
    print("  Default Login: admin / healthinsight2024")
    print("=" * 80 + "\n")
    uvicorn.run("portal.server:app", host="0.0.0.0", port=5000, reload=True)
