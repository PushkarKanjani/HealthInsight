# VitalStream × Antigravity — Auto-Execution Setup

**Status:** Ready to launch  
**Deadline:** Tomorrow (24 hours)  
**Mode:** User confirms decisions, AG agents auto-implement phases  
**Interaction:** Yes/No prompts only  

---

## HOW IT WORKS

1. **You provide 4 quick decisions** (see "DECISION PROMPTS" below)
2. **AG agents automatically execute phases** (see "PHASE EXECUTION" below)
3. **You confirm milestones** at end of each phase (Yes/No)
4. **By tomorrow:** Demo-ready project

---

## DECISION PROMPTS (Run These First)

Copy this section into Antigravity and answer each:

```
VITALSTREAM SETUP — USER DECISIONS

Confirm each decision (the agent will execute based on your answers):

┌─ DECISION 1: Cleanup Old Project Files ─────────────────────────┐
│                                                                   │
│ Clean up old HealthInsight (Spark/Iceberg/Trino/Superset)?       │
│ This removes: /spark /iceberg /trino /superset /mongodb /scripts │
│              and old config files (keep .git history)            │
│                                                                   │
│ [YES] → Delete old files, start fresh                            │
│ [NO]  → Keep old files (VitalStream in separate structure)       │
│                                                                   │
│ Your answer: ___________________                                  │
└─────────────────────────────────────────────────────────────────┘

┌─ DECISION 2: Data Source for Vitals ────────────────────────────┐
│                                                                   │
│ How should we generate vital signs for the 6 operating rooms?    │
│                                                                   │
│ [SYNTHETIC] → AI-generated vitals based on rules                 │
│              Speed: Ready in 2 min                                │
│              Data: Stable/deteriorating scenarios                 │
│              Good for: Fast setup, controlled demo                │
│                                                                   │
│ [VITALDB]   → Real surgical recordings from VitalDB (6,388 cases)│
│              Speed: Need to download (~5GB, ~5 min on 10Mbps)     │
│              Data: Real intraoperative monitoring (500 Hz)        │
│              Good for: Credible, realistic, impressive           │
│                                                                   │
│ Your answer: ___________________                                  │
│                                                                   │
│ Recommended for tomorrow's deadline: SYNTHETIC (faster)          │
└─────────────────────────────────────────────────────────────────┘

┌─ DECISION 3: Time-Series Database ──────────────────────────────┐
│                                                                   │
│ Which database for storing 518k daily vital readings?            │
│                                                                   │
│ Your machine RAM available: ____________ GB                       │
│                                                                   │
│ [CASSANDRA]   → Distributed, scale-out friendly                  │
│                RAM needed: 2–3 GB (for demo)                     │
│                Speed: Moderate (startup ~30 sec)                 │
│                Best for: Production-like setup, scaling story     │
│                                                                   │
│ [TIMESCALEDB] → Lighter, PostgreSQL extension                    │
│                RAM needed: <1 GB                                  │
│                Speed: Fast (startup ~10 sec)                     │
│                Best for: Limited RAM, simpler operations         │
│                                                                   │
│ Your answer: ___________________                                  │
│                                                                   │
│ Auto-decision: IF RAM < 6GB → TIMESCALEDB, ELSE → CASSANDRA     │
└─────────────────────────────────────────────────────────────────┘

┌─ DECISION 4: Start Immediately? ───────────────────────────────┐
│                                                                   │
│ Begin Phase 1 setup now? (Folder structure + Docker)             │
│ Time required: ~45 minutes                                       │
│                                                                   │
│ [YES] → Launch Phase 1 immediately                               │
│ [NO]  → Pause, I'll say when to start                            │
│                                                                   │
│ Your answer: ___________________                                  │
└─────────────────────────────────────────────────────────────────┘

════════════════════════════════════════════════════════════════════
Ready to start automation. Executing based on your decisions...
════════════════════════════════════════════════════════════════════
```

---

## PHASE EXECUTION (Automated by AG)

### PHASE 1: Folder Setup + Docker (Auto-run, ~45 min)

**What AG does (without interruption):**

1. **CLEANUP** (if Decision 1 = YES)
   ```
   ✓ Remove old directories
   ✓ Backup old configs to ./backup_healthinsight/
   ✓ Git commit cleanup
   ```

2. **CREATE FOLDER STRUCTURE**
   ```
   ✓ backend/
   ✓ frontend/
   ✓ simulator/
   ✓ flink/
   ✓ scripts/
   ```

3. **GENERATE FILES**
   - `docker-compose.yml` (with your DB choice: Cassandra or TimescaleDB)
   - `backend/requirements.txt`
   - `frontend/package.json`
   - `scripts/init_mongodb.js`
   - `scripts/init_cassandra.cql` OR `scripts/init_timescaledb.sql`
   - `.env` (with placeholders)

4. **START DOCKER**
   ```
   docker-compose up -d
   (wait for health checks...)
   ✓ Zookeeper: Up
   ✓ Kafka: Up
   ✓ MongoDB: Up (replica set initialized)
   ✓ [Cassandra OR TimescaleDB]: Up
   ✓ Flink: Up (JobManager at http://localhost:8081)
   ```

5. **INIT DATABASES**
   ```
   ✓ MongoDB: rs.initiate() complete
   ✓ Kafka: 4 topics created (vitals.raw, cases.events, alerts.raised, alerts.acknowledged)
   ✓ [Cassandra OR TimescaleDB]: schema initialized
   ```

**Output to you:**
```
═══════════════════════════════════════════════════════════════════
✓ PHASE 1 COMPLETE: Docker + Folder Structure
═══════════════════════════════════════════════════════════════════

All services are UP:
  • Kafka broker: localhost:9092
  • MongoDB: localhost:27017
  • [DB choice]: localhost:9042 (Cassandra) or localhost:5432 (TimescaleDB)
  • Flink JobManager: http://localhost:8081
  • FastAPI (backend): Ready to start at :5000
  • Frontend (dev): Ready to start at :5173

Ready for Phase 2 (Member implementations).

Next step: Press YES to continue with Phase 2, or NO to pause.
───────────────────────────────────────────────────────────────────

Continue to Phase 2?
[YES] → Start member implementation tasks (parallel)
[NO]  → Pause here, I'll resume later

Your answer: ___________________
```

---

### PHASE 2: Member Implementations (Parallel, ~5 hours)

**AG creates task branches for each member. They work in parallel.**

#### PUSHKAR: MongoDB + API Endpoints

```
📋 Task: MongoDB schema & FastAPI endpoints
─────────────────────────────────────────

Generated files:
  ✓ backend/app/db.py              (MongoDB client, collections)
  ✓ backend/app/models.py          (Pydantic schemas)
  ✓ backend/app/api/cases.py       (CRUD for cases)
  ✓ backend/app/api/beds.py        (ACID bed reservation)
  ✓ backend/app/api/orders.py      (Medication with allergy check)
  ✓ backend/app/api/alerts.py      (Alert lifecycle)
  ✓ backend/app/websocket_manager.py (Change stream listener)

What to do:
  1. Review generated code (in backend/app/api/)
  2. Test bed reservation:
     - Start FastAPI: python -m uvicorn app.main:app --reload
     - Call: POST /api/cases (create case in OR-2)
     - Call: POST /api/beds/reserve (reserve REC-04)
     - Try again: POST /api/beds/reserve (same bed) → should fail
  3. Test allergy check:
     - Create patient with allergy "penicillin"
     - Try: POST /api/orders (medication=Penicillin) → should fail
  4. Report: "Transactions working, double-booking prevented"

Time estimate: 1.5 hours
Status: [STARTED] → [IN_PROGRESS] → [DONE]
─────────────────────────────────────────
```

#### MEMBER 2: Kafka + Cassandra/TimescaleDB Consumer

```
📋 Task: Monitor simulator & vitals pipeline
──────────────────────────────────────────

Generated files:
  ✓ simulator/monitor_sim.py        (6 ORs, synthetic vitals → Kafka)
  ✓ backend/consumer_cassandra.py   (Kafka → DB, batched writes)
  ✓ backend/app/api/metrics.py      (Kafka lag endpoint)

What to do:
  1. Start simulator:
     python simulator/monitor_sim.py --duration 5 --speed 10x
     (5 minutes of data at 10x speed = 30 seconds wall time)
  2. Check Kafka:
     - kafkacat -b localhost:9092 -t vitals.raw -C -c 10
     - Should see readings flowing (6 per second)
  3. Check database:
     - Cassandra: SELECT COUNT(*) FROM vitalstream.vitals_by_patient_day;
     - TimescaleDB: SELECT COUNT(*) FROM vitals;
     - Expected: ~1800 readings (6 readings/sec × 300 sec)
  4. Test query:
     - "Last 10 min of Patient X" should return in <100ms
  5. Report: "X readings/sec, latency Yms"

Time estimate: 1.5 hours
Status: [STARTED] → [IN_PROGRESS] → [DONE]
──────────────────────────────────────────
```

#### MEMBER 3: Flink Alert Jobs

```
📋 Task: Alert detection & escalation
─────────────────────────────────────

Generated files:
  ✓ flink/jobs/alert_detection.py   (Windowed aggregation, thresholds)
  ✓ flink/jobs/escalation_timer.py  (Unack'd → escalate)

What to do:
  1. Start Flink jobs:
     flink run -py flink/jobs/alert_detection.py
     flink run -py flink/jobs/escalation_timer.py
  2. Monitor:
     - Open http://localhost:8081 (Flink UI)
     - Should show 2 running jobs
  3. With simulator running (from Member 2):
     - Trigger low BP alert (simulator can do this with --scenario flag)
     - Alert should appear in MongoDB within 3 seconds
     - Check: db.alerts.find({alert_type: "BP_LOW"}).limit(1)
  4. Test escalation:
     - Leave alert unacknowledged for 10 minutes
     - Check: db.escalations.find().limit(1)
     - Should show escalation entry
  5. Report: "Alert latency Xms, escalation works"

Time estimate: 1.5 hours
Status: [STARTED] → [IN_PROGRESS] → [DONE]
─────────────────────────────────────────
```

#### MEMBER 4: TimescaleDB/Cassandra Load Test

```
📋 Task: Database tuning & performance
──────────────────────────────────────

Generated files:
  ✓ scripts/load_test.py             (Simulate 6 ORs, measure latency)
  ✓ backend/app/api/metrics.py       (Expose DB health metrics)

What to do:
  1. Run load test:
     python scripts/load_test.py --duration 10 --ors 6
     (Simulate 6 ORs for 10 minutes)
  2. Observe:
     - Terminal output: writes/sec, latency (p50/p95/p99)
     - Expected: 6 writes/sec, p95 <10ms
  3. Check metrics endpoint:
     - curl http://localhost:5000/api/metrics/cassandra
     - Should show latency percentiles
  4. Test query patterns:
     - Single-partition: <100ms
     - Multi-partition (7 days): <500ms
  5. Report: "X writes/sec, p95 latency Yms"

Time estimate: 1 hour
Status: [STARTED] → [IN_PROGRESS] → [DONE]
──────────────────────────────────────────
```

#### ALL: Frontend Components + WebSocket

```
📋 Task: React UI, WebSocket, Layouts
─────────────────────────────────────

Generated files:
  ✓ frontend/src/components/ORWall.jsx         (Pushkar)
  ✓ frontend/src/components/PatientDetail.jsx  (Pushkar)
  ✓ frontend/src/components/BedBoard.jsx       (Member 2)
  ✓ frontend/src/components/PipelineHealth.jsx (Member 2)
  ✓ frontend/src/components/AlertQueue.jsx     (Member 3)
  ✓ frontend/src/components/VitalWaveform.jsx  (Member 4)
  ✓ frontend/src/hooks/useWebSocket.js         (Shared)
  ✓ frontend/src/context/CasesContext.jsx      (Shared)
  ✓ frontend/src/App.jsx                       (Shared grid layout)

What to do (in parallel, coordinate via Slack):
  1. Each member implements their component (skeleton provided)
  2. Connect to useWebSocket hook (shared)
  3. Use CasesContext for global state
  4. Test locally:
     npm run dev → http://localhost:5173
  5. Verify:
     - WebSocket connects (browser console: should see "Connected")
     - Simulator + Flink running, data flows to screen
     - ORWall shows live vitals, alerts appear in real-time

Time estimate: 2 hours (parallel)
Status: [STARTED] → [IN_PROGRESS] → [DONE]
──────────────────────────────────────────
```

**After all Phase 2 tasks:**
```
═══════════════════════════════════════════════════════════════════
✓ PHASE 2 COMPLETE: All Member Tasks
═══════════════════════════════════════════════════════════════════

Checklist:
  ✓ Pushkar: MongoDB & API endpoints (bed transaction + allergy check)
  ✓ Member 2: Kafka producer & consumer (vitals pipeline)
  ✓ Member 3: Flink alert jobs (detection + escalation)
  ✓ Member 4: Time-series DB (load test passed)
  ✓ All: Frontend components (ORWall, alerts, beds, waveforms)

Frontend online at: http://localhost:5173
Backend API at: http://localhost:5000

Ready for Phase 3 (E2E testing).

Continue to Phase 3?
[YES] → Run automated tests
[NO]  → Pause here

Your answer: ___________________
```

---

### PHASE 3: End-to-End Testing (Auto-run, ~1 hour)

```
═══════════════════════════════════════════════════════════════════
🧪 PHASE 3: Automated End-to-End Testing
═══════════════════════════════════════════════════════════════════

AG will run:

✓ Health checks (all services responding)
✓ Service connectivity (FastAPI ↔ MongoDB, Flink ↔ Kafka, etc.)
✓ Simulator → Kafka → DB pipeline (verify data flows)
✓ Flink alert detection (trigger low BP, verify alert in <3 sec)
✓ MongoDB transaction (book bed twice, one succeeds)
✓ Frontend WebSocket (verify live updates)
✓ Database query performance (verify latencies)
✓ Escalation timer (wait 10 min, verify escalation)

Monitoring:
  - All test outputs logged to ./test_results.json
  - Failed tests halted (AG prompts you)
  - Passed tests proceed to next

Expected duration: 45 min

═══════════════════════════════════════════════════════════════════

Running tests...

[RUNNING] Health checks...
✓ Zookeeper: Up
✓ Kafka: Up
✓ MongoDB: Up
✓ [DB]: Up
✓ Flink: Up
✓ FastAPI: Up
✓ Frontend: Up

[RUNNING] Simulator → Kafka → DB pipeline...
✓ Simulator started (6 ORs)
✓ Vitals flowing to Kafka (6 msg/sec)
✓ Consumer batching to DB
✓ After 30 sec: 180 readings in DB
✓ Query latency: 45ms (within budget)

[RUNNING] Flink alert detection...
✓ Alert job running
✓ Trigger low BP scenario
✓ Alert raised: 2.1 sec (within budget)
✓ Alert visible in MongoDB

[RUNNING] MongoDB transaction safety...
✓ Simulator running
✓ Create case in OR-1
✓ Book bed REC-04 (succeeds)
✓ Book same bed REC-04 again in parallel
✓ Second request fails (conflict) ✓

[RUNNING] Frontend WebSocket...
✓ Browser connected
✓ Simulator running
✓ ORWall updates in real-time (<500ms latency)
✓ Alerts appear in AlertQueue

[RUNNING] Escalation timer...
✓ Alert raised
✓ Left unacknowledged
✓ After 10 min 1 sec: escalation triggered ✓

═══════════════════════════════════════════════════════════════════
✓ PHASE 3 COMPLETE: All E2E tests PASSED
═══════════════════════════════════════════════════════════════════

Summary:
  ✓ 8/8 test categories passed
  ✓ No failures
  ✓ All latencies within budget
  ✓ Ready for demo

Next: Phase 4 (Demo preparation & talking points).

Continue to Phase 4?
[YES] → Prepare demo materials
[NO]  → Skip to Phase 5 (quick viva)

Your answer: ___________________
```

---

### PHASE 4: Demo Preparation (Auto-run, ~20 min)

```
═══════════════════════════════════════════════════════════════════
🎬 PHASE 4: Demo & Viva Preparation
═══════════════════════════════════════════════════════════════════

AG will generate:

✓ DEMO_SCRIPT.md (5-minute demo walkthrough)
✓ Member talking points (why each tool matters)
✓ Troubleshooting guide (if demo goes wrong)
✓ Backup scenarios (if live demo fails, fallback)

Generated:
  ✓ scripts/DEMO_SCRIPT.md
  ✓ scripts/TALKING_POINTS.md
  ✓ scripts/DEMO_BACKUP.md

═══════════════════════════════════════════════════════════════════
✓ PHASE 4 COMPLETE: Demo Ready
═══════════════════════════════════════════════════════════════════

Files ready:
  1. Read: scripts/DEMO_SCRIPT.md (5 min walkthrough)
  2. Practice: Each member reads their talking points
  3. Backup: scripts/DEMO_BACKUP.md (if live demo fails)

You're ready to present.

Continue to Phase 5 (final checks)?
[YES] → Run final verification
[NO]  → You're done, good luck!

Your answer: ___________________
```

---

### PHASE 5: Final Verification (Auto-run, ~5 min)

```
═══════════════════════════════════════════════════════════════════
✅ PHASE 5: Final Checks Before Viva
═══════════════════════════════════════════════════════════════════

Checklist:
  ✓ docker-compose ps (all services Up)
  ✓ Simulator running (6 ORs streaming)
  ✓ Frontend loads (http://localhost:5173)
  ✓ WebSocket connected (browser console: "Connected")
  ✓ Backend API responsive (curl http://localhost:5000/health)
  ✓ Flink jobs running (http://localhost:8081)
  ✓ MongoDB collections populated
  ✓ Demo script memorized
  ✓ Talking points ready

All clear! ✓

═══════════════════════════════════════════════════════════════════
🎯 YOU'RE READY
═══════════════════════════════════════════════════════════════════

VitalStream is demo-ready.

Presentation checklist:
  □ All members present
  □ Demo machine set up
  □ Laptop plugged in (don't rely on battery)
  □ Terminal available for logs
  □ Browser with localhost:5173 tabbed
  □ Flink UI ready (http://localhost:8081)
  □ Script printout (scripts/DEMO_SCRIPT.md)
  □ Talking points printout (scripts/TALKING_POINTS.md)

Good luck! 🚀
```

---

## IF SOMETHING BREAKS

During execution, if a phase fails:

```
✗ ERROR in [Phase/Step]
─────────────────────────────

Issue: [Description]
  Example: "Flink job failed to submit"

Likely cause: [Diagnosis]
  Example: "PyFlink not installed in container"

Fix:
  1. [Automated fix attempt]
  2. If still failing: [Manual step]

Retry?
  [YES] → Run step again (fix applied)
  [NO]  → Skip (may break downstream)
  [ABORT] → Stop automation, I'll debug manually

Your choice: ___________________
```

---

## SUMMARY: How to Use This

**Before tomorrow:**

1. **Copy decision prompts** (above) into Antigravity
2. **Answer 4 questions** (cleanup, data, DB, start now)
3. **Let AG run automatically** (no more decisions needed)
4. **Confirm each phase** (Yes/No only)
5. **By morning:** Demo-ready, 5-minute demo script ready, talking points ready

**During viva:**
- Open `scripts/DEMO_SCRIPT.md` on phone/laptop (quick reference)
- Follow the 5-minute flow
- Each member uses `scripts/TALKING_POINTS.md` (30 sec per person)

---

## FILES READY FOR USE

- `PROMPT_BOOK.md` — Detailed phase breakdown (what AG does at each step)
- `TECH_STACK.md` — Full technical details (reference, not for demo)
- `TEAM_CONTRACTS.md` — Task breakdown (reference for understanding roles)
- `TOOL_ROLES_SIMPLE.md` — Simple explanations (reference for studying)

**Share with team:**
- `PROMPT_BOOK.md` (everyone understands the plan)
- `TECH_STACK.md` (reference for technical details)
- `TEAM_CONTRACTS.md` (each member knows their task)

