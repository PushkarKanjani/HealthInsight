# VitalStream × Antigravity — Master Build Prompt

**For:** Antigravity agents  
**Project:** VitalStream (perioperative command center)  
**Mode:** Auto-execution with user decision prompts  
**Deadline:** Tomorrow (24 hours)  

---

## REFERENCE DOCUMENTS (Read These First)

You have 6 documents. Reference them as needed:

1. **README_START_HERE.md**
   - Quick overview, member roles, demo script, talking points
   - Use: To understand what the user expects

2. **ANTIGRAVITY_SETUP.md**
   - Decision tree, phase flow, troubleshooting
   - Use: To know what to show the user at each milestone

3. **PROMPT_BOOK.md**
   - Detailed phase breakdown, automated steps, checkpoints
   - Use: Exact implementation steps for each phase

4. **TEAM_CONTRACTS.md**
   - Member tasks, MongoDB collections, API endpoints, Kafka topics, Flink jobs, Cassandra schema
   - Use: Technical requirements for each component

5. **TECH_STACK.md**
   - Docker Compose, versions, code snippets, color palette, requirements
   - Use: Complete technical specifications

6. **TOOL_ROLES_SIMPLE.md**
   - Simple explanations (MongoDB stores, Kafka streams, etc.)
   - Use: Understanding the why behind each tool

---

## INITIALIZATION (Run This First)

```
╔════════════════════════════════════════════════════════════════════╗
║         VitalStream Setup — User Decisions Required                ║
╚════════════════════════════════════════════════════════════════════╝

Welcome! You're about to build a 4-tool big data healthcare project.
This prompt will automate 95% of the work. You just decide yes/no.

Total time: ~8 hours of automation + parallel member work
Your interaction: ~10 minutes of decisions + milestone confirmations

Let's start with 4 quick decisions:
```

### PROMPT_001: Decision 1 — Cleanup Old Files

```
┌─────────────────────────────────────────────────────────────┐
│ DECISION 1: Clean up old HealthInsight files?              │
│                                                              │
│ This will remove:                                            │
│   /spark /iceberg /trino /superset /mongodb /scripts        │
│   docker-compose.yml, requirements.txt, README.md, etc.     │
│                                                              │
│ You'll keep: .git (history), .gitignore, .env.example       │
│                                                              │
│ [YES] → Delete old files, start fresh (RECOMMENDED)         │
│ [NO]  → Keep old files, build alongside                     │
│                                                              │
│ Your answer: _______________                                │
└─────────────────────────────────────────────────────────────┘
```

**If user enters: YES**
```bash
# Automated cleanup
rm -rf ./data ./docs ./iceberg ./mongodb ./portal ./screenshots ./scripts ./spark ./superset ./trino
rm -f .env docker-compose.yml requirements.txt README.md PROMPT_BOOK.md
git add -A
git commit -m "cleanup: remove HealthInsight v1, prepare for VitalStream"

echo "✓ Old files removed. Ready for VitalStream."
```

**If user enters: NO**
```bash
echo "✓ Keeping old files. VitalStream will use new folder structure."
```

---

### PROMPT_002: Decision 2 — Data Source

```
┌─────────────────────────────────────────────────────────────┐
│ DECISION 2: Data source for vital signs?                   │
│                                                              │
│ [SYNTHETIC]                                                  │
│   └─ AI-generated vitals based on rules                     │
│   └─ Ready in 2 minutes (no download)                       │
│   └─ Good for: Fast setup, tomorrow's deadline              │
│   └─ Quality: Controlled scenarios (stable, low BP, etc.)   │
│                                                              │
│ [VITALDB]                                                    │
│   └─ Real surgical recordings (6,388 cases)                 │
│   └─ Takes 5+ minutes (download ~5GB on 10Mbps)             │
│   └─ Good for: Credible, impressive, realistic              │
│   └─ Quality: Real intraoperative monitoring (500 Hz)       │
│                                                              │
│ Recommended for tomorrow: SYNTHETIC                          │
│                                                              │
│ Your answer: _______________                                │
└─────────────────────────────────────────────────────────────┘
```

**Store choice:** `DATA_SOURCE = user_input`

---

### PROMPT_003: Decision 3 — Time-Series Database

```
┌─────────────────────────────────────────────────────────────┐
│ DECISION 3: Database for vitals (518k readings/day)?        │
│                                                              │
│ First, tell us: How much RAM on your demo machine?          │
│ (Available RAM in GB): _______________                       │
│                                                              │
│ [CASSANDRA]                                                  │
│   └─ Distributed, scales horizontally                       │
│   └─ RAM: 2–3 GB (for demo)                                 │
│   └─ Speed: Moderate (~30 sec startup)                      │
│   └─ Best for: Production-like setup, scale-out story       │
│   └─ Recommended if: RAM ≥ 6GB                              │
│                                                              │
│ [TIMESCALEDB]                                                │
│   └─ PostgreSQL extension (lighter)                         │
│   └─ RAM: <1 GB                                             │
│   └─ Speed: Fast (~10 sec startup)                          │
│   └─ Best for: Limited RAM, simpler setup                   │
│   └─ Recommended if: RAM < 6GB                              │
│                                                              │
│ Your answer: _______________                                │
└─────────────────────────────────────────────────────────────┘
```

**Auto-decide (if user unsure):**
```
IF RAM >= 6 THEN DB = CASSANDRA
ELSE DB = TIMESCALEDB
```

**Store choice:** `TIME_SERIES_DB = user_input OR auto_decision`

---

### PROMPT_004: Decision 4 — Start Now?

```
┌─────────────────────────────────────────────────────────────┐
│ DECISION 4: Start Phase 1 immediately?                      │
│                                                              │
│ Phase 1 takes ~45 minutes:                                   │
│   • Create folder structure                                  │
│   • Generate docker-compose.yml (with your DB choice)       │
│   • Start all services (Kafka, MongoDB, Flink, etc.)        │
│   • Initialize databases                                     │
│                                                              │
│ [YES] → Begin now (you'll be done with Phase 1 in 45 min)   │
│ [NO]  → Pause, I'll resume when you say                     │
│                                                              │
│ Your answer: _______________                                │
└─────────────────────────────────────────────────────────────┘
```

**If user enters: YES** → Jump to PHASE_1_EXECUTION  
**If user enters: NO** → PAUSE_STATE (await resume signal)

---

## PHASE EXECUTION

### PHASE 1: Folder Structure + Docker (Auto-run, ~45 min)

**Entry point:** After Decision 4 = YES

```
════════════════════════════════════════════════════════════════════
PHASE 1: Folder Structure + Docker Setup
════════════════════════════════════════════════════════════════════

Starting automated setup...

[1/6] Creating folder structure...
```

**Ref:** PROMPT_BOOK.md → PHASE1_001 through PHASE1_007

**Steps:**

1. **Create folders**
   ```bash
   mkdir -p backend/app/api backend frontend/src/{components,hooks,context} \
            simulator flink/{jobs,config} scripts
   echo "✓ Folders created"
   ```

2. **Generate docker-compose.yml**
   - Reference: TECH_STACK.md (docker-compose section)
   - Swap database:
     - If DB = CASSANDRA: include cassandra service
     - If DB = TIMESCALEDB: include timescaledb service (PostgreSQL)
   - Output: `docker-compose.yml`

3. **Generate supporting files**
   - `backend/requirements.txt` (from TECH_STACK.md)
   - `frontend/package.json` (React + Vite + Tailwind)
   - `scripts/init_mongodb.js` (from TECH_STACK.md)
   - `scripts/init_cassandra.cql` OR `scripts/init_timescaledb.sql`
   - `.env.example`

4. **Start Docker services**
   ```bash
   docker-compose up -d
   docker-compose ps  # Wait for "Up"
   
   # Initialize databases
   docker-compose exec mongodb mongosh --eval "rs.initiate()"
   docker-compose exec cassandra cqlsh -f init.cql
   
   # Create Kafka topics
   docker-compose exec kafka kafka-topics \
     --create --topic vitals.raw --partitions 6 --replication-factor 1 \
     --bootstrap-server kafka:9092
   docker-compose exec kafka kafka-topics \
     --create --topic cases.events --partitions 1 --replication-factor 1 \
     --bootstrap-server kafka:9092
   docker-compose exec kafka kafka-topics \
     --create --topic alerts.raised --partitions 1 --replication-factor 1 \
     --bootstrap-server kafka:9092
   docker-compose exec kafka kafka-topics \
     --create --topic alerts.acknowledged --partitions 1 --replication-factor 1 \
     --bootstrap-server kafka:9092
   
   echo "✓ All services up and initialized"
   ```

5. **Verification**
   ```bash
   echo "Verifying services..."
   curl http://localhost:8081/  # Flink
   curl http://localhost:27017/  # MongoDB
   # (All checks pass or fail → report to user)
   ```

6. **Checkpoint**
   ```
   ════════════════════════════════════════════════════════════════════
   ✓ PHASE 1 COMPLETE
   ════════════════════════════════════════════════════════════════════
   
   All services are UP:
     • Kafka broker: localhost:9092
     • MongoDB: localhost:27017
     • [CASSANDRA/TIMESCALEDB]: Up
     • Flink JobManager: http://localhost:8081
     • FastAPI: Ready at localhost:5000
     • Frontend: Ready at localhost:5173
   
   Ready for Phase 2 (member implementations).
   
   Continue to Phase 2?
   [YES] → Start member tasks
   [NO]  → Pause
   
   Your answer: _______________
   ```

---

### PHASE 2: Member Implementations (Parallel, ~5 hours)

**Entry point:** After Phase 1 checkpoint = YES

**Ref:** PROMPT_BOOK.md → PHASE2_PUSHKAR, PHASE2_MEMBER2, PHASE2_MEMBER3, PHASE2_MEMBER4

**Generate 4 task branches (run in parallel):**

#### BRANCH 2A: Pushkar (MongoDB + API)

**Generate files (from TECH_STACK.md → Backend API section):**
- `backend/app/db.py` (MongoDB client initialization)
- `backend/app/models.py` (Pydantic schemas for cases, beds, orders, alerts)
- `backend/app/main.py` (FastAPI app, routes, WebSocket setup)
- `backend/app/api/cases.py` (POST /api/cases, GET /api/cases/active)
- `backend/app/api/beds.py` (POST /api/beds/reserve [ACID transaction], GET /api/beds/available)
- `backend/app/api/orders.py` (POST /api/orders with allergy check)
- `backend/app/api/alerts.py` (POST /api/alerts/{id}/acknowledge, GET unacknowledged)
- `backend/app/api/patients.py` (GET /api/patients/{id})
- `backend/app/websocket_manager.py` (MongoDB change stream listener → WebSocket)

**Instructions for Pushkar:**
```
✓ Review generated schemas (TEAM_CONTRACTS.md reference)
✓ Start FastAPI: python -m uvicorn app.main:app --reload
✓ Test endpoints:
  - POST /api/cases (create case)
  - POST /api/beds/reserve (reserve bed)
  - POST /api/beds/reserve (same bed, 2nd time) → should fail
  - POST /api/orders (medication patient is allergic to) → should fail
✓ Report: "Double-booking prevented ✓, Allergy blocking works ✓"
```

---

#### BRANCH 2B: Member 2 (Kafka + Consumer)

**Generate files:**
- `simulator/monitor_sim.py` (Produce vitals to Kafka from Synthea patients or VitalDB)
- `backend/consumer_cassandra.py` (Kafka → Cassandra consumer, batched writes)
- `backend/app/api/metrics.py` (GET /api/metrics/kafka-lag)
- `scripts/synthetic_data_gen.py` (Load Synthea patients, create sample data)

**Instructions for Member 2:**
```
✓ Start simulator: python simulator/monitor_sim.py --duration 5 --speed 10x
✓ Check Kafka: kafkacat -b localhost:9092 -t vitals.raw | head -20
✓ Start consumer: python backend/consumer_cassandra.py
✓ Verify data in DB:
  - Cassandra: SELECT COUNT(*) FROM vitalstream.vitals_by_patient_day;
  - TimescaleDB: SELECT COUNT(*) FROM vitals;
✓ Test query latency: "Last 10 min of Patient X" in <100ms
✓ Report: "X readings/sec, latency Yms"
```

---

#### BRANCH 2C: Member 3 (Flink)

**Generate files:**
- `flink/jobs/alert_detection.py` (PyFlink job: 30-sec window, thresholds, deduplication)
- `flink/jobs/escalation_timer.py` (PyFlink job: track unack'd, escalate at 10 min)
- `scripts/scenario_runner.py` (Trigger low BP alert, wait for escalation)

**Instructions for Member 3:**
```
✓ Submit jobs to Flink:
  flink run -py flink/jobs/alert_detection.py
  flink run -py flink/jobs/escalation_timer.py
✓ Check Flink UI: http://localhost:8081 (should show 2 running jobs)
✓ With simulator running, trigger low BP scenario
✓ Verify alert in MongoDB within 3 seconds
✓ Test escalation: leave alert unack'd for 10 min, check escalations collection
✓ Report: "Alert latency Xms, escalation works ✓"
```

---

#### BRANCH 2D: Member 4 (Cassandra/TimescaleDB)

**Generate files:**
- `scripts/load_test.py` (Simulate 6 ORs, measure write latency and throughput)
- `backend/app/api/metrics.py` (expose DB health: writes/sec, latency percentiles)

**Instructions for Member 4:**
```
✓ Run load test: python scripts/load_test.py --duration 10 --ors 6
✓ Observe output: writes/sec, latency (p50/p95/p99)
✓ Expected: 6 writes/sec, p95 <10ms
✓ Test query patterns:
  - Single-partition (patient X, day Y): <100ms
  - Multi-partition (patient X, 7 days): <500ms
✓ Check metrics endpoint: curl http://localhost:5000/api/metrics/cassandra
✓ Report: "X writes/sec, p95 latency Yms"
```

---

#### BRANCH 2E: All Members (Frontend)

**Generate files (skeleton components from TECH_STACK.md):**
- `frontend/src/components/ORWall.jsx` (6-bed grid, live vitals)
- `frontend/src/components/PatientDetail.jsx` (allergies, orders, timeline)
- `frontend/src/components/BedBoard.jsx` (recovery beds, reserve button)
- `frontend/src/components/PipelineHealth.jsx` (Flink, Kafka, Cassandra metrics)
- `frontend/src/components/AlertQueue.jsx` (unack'd alerts, ACK button)
- `frontend/src/components/VitalWaveform.jsx` (uPlot chart, 30-min waveform)
- `frontend/src/hooks/useWebSocket.js` (WebSocket connection, auto-reconnect)
- `frontend/src/context/CasesContext.jsx` (global state)
- `frontend/src/App.jsx` (grid layout, 3 columns)
- `frontend/tailwind.config.js` (pastel color palette from TECH_STACK.md)
- `frontend/src/index.css` (styling)

**Instructions for all members:**
```
✓ Split work (coordinate via Slack):
  - Pushkar: ORWall + PatientDetail
  - Member 2: BedBoard + PipelineHealth
  - Member 3: AlertQueue
  - Member 4: VitalWaveform
  - All: Shared (useWebSocket, CasesContext, App.jsx)
✓ Start dev server: npm run dev
✓ Verify WebSocket connects (browser console: "Connected")
✓ With simulator + Flink running, watch data flow to screen
✓ Test: All 6 screens show live updates
✓ Report: "Frontend responsive, WebSocket working ✓"
```

---

**Phase 2 checkpoint:**
```
════════════════════════════════════════════════════════════════════
✓ PHASE 2 COMPLETE: All Member Tasks Done
════════════════════════════════════════════════════════════════════

Checklist:
  ✓ Pushkar: MongoDB & API (transactions, allergy check)
  ✓ Member 2: Kafka → Cassandra/TimescaleDB pipeline
  ✓ Member 3: Flink alert jobs (detection, escalation)
  ✓ Member 4: Time-series DB (load test passed)
  ✓ All: Frontend (6 screens, WebSocket, state management)

Frontend: http://localhost:5173
Backend: http://localhost:5000

Ready for Phase 3?
[YES] → Run E2E tests
[NO]  → Pause

Your answer: _______________
```

---

### PHASE 3: End-to-End Testing (Auto-run, ~1 hour)

**Entry point:** After Phase 2 checkpoint = YES

**Ref:** PROMPT_BOOK.md → PHASE 3

```
════════════════════════════════════════════════════════════════════
🧪 PHASE 3: Automated End-to-End Testing
════════════════════════════════════════════════════════════════════

Running comprehensive tests...
```

**Automated tests:**

1. **Health checks** (verify all services responding)
2. **Connectivity tests** (FastAPI ↔ MongoDB, Flink ↔ Kafka, etc.)
3. **Data flow test** (Simulator → Kafka → DB, verify 300 readings in 30 sec)
4. **Alert detection test** (trigger low BP, verify alert in <3 sec)
5. **Transaction safety test** (book bed twice, one succeeds, one fails)
6. **WebSocket test** (verify frontend receives live updates)
7. **Query latency test** (verify <100ms for single-partition, <500ms multi-partition)
8. **Escalation test** (unack'd alert auto-escalates after 10 min)

**Output:**
```
[PASS] Health checks
[PASS] Connectivity
[PASS] Data flow (300 readings in 30 sec)
[PASS] Alert detection (2.1 sec latency)
[PASS] Transaction safety (double-booking rejected)
[PASS] WebSocket (<500ms updates)
[PASS] Query latency (92ms single, 410ms multi)
[PASS] Escalation (10 min 1 sec)

════════════════════════════════════════════════════════════════════
✓ PHASE 3 COMPLETE: All 8 Tests Passed
════════════════════════════════════════════════════════════════════

Continue to Phase 4?
[YES] → Prepare demo materials
[NO]  → Skip to Phase 5

Your answer: _______________
```

---

### PHASE 4: Demo Preparation (Auto-run, ~20 min)

**Entry point:** After Phase 3 checkpoint = YES

**Generates:**
- `scripts/DEMO_SCRIPT.md` (5-minute demo walkthrough)
- `scripts/TALKING_POINTS.md` (30-sec talking points per member)
- `scripts/DEMO_BACKUP.md` (fallback scenarios if live demo fails)

**Output:**
```
════════════════════════════════════════════════════════════════════
🎬 PHASE 4: Demo & Viva Preparation Complete
════════════════════════════════════════════════════════════════════

Generated:
  ✓ scripts/DEMO_SCRIPT.md (5-min walkthrough)
  ✓ scripts/TALKING_POINTS.md (member talking points)
  ✓ scripts/DEMO_BACKUP.md (fallback scenarios)

Next: Read and practice the demo script.

Continue to Phase 5?
[YES] → Final checks
[NO]  → You're done

Your answer: _______________
```

---

### PHASE 5: Final Verification (Auto-run, ~5 min)

**Entry point:** After Phase 4 checkpoint = YES

**Checks:**
- docker-compose ps (all services Up)
- Simulator running
- Frontend loads
- WebSocket connected
- FastAPI responsive
- Flink jobs running
- MongoDB data populated
- Demo script readable
- Talking points readable

**Output:**
```
════════════════════════════════════════════════════════════════════
✅ PHASE 5: All Systems Go
════════════════════════════════════════════════════════════════════

✓ All services running
✓ Simulator streaming (6 readings/sec)
✓ Frontend responsive
✓ WebSocket connected
✓ Database populated
✓ Demo script ready
✓ Talking points ready

🎯 YOU'RE READY FOR VIVA

Viva checklist:
  □ All members present
  □ Demo machine set up
  □ Terminal available
  □ Browser with localhost:5173 tabbed
  □ Flink UI (http://localhost:8081) ready
  □ Demo script printed
  □ Talking points printed

Good luck! 🚀
```

---

## RESUMPTION LOGIC

If user pauses at any checkpoint:

```
PAUSE_STATE = PHASE_N_CHECKPOINT

When user says "resume":
  → Jump to PHASE_N_EXECUTION
  → Continue from where you left off
  → No re-running of completed phases
```

---

## ERROR HANDLING

If any step fails:

```
✗ ERROR in [Step]
  Issue: [Description]
  Likely cause: [Diagnosis]
  Automated fix: [What to try]

Retry?
  [YES] → Run step again
  [NO]  → Skip (may break downstream)
  [ABORT] → Stop, user will debug

Your answer: _______________
```

---

## SUCCESS CONDITION

All 5 phases complete = **Ready for viva**

- Working VitalStream project ✓
- 5-minute demo script ✓
- Talking points per member ✓
- One bed-conflict test proven ✓
- One alert scenario proven ✓
- One escalation demo proven ✓

---

## KEY DOCUMENTS TO REFERENCE

- **README_START_HERE.md** → User orientation
- **ANTIGRAVITY_SETUP.md** → Decision flow, troubleshooting
- **PROMPT_BOOK.md** → Detailed phase breakdown
- **TEAM_CONTRACTS.md** → Member tasks, schemas
- **TECH_STACK.md** → Code snippets, versions, color palette
- **TOOL_ROLES_SIMPLE.md** → Explanations for examiners

---

## READY TO LAUNCH

You are now prepared to execute VitalStream.

**Next command:** Present this prompt to the user, ask them to confirm they're ready to start, and await the 4 decisions.

Good luck! 🚀

