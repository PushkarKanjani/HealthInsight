# VitalStream — Team Contracts & Task Breakdown

---

## Overview

Each member owns one big data tool. The contract between you is simple:
- **Inputs:** documented schemas (topics, collections, tables).
- **Outputs:** agreed-upon structure, no surprises.
- **Interface:** Kafka topics and MongoDB collections are your shared API.

---

## Member 1: Pushkar (MongoDB)

### Your Responsibility
Patient records, case lifecycle, bed & room management, orders, alerts, and transactional safety (no double-bookings, no conflicts).

### Collections You Own

#### 1. `patients`
**Purpose:** Demographic and clinical context.
**Schema:**
```javascript
{
  patient_id: "john-52-synthea",          // Unique ID (from Synthea)
  name: "John Doe",
  age: 52,
  gender: "M",
  blood_type: "O+",
  allergies: ["penicillin", "latex"],     // Array, allow empty
  chronic_conditions: ["hypertension", "type-2-diabetes"],
  weight_kg: 85,
  height_cm: 180,
  source: "synthea",                      // Marker: all patients are synthetic
  created_at: ISODate("2026-10-25T08:00:00Z"),
  updated_at: ISODate("2026-10-25T08:00:00Z")
}
```
**Indexes:** `{patient_id: 1}`, `{name: 1}`.
**Read-heavy.** Populated once at startup from Synthea CSV.

---

#### 2. `cases`
**Purpose:** Surgery lifecycle. One document per operating room session.
**Schema:**
```javascript
{
  case_id: "5421",                         // Unique (timestamp-based or UUID)
  patient_id: "john-52-synthea",
  or_id: "OR-2",                           // Operating room 1–6
  surgeon_name: "Dr. Sarah Smith",
  scheduled_start: ISODate("2026-10-25T09:00:00Z"),
  actual_start: ISODate("2026-10-25T09:05:00Z"),
  actual_end: ISODate("2026-10-25T11:30:00Z"),
  anesthesiologist: "Dr. Brown",
  procedure_type: "Appendectomy",
  estimated_duration_minutes: 120,
  
  // Recovery bed reservation (linked to your `beds` collection)
  recovery_bed_reserved: "REC-04",         // Null until reserved
  recovery_bed_assigned_at: ISODate("2026-10-25T09:30:00Z"),
  
  // Handoff to ward (later phase)
  ward_bed_reserved: null,                 // Null unless extended stay
  ward_bed_assigned_at: null,
  
  case_status: "in_progress",              // Enum: scheduled, in_progress, completed, discharged
  notes: "Routine procedure, no complications",
  
  created_at: ISODate("2026-10-25T08:45:00Z"),
  updated_at: ISODate("2026-10-25T11:31:00Z")
}
```
**Indexes:** `{case_id: 1}`, `{or_id: 1, case_status: 1}`, `{patient_id: 1}`, `{actual_start: -1}`.

**Transactional Requirement:** Bed reservation must be atomic.
```javascript
// POST /api/beds/reserve
// Body: { case_id: "5421", bed_id: "REC-04" }

session = start_session()
session.start_transaction()

try:
  // 1. Check bed is free
  bed = db.beds.findOne({bed_id: "REC-04", available: true}, session)
  if (!bed):
    abort_transaction()
    throw Error("Bed not available")

  // 2. Reserve it
  db.beds.updateOne(
    {bed_id: "REC-04"},
    {$set: {available: false, current_occupant_case_id: "5421"}},
    {session}
  )

  // 3. Update case
  db.cases.updateOne(
    {case_id: "5421"},
    {$set: {recovery_bed_reserved: "REC-04", recovery_bed_assigned_at: now}},
    {session}
  )

  session.commit_transaction()
  return {success: true}

catch error:
  session.abort_transaction()
  throw error
```

---

#### 3. `beds`
**Purpose:** Room and bed availability tracking.
**Schema:**
```javascript
{
  bed_id: "REC-04",
  bed_type: "recovery",                    // Enum: or, recovery, ward
  ward: "PACU",                            // Post-Anesthesia Care Unit
  capacity: 1,                             // Single bed
  
  available: true,                         // Boolean: free or occupied
  current_occupant_case_id: null,          // Case ID if occupied, else null
  occupant_since: null,
  
  last_cleaned_at: ISODate("2026-10-25T08:00:00Z"),
  maintenance_status: "operational",       // Enum: operational, maintenance, quarantine
  
  created_at: ISODate("2026-10-20T10:00:00Z"),
  updated_at: ISODate("2026-10-25T10:15:00Z")
}
```
**Indexes:** `{bed_type: 1, available: 1}`, `{bed_id: 1}`.

**Sample data (init at startup):**
```javascript
// 6 ORs
{ bed_id: "OR-1", bed_type: "or", ward: "Main OR", available: true, ... }
{ bed_id: "OR-2", bed_type: "or", ward: "Main OR", available: true, ... }
{ bed_id: "OR-3", bed_type: "or", ward: "Main OR", available: true, ... }
{ bed_id: "OR-4", bed_type: "or", ward: "Main OR", available: true, ... }
{ bed_id: "OR-5", bed_type: "or", ward: "Main OR", available: true, ... }
{ bed_id: "OR-6", bed_type: "or", ward: "Main OR", available: true, ... }

// 6 recovery beds
{ bed_id: "REC-01", bed_type: "recovery", ward: "PACU", available: true, ... }
{ bed_id: "REC-02", bed_type: "recovery", ward: "PACU", available: true, ... }
{ bed_id: "REC-03", bed_type: "recovery", ward: "PACU", available: true, ... }
{ bed_id: "REC-04", bed_type: "recovery", ward: "PACU", available: true, ... }
{ bed_id: "REC-05", bed_type: "recovery", ward: "PACU", available: true, ... }
{ bed_id: "REC-06", bed_type: "recovery", ward: "PACU", available: true, ... }
```

---

#### 4. `orders`
**Purpose:** Medication orders, with allergy checking at insert time.
**Schema:**
```javascript
{
  order_id: "ord-8821",
  case_id: "5421",
  patient_id: "john-52-synthea",
  
  medication: "Epinephrine",               // Drug name
  dose: "1",
  dose_unit: "mg",
  route: "IV",                             // Enum: IV, IM, oral, topical
  frequency: "as_needed",                  // Enum: once, every_X_hours, as_needed
  
  indication: "Hypotension during surgery",
  contraindications_checked: true,
  allergic_to_drug: false,                 // Set to false at order time (from patient.allergies)
  
  created_at: ISODate("2026-10-25T09:10:00Z"),
  created_by: "Dr. Smith",
  
  administered_at: null,                   // Null until given
  administered_by: null,
  
  status: "active"                         // Enum: active, administered, cancelled
}
```
**Indexes:** `{case_id: 1}`, `{patient_id: 1}`.

**Validation Rule (at insert):**
```javascript
// POST /api/orders
// Body: { case_id: "5421", medication: "Epinephrine", ... }

order_obj.allergic_to_drug = patient.allergies.includes(order_obj.medication)
if (order_obj.allergic_to_drug):
  return Error(400, "Patient allergic to " + order_obj.medication)

db.orders.insertOne(order_obj)
```

---

#### 5. `alerts`
**Purpose:** Alerts raised by Flink, acknowledged by nurses.
**Schema:**
```javascript
{
  alert_id: "alrt-9932",                  // Unique (UUID or timestamp)
  case_id: "5421",
  patient_id: "john-52-synthea",
  
  alert_type: "BP_LOW",                   // Enum: BP_LOW, O2_FALLING, HR_ABNORMAL, TEMP_ABNORMAL
  severity: "high",                        // Enum: low, medium, high, critical
  
  raised_at: ISODate("2026-10-25T09:47:00Z"),
  reason: "Systolic BP 88 mmHg for 30 seconds",
  flink_event_id: "flink-evt-12345",       // Trace back to Flink job
  
  acknowledged: false,
  acknowledged_by: null,                   // Nurse name
  acknowledged_at: null,
  
  escalated: false,                        // True if unack'd > 10 min
  escalated_at: null,
  escalation_target: "charge_nurse_pager",
  
  resolved: false,                         // Manually marked by clinician
  resolved_at: null,
  resolution_note: null,
  
  created_at: ISODate("2026-10-25T09:47:00Z"),
  updated_at: ISODate("2026-10-25T09:47:00Z")
}
```
**Indexes:** `{case_id: 1, raised_at: -1}`, `{acknowledged: 1, raised_at: -1}`, `{escalated: 1}`.

**Change Stream (for frontend):**
```javascript
// Backend listens to this
async def watch_alerts():
  async with db.alerts.watch([
    {$match: {operationType: {$in: ["insert", "update"]}}}
  ]) as stream:
    async for change in stream:
      # Push via WebSocket to browser
      await websocket.send_json(change)
```

---

#### 6. `escalations`
**Purpose:** Track unacknowledged alerts that have been escalated.
**Schema:**
```javascript
{
  escalation_id: "esc-123",
  alert_id: "alrt-9932",
  case_id: "5421",
  
  escalated_at: ISODate("2026-10-25T09:57:00Z"),
  escalation_level: 1,                      // 1 = charge nurse, 2 = medical director
  target_role: "charge_nurse",
  target_pager_id: "pager-cs-01",           // Simulated
  
  acknowledged: false,
  acknowledged_by: null,
  acknowledged_at: null,
  
  created_at: ISODate("2026-10-25T09:57:00Z"),
  updated_at: ISODate("2026-10-25T09:57:00Z")
}
```

---

### Your Tasks

**Phase 1: Schema & Setup**
- [ ] Design and validate all 6 collections.
- [ ] Set up MongoDB replica set (for transactions).
- [ ] Create indexes.
- [ ] Write schema documentation.

**Phase 2: API Endpoints (with fastapi)**
- [ ] `POST /api/cases` — Create a new case (check OR is free).
- [ ] `GET /api/cases/active` — List all in-progress cases.
- [ ] `POST /api/beds/reserve` — Reserve a bed (ACID transaction).
- [ ] `GET /api/beds/available` — List free beds.
- [ ] `POST /api/orders` — Create an order (allergy check).
- [ ] `GET /api/alerts/unacknowledged` — List alerts needing action.
- [ ] `POST /api/alerts/{alert_id}/acknowledge` — Nurse acknowledges.
- [ ] `GET /api/patients/{patient_id}` — Fetch patient context (allergies, conditions).

**Phase 3: Transactions & Safety**
- [ ] Write and test the bed-reservation transaction (double-booking test).
- [ ] Test order insert with allergy rejection.
- [ ] Test concurrent acknowledgements (same alert ack'd twice = idempotent).

**Phase 4: Change Streams**
- [ ] Set up MongoDB change stream on `alerts` collection.
- [ ] Connect to FastAPI WebSocket, push new/updated alerts to frontend.

**Phase 5: Testing**
- [ ] Write a script that tries to book the same bed twice in parallel → verify one fails.
- [ ] Verify allergy blocking works.

---

## Member 2: Kafka + Cassandra Consumer

### Your Responsibility
Event streaming (vital signs from simulated monitors), durable message ordering, and writing to Cassandra.

### Topics You Own

#### `vitals.raw`
**Purpose:** Every heartbeat, blood pressure, oxygen reading from monitors.
**Partition count:** 6 (one per OR, so all readings from OR-2 always go to partition 2).
**Schema (Avro or JSON):**
```json
{
  "or_id": "OR-2",
  "patient_id": "john-52-synthea",
  "case_id": "5421",
  "timestamp_unix_ms": 1698225600000,      // Millisecond precision
  "heart_rate": 74,                        // Beats per minute
  "systolic_bp": 120,                      // mmHg
  "diastolic_bp": 80,                      // mmHg
  "oxygen_sat": 97,                        // Percent (0–100)
  "temperature_c": 36.8,                   // Celsius
  "respiratory_rate": 16,                  // Breaths per minute
  "source": "simulator"                    // Marker
}
```
**Retention:** 7 days (to support replay).

#### `cases.events`
**Purpose:** Case lifecycle events (started, moved, ended).
**Partition count:** 1 (ordering matters; all case events in order).
**Schema:**
```json
{
  "case_id": "5421",
  "event_type": "case_started",            // Enum: case_started, case_moved, case_ended
  "timestamp_unix_ms": 1698225600000,
  "or_id": "OR-2",
  "patient_id": "john-52-synthea",
  "data": {
    "surgeon": "Dr. Smith",
    "previous_or": null                    // Null if case_started, or_id if case_moved
  }
}
```

---

### Cassandra Table You Consume Into

```cql
CREATE TABLE vitalstream.vitals_by_patient_day (
  patient_id TEXT,
  bucket_date DATE,              -- Partition key (e.g., 2026-10-25)
  timestamp_seconds BIGINT,      -- Clustering column (time within day)
  or_id TEXT,
  case_id TEXT,
  heart_rate INT,
  systolic_bp INT,
  diastolic_bp INT,
  oxygen_sat INT,
  temperature DECIMAL,
  respiratory_rate INT,
  
  PRIMARY KEY ((patient_id, bucket_date), timestamp_seconds)
) WITH CLUSTERING ORDER BY (timestamp_seconds DESC)
  AND default_time_to_live = 2592000;  -- 30 days
```

---

### Your Tasks

**Phase 1: Kafka Setup**
- [ ] Create topics: `vitals.raw` (6 partitions), `cases.events` (1 partition).
- [ ] Test producing sample messages by hand.
- [ ] Document retention policy (7 days).

**Phase 2: Monitor Simulator**
- [ ] Build a Python script (`simulator/monitor_sim.py`) that:
  - Reads your Synthea patients from CSV.
  - For each of 6 "operating rooms", generates a case.
  - Replays VitalDB recordings (or synthetic vitals if you prefer) at 1 reading/sec to `vitals.raw` with a speed factor (e.g., 10x real-time for demo).
  - Sends case events to `cases.events`.
- [ ] Make it configurable (how many ORs, how fast, duration).

**Phase 3: Consumer → Cassandra**
- [ ] Write a Kafka consumer (Python + cassandra-driver) that:
  - Reads from `vitals.raw` in order.
  - Batches 10 seconds of readings.
  - Writes to `vitals_by_patient_day` in Cassandra.
  - Handles write failures gracefully (retry logic).
- [ ] Test that queries like "Show me Patient X's vitals for 2026-10-25, last 30 min" return in <100ms.

**Phase 4: Load Testing**
- [ ] Run the simulator for 1 hour at normal speed, 6 ORs.
- [ ] Measure: writes/sec to Cassandra, latency, any dropped messages.
- [ ] Report: "We sustained 6 vitals/sec for 1 hour with <5ms write latency."

**Phase 5: Kafka Lag Monitoring**
- [ ] Write a script that reports Kafka consumer lag (how far behind you are in the topic).
- [ ] Expose this via a REST endpoint that the frontend can call for the "Pipeline Health" panel.

---

## Member 3: Flink

### Your Responsibility
Stateful stream processing. Watch vitals, detect problems, raise alerts.

### Jobs You Own

#### Job 1: Alert Detection

**Input:** `vitals.raw` from Kafka.
**Output:** `alerts.raised` (back to Kafka) and directly to MongoDB `alerts` collection.
**Logic (pseudocode):**

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.window import TumblingEventTimeWindows
from pyflink.common.serializer import Serializer

env = StreamExecutionEnvironment.get_execution_environment()

# Source: Kafka vitals.raw
vitals = env.add_source(...)

# 30-second window per patient, detect patterns
def detect_alerts(readings):
  # readings = list of vitals for one patient in 30 sec window
  alerts = []
  
  avg_systbp = mean([r.systolic_bp for r in readings])
  min_o2 = min([r.oxygen_sat for r in readings])
  o2_trend = readings[-1].oxygen_sat - readings[0].oxygen_sat
  
  if avg_systbp < 90:
    alerts.append({
      alert_type: "BP_LOW",
      severity: "high" if avg_systbp < 80 else "medium",
      reason: f"Avg SystBP {avg_systbp}"
    })
  
  if min_o2 < 94:
    alerts.append({
      alert_type: "O2_LOW",
      severity: "high" if min_o2 < 90 else "medium",
      reason: f"Min O2 {min_o2}%"
    })
  
  if o2_trend < -5:  # Dropped 5+ points in 30 sec
    alerts.append({
      alert_type: "O2_FALLING",
      severity: "high",
      reason: f"O2 fell {abs(o2_trend):.1f}% in 30 seconds"
    })
  
  return alerts

windowed = vitals \
  .key_by(lambda v: v.patient_id) \
  .window(TumblingEventTimeWindows.of_seconds(30)) \
  .process(detect_alerts)

# Deduplicate: only raise same alert once per 5 minutes
deduped = windowed.key_by(lambda a: (a.patient_id, a.alert_type)) \
  .process(AlertDeduplicator(suppress_duration_seconds=300))

# Sink: Kafka + MongoDB
deduped.add_sink(KafkaSink(..., topic='alerts.raised'))
deduped.add_sink(MongoDBSink(..., collection='alerts'))

env.execute("AlertDetection")
```

---

#### Job 2: Escalation Timer

**Input:** `alerts.raised` and `alerts.acknowledged` from Kafka.
**Output:** MongoDB `escalations` collection (and optionally a `alerts.escalated` topic).
**Logic:**

```python
from pyflink.common.typeinfo import Types

alerts_raised = env.add_source(KafkaSource(..., topic='alerts.raised'))
alerts_acked = env.add_source(KafkaSource(..., topic='alerts.acknowledged'))

# Union both streams
all_events = alerts_raised.union(alerts_acked)

# Keyed by alert_id, maintain state: {alert_id -> (raised_time, acked?)}
def escalation_logic(key, events, context):
  state = context.get_state(...)  # {raised_at, acknowledged}
  
  for event in events:
    if event.type == "raised":
      state['raised_at'] = event.timestamp
      state['acknowledged'] = False
    elif event.type == "acknowledged":
      state['acknowledged'] = True
  
  # Check: if raised but unack'd for 10 min, escalate
  elapsed = now - state['raised_at']
  if not state['acknowledged'] and elapsed > 600_000:  # 10 min in ms
    yield {
      escalation_id: uuid(),
      alert_id: key,
      escalated_at: now,
      escalation_level: 1
    }

escalated = all_events.key_by(lambda e: e.alert_id) \
  .process(EscalationLogic())

escalated.add_sink(MongoDBSink(..., collection='escalations'))

env.execute("EscalationTimer")
```

---

### Your Tasks

**Phase 1: Flink Setup**
- [ ] Deploy Flink cluster (JobManager + TaskManager) via Docker.
- [ ] Verify it's running: `http://localhost:8081`.
- [ ] Test a simple "pass-through" job to verify Kafka source works.

**Phase 2: Alert Detection Job**
- [ ] Implement the windowed aggregation logic (30 sec window per patient).
- [ ] Define thresholds (BP < 90, O2 < 94, falling trend).
- [ ] Implement deduplication (suppress same alert type for same patient for 5 min).
- [ ] Test with simulated vitals.

**Phase 3: Escalation Timer Job**
- [ ] Track alert lifetime (raised time → ack time).
- [ ] Auto-escalate if unack'd > 10 min.
- [ ] Write to MongoDB `escalations` collection.
- [ ] Test: raise an alert, wait 10 min, verify escalation triggers.

**Phase 4: State Management**
- [ ] Use Flink's managed state (not in-memory) so job survives restarts.
- [ ] Enable checkpoints every 5 minutes.
- [ ] Test: kill Flink at 9:46, restart at 9:47, verify no alerts lost.

**Phase 5: Testing & Metrics**
- [ ] Run a 30-minute demo scenario: stable → low BP alert → escalate.
- [ ] Report alert detection latency (from vital reading to alert visible on screen).
- [ ] Expose Flink metrics (processed records/sec, checkpoint lag) via REST endpoint.

---

## Member 4: Cassandra

### Your Responsibility
High-throughput time-series storage, schema design, partitioning strategy.

### Table You Own

```cql
CREATE TABLE vitalstream.vitals_by_patient_day (
  patient_id TEXT,
  bucket_date DATE,
  timestamp_seconds BIGINT,
  or_id TEXT,
  case_id TEXT,
  heart_rate INT,
  systolic_bp INT,
  diastolic_bp INT,
  oxygen_sat INT,
  temperature DECIMAL,
  respiratory_rate INT,
  
  PRIMARY KEY ((patient_id, bucket_date), timestamp_seconds)
) WITH CLUSTERING ORDER BY (timestamp_seconds DESC)
  AND default_time_to_live = 2592000;  -- Auto-delete after 30 days
```

---

### Your Tasks

**Phase 1: Cassandra Setup**
- [ ] Deploy Cassandra via Docker.
- [ ] Create keyspace `vitalstream`.
- [ ] Create the `vitals_by_patient_day` table.
- [ ] Create indexes if needed.

**Phase 2: Schema & Partitioning Justification**
- [ ] Document why you chose (patient_id, bucket_date) as partition key:
  - Distributes writes across patients and days (no hot partition).
  - Allows query: "Get Patient X's vitals for Day Y".
- [ ] Show that 6 ORs × 86,400 seconds/day = 518k readings/day = sustainable write load.

**Phase 3: Query Patterns**
- [ ] Write efficient queries:
  ```cql
  -- 1. Last 30 min of patient vitals
  SELECT * FROM vitals_by_patient_day
  WHERE patient_id = 'john-52'
    AND bucket_date = '2026-10-25'
    AND timestamp_seconds > <30min_ago>
  ORDER BY timestamp_seconds DESC
  LIMIT 1800;

  -- 2. All vitals for patient over a date range (multi-partition scan)
  SELECT * FROM vitals_by_patient_day
  WHERE patient_id = 'john-52'
    AND bucket_date >= '2026-10-20'
    AND bucket_date <= '2026-10-25'
  ORDER BY bucket_date DESC, timestamp_seconds DESC
  LIMIT 10000;
  ```
- [ ] Measure: single-partition query <100ms, multi-partition <500ms.

**Phase 4: Load Testing**
- [ ] Write a load test (Python + cassandra-driver):
  - Simulate 6 ORs, 1 reading/sec for 1 hour.
  - Measure: write latency (p50, p95, p99).
  - Expected: 6 writes/sec, <10ms latency.
- [ ] Report: "Cassandra sustained 6 writes/sec with p95 latency = 8ms."

**Phase 5: Retention & Operations**
- [ ] Verify TTL works (data older than 30 days auto-deletes).
- [ ] Monitor disk space.
- [ ] If data grows, plan for replication (replicate to 2 nodes).
- [ ] Document: "Scale from 6 ORs to 30 ORs by replicating to 3 nodes."

---

## All Members: Frontend + Shared Endpoints

### Shared Responsibility
- Set up FastAPI gateway (routes, WebSocket).
- Build the 6-screen UI: ORWall, AlertQueue, BedBoard, PatientDetail, VitalWaveform, PipelineHealth.

### Who Builds What
- **Pushkar:** ORWall + PatientDetail (shows patient context, allergies, orders).
- **Member 2:** BedBoard + PipelineHealth (Kafka lag, Cassandra latency).
- **Member 3:** AlertQueue (real-time unack'd alerts from WebSocket).
- **Member 4:** VitalWaveform (fetches 30 min of vitals from Cassandra, uPlot chart).
- **All:** Grid layout, color scheme, WebSocket hook, context/state management.

---

## Milestone Schedule (4 weeks)

| Week | Pushkar | Member 2 | Member 3 | Member 4 |
|------|---------|----------|----------|----------|
| **1** | Schema design, setup MongoDB replica set | Kafka topics, monitor simulator outline | Flink cluster setup | Cassandra table creation, schema docs |
| **2** | API endpoints (cases, beds, orders) | Monitor simulator working, Kafka producer | Alert detection job (code) | Query pattern validation, load test setup |
| **3** | Bed reservation transaction, allergy check, change streams | Cassandra consumer, lag monitoring | Escalation timer job, state management | Load test (6 ORs, 1 hour), TTL validation |
| **4** | Testing (double-booking), frontend integration | Testing (Kafka→Cassandra pipeline), endpoint | Testing (escalation demo), metrics endpoint | Documentation, scale-out plan |

---

## Demo Script (5 minutes)

1. **ORWall (30 sec):** Show 3 ORs with live vitals streaming. "Every heartbeat is coming from Kafka, updated every second."
2. **Alert Scenario (60 sec):** Trigger a BP low alert by script. "Flink detected it in 2 seconds. See it on screen. Now let's leave it unacknowledged." Wait 10 min... escalation fires. "Unacknowledged for 10 min, now it escalated automatically."
3. **Bed Conflict (30 sec):** Try to book the same recovery bed twice in parallel. One succeeds, one fails. "MongoDB transaction made sure."
4. **VitalWaveform (30 sec):** Click a patient, see 30-min waveform. "This came from Cassandra, which stores all 518k daily readings."
5. **Close:** "We used 4 big data tools instead of a spreadsheet. Real streaming + real transactions + real history."

---

## Definition of Done

- [ ] All services up (Kafka, Flink, MongoDB, Cassandra, FastAPI) via `docker-compose up`.
- [ ] Monitor simulator running, 6 ORs streaming vitals.
- [ ] Web app accessible, all 6 screens rendered.
- [ ] One bed-conflict test passes (double-booking rejected).
- [ ] One alert scenario runs end-to-end (vital → Flink → MongoDB → screen, <3 sec).
- [ ] One escalation demo runs (unack'd alert → escalates after 10 min).
- [ ] Each member can explain their tool in viva (why this tool, what it does, what breaks without it).

