# HealthInsight v2 — AI Clinical Command Center
## Master Build Plan (Prompts 23–32)

**Prepared:** October 18, 2026
**Status:** APPROVED FOR EXECUTION
**Rule:** Zero disruption to v1 Lakehouse (Spark / Iceberg / Trino / MongoDB).

---

## Vision

> Transform HealthInsight from a batch analytics dashboard into a **premium, AI-powered Clinical Intelligence Platform** — a glass-morphic, Three.js-animated, JWT-authenticated web portal where healthcare professionals ask questions in plain English and receive distributed analytics answers powered by Apache Spark, Apache Iceberg, Trino, and MongoDB.

---

## Technology Stack (v2 Additions Only)

| Layer | Tool | Purpose |
|---|---|---|
| **Backend API** | FastAPI + Uvicorn | Lightweight async REST gateway (`localhost:5000`) |
| **Authentication** | PyJWT (HS256) | Stateless JWT tokens — login, all `/api/*` protected |
| **AI Engine** | Google Gemini (`gemini-2.0-flash`) via `google-genai` SDK | Natural language → Trino SQL translation |
| **Fallback Engine** | Deterministic keyword router (Python) | Offline-safe: 12 hardcoded clinical queries always work without internet |
| **Distributed SQL** | Trino 435 via `trino-python-client` | Executes generated SQL over 321,000 Iceberg records |
| **Serving Store** | MongoDB 7.0 via `pymongo` | Sub-2ms patient profile and KPI lookups |
| **Frontend** | HTML5 + Vanilla CSS3 + Vanilla ES6 JS | Zero build tools, instant load |
| **3D Background** | Three.js r160 (CDN) | WebGL liquid/water flow cursor reactive animation |
| **Smooth Scroll** | Lenis v1.1.1 (CDN) | Apple-class silky scroll momentum |
| **Charts** | Chart.js v4.4 (CDN) | Dynamic bar, donut, line charts from query results |
| **Typography** | Inter + Outfit (Google Fonts CDN) | Clinical precision aesthetic |

---

## Folder Structure (v2 additions inside `portal/`)

```
HealthInsight/
├── portal/                         ← NEW (v2 AI Command Center)
│   ├── server.py                   ← FastAPI backend entry point (port 5000)
│   ├── auth.py                     ← JWT authentication logic
│   ├── query_engine.py             ← Trino query executor + SQL safety validator
│   ├── ai_engine.py                ← Gemini Text-to-SQL + deterministic fallback
│   ├── mongo_service.py            ← MongoDB patient lookup + KPI service
│   ├── schema_context.py           ← Iceberg table schema strings for Gemini prompts
│   └── static/
│       ├── index.html              ← Login page (glassmorphic + Three.js bg)
│       ├── dashboard.html          ← AI Command Center (3 tabs)
│       ├── style.css               ← Global design system (Clinical Glass Dark)
│       ├── three-scene.js          ← WebGL liquid cursor animation
│       ├── auth.js                 ← JWT token management (localStorage)
│       ├── chat.js                 ← AI Copilot chat interface + Chart.js rendering
│       └── monitor.js              ← Lakehouse health status monitor
│
├── spark/                          ← UNCHANGED (v1)
├── trino/                          ← UNCHANGED (v1)
├── superset/                       ← UNCHANGED (v1)
├── docs/                           ← Updated (v2 docs added)
├── scripts/                        ← Updated (portal start script added)
└── docker-compose.yml              ← Unchanged (portal runs on host, not Docker)
```

---

## UI Design System: "Clinical Glass Dark"

```
Background Canvas:     #050B18   Deep Navy — WebGL depth field
Glass Card:            rgba(255,255,255,0.04)  + backdrop-filter: blur(24px)
Glass Border:          rgba(255,255,255,0.08)
Glass Hover:           rgba(255,255,255,0.07)
Primary Accent:        #00D4FF   Electric Cyan — CTAs and active states
AI Accent:             #7C3AED   Royal Violet — AI Copilot elements
Success:               #10B981   Emerald — Connected / Healthy indicators
Warning:               #F59E0B   Amber — Caution / Partial
Error:                 #EF4444   Crimson — Disconnected / Failed
Text Primary:          #F0F6FF   Ice White
Text Secondary:        #94A3B8   Slate Grey
Font Heading:          Outfit 700
Font Body:             Inter 400/500
Border Radius:         16px (cards), 12px (inputs), 24px (pills)
```

### Three.js Liquid Cursor Animation
- 8,000 micro-particle field on a `#050B18` deep navy canvas.
- Mouse proximity creates fluid displacement ripple (GPU vertex shader).
- Particles near the cursor flow and orbit, then return elastically.
- Runs at 60fps on any modern GPU via `requestAnimationFrame`.

---

## The 3 Dashboard Sections

### Section 1: "Ask HealthInsight" — AI Copilot (Powered by Trino + Gemini)

```
┌──────────────────────────────────────────────────────────────┐
│  🤖  Ask HealthInsight Clinical Copilot     [● Trino Live]   │
├──────────────────────────────────────────────────────────────┤
│  Quick Questions:                                            │
│  [Top 10 conditions] [Cost by class] [Age groups] [Trends]  │
├──────────────────────────────────────────────────────────────┤
│  [Chat Thread — scrollable with Lenis]                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 🙋 "What is the most expensive encounter type?"      │   │
│  │ 🤖 Translating to Trino SQL...                       │   │
│  │ ┌─────────────────────────────────────────────────┐  │   │
│  │ │ SELECT encounter_class,                         │  │   │
│  │ │   ROUND(AVG(total_claim_cost),2) AS avg_cost    │  │   │
│  │ │ FROM iceberg.healthcare.encounter_analytics     │  │   │
│  │ │ GROUP BY encounter_class ORDER BY avg_cost DESC │  │   │
│  │ └─────────────────────────────────────────────────┘  │   │
│  │ ⚡ 0.41s | 321,528 rows scanned | 6 results          │   │
│  │ [📋 Copy SQL]  [📊 Chart]  [⬇️ Export CSV]           │   │
│  └──────────────────────────────────────────────────────┘   │
├──────────────────────────────────────────────────────────────┤
│  [ Ask a clinical question in plain English...  ] [ Ask → ] │
└──────────────────────────────────────────────────────────────┘
```

### Section 2: "Lakehouse Monitor" — System Health

```
┌────────────────────────────────────────────────────────────────┐
│  HEALTHINSIGHT LAKEHOUSE STATUS                                │
├───────────────────────┬────────────────────────────────────────┤
│  ● Trino MPP Engine   │ HEALTHY | 321,528 records | 0.4s avg  │
│  ● Apache Iceberg     │ HEALTHY | 6 tables registered         │
│  ● MongoDB Serving    │ HEALTHY | 6 collections | sub-2ms     │
│  ● AI Copilot         │ ONLINE  | Gemini + Fallback Active     │
└───────────────────────┴────────────────────────────────────────┘
```

### Section 3: "Patient Explorer" — MongoDB Instant Lookup

```
┌──────────────────────────────────────────────────────────────┐
│  🔍  Patient Journey Explorer              [● MongoDB Live]  │
├──────────────────────────────────────────────────────────────┤
│  [ Enter synthetic patient ID...  ] [ Explore → ]           │
├──────────────────────────────────────────────────────────────┤
│  Patient Card    │  Encounter Timeline  │  Condition History │
└──────────────────────────────────────────────────────────────┘
```

---

## Prompt Execution Plan (10 Prompts → 10 Commits)

### Prompt 23 — FastAPI Backend + JWT Auth
**Files:** `portal/server.py`, `portal/auth.py`
**Deliverables:** `POST /auth/login`, `GET /api/health` (JWT required), CORS configured.
**Verify:** `curl -X POST http://localhost:5000/auth/login -d '{"username":"admin","password":"healthinsight2024"}'` returns `{"access_token": "..."}`
**Commit:** `feat(portal): fastapi backend with jwt authentication`

### Prompt 24 — Query Engine + Trino Integration
**Files:** `portal/query_engine.py`, `portal/schema_context.py`
**Deliverables:** `POST /api/query/sql` executes Trino SQL safely (SELECT-only guard).
**Verify:** POST raw SQL → returns rows array + execution_time_ms.
**Commit:** `feat(portal): trino query engine with sql safety validation`

### Prompt 25 — Gemini AI + Deterministic Fallback Engine
**Files:** `portal/ai_engine.py`
**Deliverables:** `POST /api/query/natural` converts text → SQL → Trino results. 12 offline fallbacks.
**Verify:** POST `"top 5 conditions by frequency"` → returns generated_sql + data.
**Commit:** `feat(portal): gemini text-to-sql engine with offline fallback`

### Prompt 26 — MongoDB Service Layer
**Files:** `portal/mongo_service.py`
**Deliverables:** `GET /api/kpis`, `GET /api/patient/{id}`.
**Verify:** KPI endpoint returns in <10ms. Patient lookup returns demographic + history.
**Commit:** `feat(portal): mongodb service layer for kpi and patient endpoints`

### Prompt 27 — Design System CSS + Three.js Liquid Scene
**Files:** `portal/static/style.css`, `portal/static/three-scene.js`
**Deliverables:** Full CSS design token system. WebGL liquid cursor animation at 60fps.
**Verify:** Open `portal/static/index.html` in browser → animated background visible.
**Commit:** `feat(portal): clinical glass dark design system with threejs liquid cursor`

### Prompt 28 — Login Page (Glassmorphic + Three.js + JWT)
**Files:** `portal/static/index.html`, `portal/static/auth.js`
**Deliverables:** Full-screen login over Three.js bg. `admin/healthinsight2024` → JWT stored → redirect.
**Verify:** Login succeeds → `localStorage` has `hi_token` → lands on `dashboard.html`.
**Commit:** `feat(portal): glassmorphic login page with threejs background`

### Prompt 29 — Dashboard Shell + Lenis Scroll + Status Monitor
**Files:** `portal/static/dashboard.html`, `portal/static/monitor.js`
**Deliverables:** 3-section layout. Header with user info + logout. Lenis smooth scroll. Status cards polling `/api/health`.
**Verify:** All 3 status indicators show HEALTHY. Scroll is momentum-based.
**Commit:** `feat(portal): dashboard shell with lenis scroll and system monitor`

### Prompt 30 — AI Copilot Chat Interface + Chart.js
**Files:** `portal/static/chat.js` (merged into dashboard)
**Deliverables:** Chat thread with SQL code block, data table, Chart.js bar/donut, Copy SQL, Export CSV, Quick chips.
**Verify:** Type "age group distribution" → chart renders with real Trino data.
**Commit:** `feat(portal): ai copilot chat ui with chartjs visualization`

### Prompt 31 — Patient Explorer Tab
**Files:** Patient lookup component (inside dashboard.html + monitor.js)
**Deliverables:** Patient ID search → demographic card (age, gender, race, city) + encounter count + top conditions from MongoDB.
**Verify:** Known patient ID returns full card in <100ms.
**Commit:** `feat(portal): patient explorer with mongodb instant lookup`

### Prompt 32 — Final Integration, Docs & Git Freeze
**Files:** `scripts/start_portal.ps1`, `scripts/start_portal.sh`, updated `README.md`, `docs/v2_build_plan.md`
**Deliverables:** One-command portal start. Updated README with v2 architecture diagram. Final Git tag.
**Verify:** `python portal/server.py` → all endpoints live → full demo flow verified.
**Commit:** `feat(portal): complete v2 ai portal integration and documentation freeze`

---

## Absolute Non-Negotiable Rules

1. **Zero Breaking Changes to v1:** No edits to `spark/`, `trino/`, `docker-compose.yml`, or Iceberg warehouse.
2. **SELECT-Only SQL Guard:** The query engine must reject any SQL containing `DROP`, `INSERT`, `UPDATE`, `DELETE`, `CREATE`, `TRUNCATE`.
3. **Fallback-First Design:** 12 clinical queries must work 100% offline without any API key.
4. **JWT on All API Routes:** Every `/api/*` endpoint must return `401 Unauthorized` without a valid Bearer token.
5. **Real Data Only:** Every number rendered in the portal must come from live Trino or MongoDB.
6. **60fps WebGL Guarantee:** Three.js uses GPU vertex shaders. No CPU pixel-level DOM manipulation.
7. **Gemini API Key in `.env` only:** Never hardcoded in any Python or JS file.
