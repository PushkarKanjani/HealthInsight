# HealthInsight — Final Handover Document

**Last Updated:** October 18, 2026
**Status:** v1 FROZEN | v2 IN PROGRESS

---

## Quick Reference — Service URLs

| Service | URL | Credentials |
|---|---|---|
| **Trino Web UI** | http://localhost:8080 | `admin` (no password) |
| **MongoDB** | mongodb://localhost:27017 | No auth |
| **Apache Superset** | http://localhost:8088 | `admin` / `admin` |
| **AI Portal (v2)** | http://localhost:5000 | `admin` / `healthinsight2024` |

---

## v1 Pipeline — Verified Metrics

| Metric | Value |
|---|---|
| Total Patients | 12,352 |
| Total Encounters (`encounter_analytics`) | 321,528 |
| Total Condition Events (`condition_analytics`) | 114,544 |
| Iceberg Tables Registered in Trino | 6 |
| MongoDB Collections Populated | 6 |
| Superset Dashboard Charts | 6 |

### MongoDB Collections

| Collection | Document Count | Description |
|---|---|---|
| `kpis` | 1 | Top-level platform KPIs |
| `encounter_class_summary` | 6 | Encounter class statistics |
| `age_group_summary` | 6 | Age group analytics |
| `top_conditions` | 10 | Most prevalent conditions |
| `monthly_trend` | ~60 | Encounters per month |
| `patient_profiles` | 12,352 | Per-patient demographic + encounter summary |

---

## v1 Trino Verification Queries

```sql
-- Record counts
SELECT COUNT(*) FROM iceberg.healthcare.encounter_analytics;   -- 321,528
SELECT COUNT(*) FROM iceberg.healthcare.condition_analytics;   -- 114,544

-- Top encounter classes by volume
SELECT encounter_class, COUNT(*) AS count
FROM iceberg.healthcare.encounter_analytics
GROUP BY encounter_class ORDER BY count DESC;

-- Most prevalent conditions
SELECT description, COUNT(*) AS cases
FROM iceberg.healthcare.condition_analytics
GROUP BY description ORDER BY cases DESC LIMIT 10;
```

---

## v2 Portal Setup Checklist

- [ ] `PORTAL_JWT_SECRET` set in `.env` (change from default).
- [ ] `GEMINI_API_KEY` set in `.env` (optional — offline fallback works without it).
- [ ] Docker services running: `docker compose up -d trino mongodb`.
- [ ] Portal started: `python -m uvicorn portal.server:app --port 5000 --reload`.
- [ ] Login verified: `admin` / `healthinsight2024`.
- [ ] AI Copilot test: "Top 10 conditions by frequency" returns real Trino data.
- [ ] Patient Explorer test: valid synthetic patient ID returns demographic card.

---

## Repository Structure

```
HealthInsight/
├── .env                        ← Local secrets (not committed)
├── .env.example                ← Template with all required vars
├── docker-compose.yml          ← MongoDB + Trino + Superset services
├── requirements.txt            ← All Python deps (v1 + v2)
├── README.md                   ← Full platform documentation
├── PROMPT_BOOK.md              ← AI build instructions (Prompts 00–32)
│
├── spark/                      ← v1: Distributed ETL scripts
│   ├── 00_test_iceberg.py
│   ├── 01_profile_dataset.py
│   ├── 02_ingest_raw_to_iceberg.py
│   ├── 03_build_analytics_tables.py
│   └── 04_export_mongodb.py
│
├── trino/                      ← v1: Trino catalog + verification queries
│   ├── catalog/                ← iceberg.properties
│   └── queries/                ← SQL verification scripts
│
├── iceberg/                    ← v1: Iceberg warehouse (Parquet + metadata)
│   └── warehouse/
│
├── mongodb/                    ← v1: MongoDB init scripts
│
├── superset/                   ← v1: Superset Docker config + setup
│
├── portal/                     ← v2: AI Command Center (to be built)
│   ├── server.py
│   ├── auth.py
│   ├── query_engine.py
│   ├── ai_engine.py
│   ├── mongo_service.py
│   ├── schema_context.py
│   └── static/
│       ├── index.html
│       ├── dashboard.html
│       ├── style.css
│       ├── three-scene.js
│       └── auth.js
│
├── scripts/                    ← Pipeline + portal start scripts
│   ├── run_pipeline.ps1
│   ├── run_pipeline.sh
│   ├── start_portal.ps1        ← (to be created in Prompt 32)
│   └── start_portal.sh         ← (to be created in Prompt 32)
│
└── docs/                       ← All documentation
    ├── DOC1_PRD_TECHSTACK_ARCHITECTURE.md
    ├── DOC2_TRD_DB_PIPELINE.md
    ├── DOC3_UI_BRIEF_DEMO_VIVA.md
    ├── v2_build_plan.md        ← v2 implementation plan
    ├── final_handover.md       ← This file
    ├── architecture.md
    ├── data_lineage.md
    ├── dataset_dictionary.md
    ├── analytics_support_matrix.md
    ├── mongodb_verification.md
    ├── project_audit.md
    ├── team_setup_guide.md
    ├── version_lock.md
    └── viva_questions.md
```

---

## Git Commit History

| Phase | Commits | Description |
|---|---|---|
| **v1 Prompts 00–22** | 15 commits | Full Lakehouse: Spark ETL, Iceberg tables, Trino SQL, MongoDB, Superset |
| **v2 Prompts 23–32** | 10 commits (planned) | AI Portal: FastAPI, JWT, Gemini, Three.js UI |

---

## Known Working Versions (Locked)

| Tool | Version |
|---|---|
| Python | 3.11.9 |
| PySpark | 3.5.3 |
| Apache Iceberg Runtime | 1.5.2 |
| Trino (Docker) | 435 |
| MongoDB (Docker) | 7.0 |
| Apache Superset (Docker) | 3.1.x |
| FastAPI | 0.115.0 |
| PyJWT | 2.10.1 |
| google-genai SDK | 1.21.0 |
