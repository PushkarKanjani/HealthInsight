# VitalStream PROMPT_BOOK — Antigravity Auto-Execution Guide

**Deadline:** Tomorrow (24 hours)  
**Mode:** Auto-execution with user decision prompts (yes/no only)  
**Status:** Setup phase → Implementation phases → Testing → Demo ready

---

## DECISION TREE: Initial Setup (USER CONFIRMS)

```
START
  ├─ Question 1: Clean up old HealthInsight files and start fresh?
  │  └─ YES → CLEANUP_PHASE
  │  └─ NO  → SKIP to FOLDER_SETUP
  │
  ├─ Question 2: Use synthetic vitals or download VitalDB?
  │  └─ SYNTHETIC → Fast, no downloads, ready immediately
  │  └─ VITALDB → Real surgical data, slower, more credible (need internet + 5GB)
  │
  ├─ Question 3: Cassandra or TimescaleDB? (RAM: <6GB → TimescaleDB, ≥6GB → Cassandra)
  │  └─ CASSANDRA → Distributed, scale-out friendly (default)
  │  └─ TIMESCALEDB → Lighter, better for <6GB RAM
  │
  └─ Question 4: Start Phase 1 (Folder + Docker) immediately?
     └─ YES → EXEC_PHASE_1
     └─ NO  → PAUSE (you'll run later)
```

---

## CLEANUP PHASE (if Question 1 = YES)

**What it does:** Removes old project files, keeps only `.git` history.

**Automated steps:**
```bash
# CLEANUP_001: Remove old directories
rm -rf ./data ./docs ./iceberg ./mongodb ./portal ./screenshots ./scripts ./spark ./superset ./trino
echo "✓ Removed old HealthInsight components"

# CLEANUP_002: Remove old config files (keep .env.example for reference)
rm -f .env PROMPT_BOOK.md README.md docker-compose.yml requirements.txt
echo "✓ Removed old configs (except .env.example)"

# CLEANUP_003: Git cleanup (optional, keeps history)
git add -A
git commit -m "cleanup: remove HealthInsight v1, prepare for VitalStream"
echo "✓ Git checkpoint created"

# CLEANUP_004: Verify clean slate
ls -la
# Expected: only .git, .gitignore, .env.example, and new folders coming
```

**Output confirmation:**
```
✓ Cleanup complete
  Removed: /iceberg /mongodb /spark /superset /trino /portal /scripts /data /docs
  Kept: .git (history), .gitignore, .env.example
  Ready for: VitalStream folder structure
```

---

## PHASE 1: Folder Structure + Docker Compose (1 hour)

**Triggers:** After cleanup (or skip cleanup) + Question 4 = YES

**What it does:** Creates folder structure, generates docker-compose.yml, pulls Docker images.

### PHASE1_001: Create Folder Structure

```
VitalStream/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              (FastAPI routes)
│   │   ├── models.py            (Pydantic schemas)
│   │   ├── db.py                (MongoDB, Cassandra clients)
│   │   ├── websocket_manager.py (WebSocket handler)
│   │   └── api/
│   │       ├── cases.py         (POST /api/cases, GET /api/cases/active)
│   │       ├── beds.py          (POST /api/beds/reserve, GET /api/beds/available)
│   │       ├── orders.py        (POST /api/orders with allergy check)
│   │       ├── alerts.py        (POST /api/alerts/{id}/acknowledge, GET unacked)
│   │       └── patients.py      (GET /api/patients/{id})
│   ├── requirements.txt          (fastapi, pymongo, cassandra-driver, kafka-python)
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ORWall.jsx
│   │   │   ├── AlertQueue.jsx
│   │   │   ├── BedBoard.jsx
│   │   │   ├── PatientDetail.jsx
│   │   │   ├── VitalWaveform.jsx
│   │   │   └── PipelineHealth.jsx
│   │   ├── hooks/
│   │   │   └── useWebSocket.js
│   │   ├── context/
│   │   │   └── CasesContext.jsx
│   │   ├── App.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── simulator/
│   ├── __init__.py
│   ├── monitor_sim.py           (6 ORs, Kafka producer)
│   └── requirements.txt
├── flink/
│   ├── jobs/
│   │   ├── alert_detection.py   (PyFlink job)
│   │   └── escalation_timer.py
│   └── config/
│       └── flink-conf.yaml
├── scripts/
│   ├── init_mongodb.js          (replica set init, collections)
│   ├── init_cassandra.cql       (keyspace, table)
│   ├── init_kafka_topics.sh     (create topics)
│   └── synthetic_data_gen.py    (Synthea loader + sample patients)
├── docker-compose.yml
├── .env.example
├── PROMPT_BOOK.md               (this file)
├── TECH_STACK.md                (from earlier)
├── TEAM_CONTRACTS.md
└── README.md                    (Quick start)
```

**Automated:**
```bash
# PHASE1_001: Create directories
mkdir -p backend/app/api backend frontend/src/{components,hooks,context} simulator flink/{jobs,config} scripts

# PHASE1_002: Copy/generate placeholder files (detailed below)
# (Agent will use templates)

# PHASE1_003: Initialize git structure
git add .
git commit -m "feat: VitalStream folder structure"
```

**Output:**
```
✓ PHASE1_001: Folder structure created
✓ PHASE1_002: Placeholder files generated
✓ Ready for Phase 1 continued
```

---

### PHASE1_002: Generate docker-compose.yml

**Agent copies from TECH_STACK.md, generates:**

```yaml
# docker-compose.yml (auto-generated, pinned versions)
version: "3.8"

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.6.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    volumes:
      - zk_data:/var/lib/zookeeper/data

  kafka:
    image: confluentinc/cp-kafka:7.6.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
    volumes:
      - kafka_data:/var/lib/kafka/data

  # (MongoDB, Cassandra, Flink, FastAPI, Frontend follow from TECH_STACK.md)
```

**Output:**
```
✓ PHASE1_002: docker-compose.yml generated
✓ PHASE1_003: Docker images pulled (this may take 5–10 min)
```

---

### PHASE1_003: Start Services

```bash
# PHASE1_004: Bring up services
docker-compose up -d

# PHASE1_005: Wait for health checks (Kafka, MongoDB, Cassandra online)
docker-compose ps
# Expected: all services "Up"

# PHASE1_006: Initialize databases
docker-compose exec mongodb mongosh --eval "rs.initiate()"
docker-compose exec cassandra cqlsh -f /docker-entrypoint-initdb.d/init.cql

# PHASE1_007: Create Kafka topics
docker-compose exec kafka kafka-topics --create --topic vitals.raw --partitions 6 --replication-factor 1 --bootstrap-server kafka:9092
docker-compose exec kafka kafka-topics --create --topic cases.events --partitions 1 --replication-factor 1 --bootstrap-server kafka:9092
docker-compose exec kafka kafka-topics --create --topic alerts.raised --partitions 1 --replication-factor 1 --bootstrap-server kafka:9092
docker-compose exec kafka kafka-topics --create --topic alerts.acknowledged --partitions 1 --replication-factor 1 --bootstrap-server kafka:9092
```

**Output:**
```
✓ PHASE1_004: All services running
  - Zookeeper: ready
  - Kafka: ready (4 topics created)
  - MongoDB: ready (replica set initialized)
  - Cassandra: ready (keyspace vitalstream, table vitals_by_patient_day)
  - Flink: ready (JobManager UI at http://localhost:8081)
  - FastAPI: ready (API at http://localhost:5000)
  - Frontend: ready (dev server at http://localhost:5173)

Next: PHASE 2 (Member implementations)
```

---

## PHASE 2: Member Implementation Tasks (4–6 hours)

**Parallel execution.** Each member works on their component.

### PHASE2_PUSHKAR: MongoDB Schema + API

**Entry point:** `backend/app/api/cases.py`, `backend/app/api/beds.py`, etc.

**Agent instruction:**
```
Generate:
1. MongoDB schemas (from TEAM_CONTRACTS.md)
2. FastAPI endpoints:
   - POST /api/cases (create case, check OR free)
   - GET /api/cases/active
   - POST /api/beds/reserve (ACID transaction)
   - GET /api/beds/available
   - POST /api/orders (allergy check)
   - GET /api/alerts/unacknowledged
   - POST /api/alerts/{id}/acknowledge

3. Change stream listener (push alerts via WebSocket)

Test: 
- Bed conflict test (book same bed twice in parallel → one fails)
- Allergy block test (order medication patient is allergic to → rejected)

Estimate: 2 hours
```

---

### PHASE2_MEMBER2: Kafka + Cassandra Consumer

**Entry point:** `simulator/monitor_sim.py`, `backend/consumer_cassandra.py`

**Agent instruction:**
```
Generate:
1. Monitor simulator (simulator/monitor_sim.py):
   - Load Synthea patients from CSV
   - For each of 6 ORs, generate synthetic vitals (or replay VitalDB if chosen)
   - Send to vitals.raw topic (1 reading/sec per OR, 10x speed for demo)
   - Send case events to cases.events topic

2. Cassandra consumer (backend/consumer_cassandra.py):
   - Read vitals.raw from Kafka
   - Batch every 10 seconds
   - Write to vitals_by_patient_day table

3. Lag monitoring endpoint:
   - GET /api/metrics/kafka-lag → report consumer offset lag

Test:
- Run simulator for 5 min, verify 300 readings in Cassandra
- Query: SELECT * FROM vitals_by_patient_day WHERE patient_id='...' AND bucket_date='2026-10-25'
  Expected: <100ms response

Estimate: 2 hours
```

---

### PHASE2_MEMBER3: Flink Alert Jobs

**Entry point:** `flink/jobs/alert_detection.py`, `flink/jobs/escalation_timer.py`

**Agent instruction:**
```
Generate:
1. Alert detection job (flink/jobs/alert_detection.py):
   - 30-second tumbling window per patient
   - Thresholds: SystBP < 90, O2 < 94, O2 falling >5 in 60 sec
   - Deduplicate: suppress same alert type for 5 min
   - Output: alerts.raised topic + MongoDB alerts collection

2. Escalation timer job (flink/jobs/escalation_timer.py):
   - Track alert lifetime
   - If unack'd > 10 min, escalate to escalations collection
   - Output: MongoDB escalations collection

3. Submit jobs to Flink cluster:
   - flink run -py alert_detection.py
   - flink run -py escalation_timer.py

Test:
- Simulator running, trigger low BP alert
- Verify alert appears in MongoDB alerts collection <3 sec
- Wait 10 min, verify escalation fires
- Check Flink metrics: http://localhost:8081

Estimate: 2.5 hours
```

---

### PHASE2_MEMBER4: Cassandra Schema + Load Test

**Entry point:** `flink/jobs/cassandra_init.cql`, load test script

**Agent instruction:**
```
Generate:
1. Cassandra initialization (scripts/init_cassandra.cql):
   - Keyspace vitalstream
   - Table vitals_by_patient_day (partitioned by patient_id, bucket_date)
   - Indexes for query patterns
   - TTL = 30 days

2. Load test script (scripts/cassandra_load_test.py):
   - Simulate 6 ORs, 1 reading/sec for 10 min
   - Measure: write latency (p50, p95, p99)
   - Report: "X writes/sec, <Yms latency"

3. Query validation:
   - Test single-partition query (patient X, day Y)
   - Test multi-partition query (patient X, last 7 days)

Test:
- Run load test
- Expected: 6 writes/sec, p95 <10ms
- Report metrics endpoint: GET /api/metrics/cassandra

Estimate: 1.5 hours
```

---

### PHASE2_ALL: Frontend Components + Shared API

**Entry point:** `frontend/src/App.jsx`, `frontend/src/components/`

**Agent instruction:**
```
Generate:
1. React components (Pushkar builds ORWall + PatientDetail):
   - ORWall.jsx: 6-bed grid, live vitals (HR/BP/O2), status color
   - PatientDetail.jsx: Click OR → patient allergies, orders, timeline

2. React components (Member 2 builds BedBoard + PipelineHealth):
   - BedBoard.jsx: Recovery beds (free/occupied), reserve button
   - PipelineHealth.jsx: Flink uptime, Kafka lag, Cassandra latency

3. React components (Member 3 builds AlertQueue):
   - AlertQueue.jsx: Unack'd alerts, severity color, ACK button

4. React components (Member 4 builds VitalWaveform):
   - VitalWaveform.jsx: uPlot chart, 30-min HR/BP/O2

5. Shared infrastructure:
   - hooks/useWebSocket.js: Connect to FastAPI WebSocket, auto-reconnect
   - context/CasesContext.jsx: Global state for cases, alerts, beds
   - App.jsx: Layout grid (3 columns: ORWall, AlertQueue, VitalWaveform)

6. Styling:
   - Tailwind CSS with pastel palette (from TECH_STACK.md)
   - No glass effect, minimal design

Test:
- npm run dev → http://localhost:5173
- Verify WebSocket connects
- Simulator running, watch vitals appear on ORWall live

Estimate: 2.5 hours (parallel)
```

---

## PHASE 3: End-to-End Testing (1.5 hours)

**Triggered after all Phase 2 tasks complete.**

**Agent checks:**

```bash
# PHASE3_001: Service health
curl http://localhost:5000/health           # FastAPI
curl http://localhost:8081                  # Flink UI
curl http://localhost:5173                  # Frontend

# PHASE3_002: Simulate scenario (script)
python scripts/scenario_runner.py --duration 5 --scenario "stable_then_low_bp"

# PHASE3_003: Check outputs
# 1. Monitor logs for errors
docker-compose logs --tail 50

# 2. Verify MongoDB documents
docker-compose exec mongodb mongosh -d vitalstream --eval "db.alerts.find({}).limit(5)"

# 3. Verify Cassandra data
docker-compose exec cassandra cqlsh -e "SELECT COUNT(*) FROM vitalstream.vitals_by_patient_day;"

# 4. Check Flink job status
# Visit http://localhost:8081 → JobManager → Running Jobs

# PHASE3_004: Run demo scenario
python scripts/demo_scenarios.py --mode "automated_full_demo"

# Expected output:
# ✓ Simulator running, 6 ORs streaming
# ✓ Vitals appear on ORWall in real-time
# ✓ Low BP alert triggered after 2 min
# ✓ Alert visible in AlertQueue
# ✓ Unacknowledged for 10 min → auto-escalation fires
# ✓ Patient detail shows 30-min waveform from Cassandra
```

**Output:**
```
✓ PHASE 3: E2E tests passed
  ✓ All services healthy
  ✓ Vitals streaming (Kafka → Cassandra)
  ✓ Alerts raised (Flink working)
  ✓ Frontend connected via WebSocket
  ✓ Demo scenario complete
  ✓ Ready for viva demo
```

---

## PHASE 4: Demo & Viva Prep (30 min)

**Agent generates demo script and talking points.**

```bash
# PHASE4_001: Generate demo script
cat > scripts/DEMO_SCRIPT.md << 'EOF'
# VitalStream Demo (5 minutes)

## Setup (ensure running)
docker-compose up -d
python simulator/monitor_sim.py &
# Wait 30 sec for services to stabilize

## Demo flow

### 1. ORWall Live (30 sec)
- Open http://localhost:5173
- Show ORWall with 3 live ORs
- "Every second, monitors send a reading to Kafka. We're streaming 6 readings/sec."

### 2. Alert Detection (60 sec)
- Trigger low BP scenario
- "Flink detected it in 2 seconds. See the alert in AlertQueue."
- Leave alert unacknowledged
- "Now we'll wait 10 minutes. Unacknowledged alerts auto-escalate."
- (Skip ahead 10 min in logs to show escalation)

### 3. Transaction Safety (30 sec)
- Show BedBoard with free recovery beds
- "If two surgeries end at the same time, both need a bed. MongoDB's ACID transaction makes sure only one gets REC-04."
- (Click demo button: "Book bed twice in parallel")
- "One succeeds, one fails. Safe."

### 4. Time-Series Query (30 sec)
- Click Patient John
- PatientDetail opens, VitalWaveform chart shows last 30 min
- "This came from Cassandra in <100ms. We store 518k readings/day and answer queries fast."

### 5. Closing (30 sec)
- "We used 4 big data tools. MongoDB for transactions, Kafka for streaming, Flink for smart alerts, Cassandra for history. Real-time + safe + scalable. Not just Excel."
EOF
```

**Talking points (per member):**
```
PUSHKAR:
"I built the transaction engine. MongoDB stores patients, cases, beds, orders, alerts. 
The tricky part was bed reservation: two surgeries can't use the same recovery bed. 
I use ACID transactions to make sure exactly one wins. Here's the test: [show console output]"

MEMBER 2:
"I'm the data pipes. Kafka brings in 6 vital readings per second from the monitors. 
The readings are ordered, durable, and replayable. If Flink crashes, it resumes from Kafka. 
And Cassandra is the archive. We write 518k readings a day and query the recent ones in <100ms."

MEMBER 3:
"I wrote the alert logic in Flink. Every 30 seconds, I check: is blood pressure too low? 
Is oxygen falling? If yes, raise an alert. And if a nurse doesn't acknowledge in 10 minutes, 
it escalates automatically. Spreadsheets can't do stateful stream processing."

MEMBER 4:
"I designed Cassandra for scale. We partition by patient and date so no single partition gets slammed. 
One week of data is ~3.6M readings, and we can query any patient's last 30 minutes in <100ms. 
That's why we don't use a traditional database: it chokes on this volume."
```

---

## USER PROMPTS (Yes/No Flow)

**Run this before starting automation:**

```
=========================================
  VitalStream Setup (Deadline: Tomorrow)
=========================================

Question 1: Clean up old HealthInsight files?
  [YES] → Remove old components, start fresh
  [NO]  → Keep old files, use new folder structure alongside

Your choice: _______

Question 2: Data source?
  [SYNTHETIC] → Generated vitals, no download (ready in 5 min)
  [VITALDB]   → Real surgical recordings (need internet, 5min+ download)

Your choice: _______

Question 3: Database (time-series vitals)?
  [CASSANDRA]  → Distributed, scale-out friendly (need ≥6GB RAM)
  [TIMESCALEDB] → Lighter, PostgreSQL extension (<2GB RAM)

Your choice: _______

Question 4: Start Phase 1 now? (Docker + folders)
  [YES] → Begin immediately (30–45 min)
  [NO]  → I'll run later

Your choice: _______

=========================================
  Starting automation...
=========================================
```

---

## QUICK CHECKPOINTS

After each phase, **user confirms** with:

```
✓ Phase X complete. Review output above.

Continue to Phase X+1?
  [YES] → Proceed
  [NO]  → Pause (I'll resume later)

Your choice: _______
```

---

## TROUBLESHOOTING (If Failures)

Agent will detect failures and prompt:

```
✗ Error in [Phase/Step]
  Issue: [description]
  Fix: [automated recovery or manual step]

Retry automatically?
  [YES] → Run step again
  [NO]  → Skip and continue (may break downstream)

Your choice: _______
```

---

## FINAL CHECKLIST (Before Viva)

```
✓ All services up (docker-compose ps)
✓ Simulator running (6 ORs streaming)
✓ Frontend responsive (http://localhost:5173)
✓ One bed-conflict test passes
✓ One alert scenario complete (vital → alert → screen <3s)
✓ One escalation demo (unack'd → escalates)
✓ Each member can explain their tool
✓ Demo script memorized
✓ Talking points ready

Ready for 5-minute viva demo.
```

---

## EMERGENCY MODE (12 hours left)

If time runs short, **skip these:**
- Multi-partition Cassandra queries (do single-day only)
- Flink checkpoint recovery testing (trust it works)
- Frontend polish (minimal design is acceptable)

**Keep these (demo-critical):**
- Kafka + simulator (vitals streaming)
- MongoDB bed transaction (one success/failure demo)
- Flink alert detection (low BP → alert in 2 sec)
- Frontend ORWall (show live vitals)

