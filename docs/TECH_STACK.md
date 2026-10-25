# VitalStream — Tech Stack & Configuration

---

## Overview

This is the complete technical choice for the perioperative command center. Each tool is pinned to a version, and each component has one job.

**Deployment:** Docker Compose (local development). All services on the same host, shared volumes for data.

---

## BACKEND SERVICES (Docker)

### 1. Apache Kafka 3.6.1
**Role:** Event stream backbone for vital signs.

```yaml
# docker-compose.yml snippet
kafka:
  image: confluentinc/cp-kafka:7.6.0
  environment:
    KAFKA_BROKER_ID: 1
    KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
    KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
    KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
  ports:
    - "9092:9092"
  volumes:
    - kafka_data:/var/lib/kafka/data
```

**Topics (created on startup):**
- `vitals.raw` — 6 partitions (1 per OR). Schema: `{or_id, patient_id, timestamp, hr, systbp, diasbp, o2, temp}`.
- `cases.events` — 1 partition. Schema: `{case_id, event_type, timestamp, data}`. Event types: `case_started`, `case_ended`, `patient_moved`.
- `alerts.raised` — 1 partition. Schema: `{alert_id, case_id, alert_type, severity, timestamp, reason}`.
- `alerts.acknowledged` — 1 partition. Schema: `{alert_id, acknowledged_by, ack_time}`.

**Member 2 owns:** Kafka setup, monitor simulator → Kafka producer, consumer → Cassandra writer.

---

### 2. Apache Flink 1.18.1
**Role:** Stateful stream processing. Watches vitals, detects patterns, raises alerts.

```yaml
flink_jobmanager:
  image: flink:1.18.1-java17
  command: jobmanager
  ports:
    - "8081:8081"  # Web UI
  environment:
    - JOB_MANAGER_RPC_ADDRESS=flink_jobmanager
  volumes:
    - ./flink/jobs:/opt/flink/jars
    - ./flink/config:/opt/flink/conf

flink_taskmanager:
  image: flink:1.18.1-java17
  command: taskmanager
  environment:
    - JOB_MANAGER_RPC_ADDRESS=flink_jobmanager
```

**Flink Jobs (Python with PyFlink):**

1. **Alert Detection Job**
   - Input: `vitals.raw` (Kafka)
   - Logic:
     - 30-second tumbling window per patient.
     - If `SystBP < 90` for entire window → raise `BP_LOW` alert.
     - If `O2` drops >5 in 60 seconds → raise `O2_FALLING` alert.
     - Deduplicate: don't re-raise the same alert within 5 minutes.
   - Output: `alerts.raised` (Kafka)

2. **Escalation Timer Job**
   - Input: `alerts.raised` and `alerts.acknowledged` (Kafka)
   - Logic:
     - Track unacknowledged alert lifetime.
     - If unacknowledged for >10 minutes → escalate to charge nurse queue.
   - Output: `alerts.escalated` (Kafka) → write to MongoDB collection `escalations`.

**Member 3 owns:** Flink job code, alert thresholds, testing with scenarios.

---

### 3. MongoDB 7.0 (Replica Set)
**Role:** ACID transactions on case, patient, bed, order, alert records.

```yaml
mongodb:
  image: mongo:7.0
  command: --replSet rs0 --bind_ip_all
  ports:
    - "27017:27017"
  volumes:
    - mongo_data:/data/db
  environment:
    MONGO_INITDB_DATABASE: vitalstream
```

**Init script (runs once):**
```javascript
// Set up replica set for transactions
rs.initiate({
  _id: "rs0",
  members: [{ _id: 0, host: "mongodb:27017" }]
})
```

**Collections:**

1. **cases**
   ```json
   {
     "case_id": "5421",
     "patient_id": "john-52",
     "or_id": "OR-2",
     "surgeon": "Dr. Smith",
     "scheduled_start": "2026-10-25T09:00:00Z",
     "actual_start": "2026-10-25T09:05:00Z",
     "actual_end": "2026-10-25T11:30:00Z",
     "recovery_bed_reserved": "REC-04",
     "case_status": "in_progress",  // scheduled, in_progress, completed
     "created_at": "2026-10-25T08:45:00Z"
   }
   ```

2. **patients**
   ```json
   {
     "patient_id": "john-52",
     "name": "John Doe",
     "age": 52,
     "gender": "M",
     "allergies": ["penicillin", "latex"],
     "conditions": ["hypertension", "diabetes"],
     "source": "synthea"  // synthetic, from Synthea dataset
   }
   ```

3. **beds**
   ```json
   {
     "bed_id": "REC-04",
     "bed_type": "recovery",  // or: or, recovery, ward
     "ward": "PACU",
     "current_occupant_case_id": null,
     "available": true,
     "last_updated": "2026-10-25T11:35:00Z"
   }
   ```

4. **orders**
   ```json
   {
     "order_id": "ord-8821",
     "case_id": "5421",
     "medication": "Epinephrine",
     "dose": "1 mg",
     "route": "IV",
     "condition_trigger": "if_systbp_below_90",
     "created_at": "2026-10-25T09:10:00Z",
     "administered_at": null
   }
   ```

5. **alerts**
   ```json
   {
     "alert_id": "alrt-9932",
     "case_id": "5421",
     "alert_type": "BP_LOW",
     "severity": "high",  // low, medium, high, critical
     "raised_at": "2026-10-25T09:47:00Z",
     "reason": "SystBP 88 for 30 seconds",
     "acknowledged": true,
     "acknowledged_by": "Nurse Sarah",
     "acknowledged_at": "2026-10-25T09:49:00Z",
     "escalated": false,
     "escalated_at": null
   }
   ```

6. **escalations** (unacknowledged alerts > 10 min)
   ```json
   {
     "escalation_id": "esc-123",
     "alert_id": "alrt-9932",
     "case_id": "5421",
     "escalated_at": "2026-10-25T09:57:00Z",
     "target": "charge_nurse_queue",
     "resolved": false
   }
   ```

**Indexes:**
- `cases`: `{case_id: 1}`, `{or_id: 1, case_status: 1}`, `{patient_id: 1}`.
- `alerts`: `{case_id: 1, raised_at: -1}`, `{acknowledged: 1, raised_at: -1}`.
- `beds`: `{bed_type: 1, available: 1}`.

**Transactions (sample):**
```python
# Bed reservation (Pushkar's task)
with client.start_session() as session:
    with session.start_transaction():
        # Check bed is free
        bed = db.beds.find_one({"bed_id": "REC-04", "available": True}, session=session)
        if not bed:
            raise Exception("Bed not available")
        
        # Reserve it
        db.beds.update_one(
            {"bed_id": "REC-04"},
            {"$set": {"available": False, "current_occupant_case_id": "5421"}},
            session=session
        )
        
        # Update case
        db.cases.update_one(
            {"case_id": "5421"},
            {"$set": {"recovery_bed_reserved": "REC-04"}},
            session=session
        )
        # If any step fails, entire transaction rolls back
```

**Change Streams (real-time updates to frontend):**
```python
# FastAPI will listen to this
async def watch_alerts():
    async with client.start_session() as session:
        async with db.alerts.watch(
            [{"$match": {"operationType": {"$in": ["insert", "update"]}}}],
            session=session
        ) as stream:
            async for change in stream:
                # Send via WebSocket to browser
                await websocket.send_json(change)
```

**Member 1 (Pushkar) owns:** MongoDB schema design, transaction logic, bed conflict resolution, alert logging.

---

### 4. Apache Cassandra 4.1
**Role:** High-throughput time-series storage for vital signs.

```yaml
cassandra:
  image: cassandra:4.1
  ports:
    - "9042:9042"
  environment:
    CASSANDRA_CLUSTER_NAME: vitalstream_cluster
    CASSANDRA_DC: datacenter1
    CASSANDRA_RACK: rack1
    CASSANDRA_SEEDS: cassandra
    JVM_HEAP_SIZE: 2G  # Adjust for your machine
  volumes:
    - cassandra_data:/var/lib/cassandra
```

**Keyspace & Table:**
```cql
CREATE KEYSPACE vitalstream WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

CREATE TABLE vitalstream.vitals (
  patient_id TEXT,
  bucket_date DATE,  -- partition by day (e.g., 2026-10-25)
  timestamp_seconds BIGINT,
  heart_rate INT,
  systolic_bp INT,
  diastolic_bp INT,
  oxygen_sat INT,
  temperature DECIMAL,
  PRIMARY KEY ((patient_id, bucket_date), timestamp_seconds)
) WITH CLUSTERING ORDER BY (timestamp_seconds DESC);

CREATE INDEX vitals_or_id ON vitalstream.vitals (or_id);
```

**Query pattern (fast):**
```cql
-- "Show me Patient john-52's vitals for 2026-10-25, last 30 minutes"
SELECT * FROM vitals
WHERE patient_id = 'john-52'
  AND bucket_date = '2026-10-25'
  AND timestamp_seconds > 1698225600  -- 30 min ago
ORDER BY timestamp_seconds DESC
LIMIT 1800;  -- 30 min × 60 sec
```

**Retention:**
```cql
ALTER TABLE vitalstream.vitals WITH default_time_to_live = 2592000;  -- 30 days
```

**Consumer (writes from Kafka):**
- Flink task or Kafka Connect reads `vitals.raw`, batches every 10 seconds, writes to Cassandra.
- ~518k readings/day = ~6 writes/second = Cassandra handles this easily.

**Member 4 owns:** Cassandra schema, partitioning strategy, load testing, retention policy.

---

### 5. FastAPI 0.109.0
**Role:** REST API gateway + WebSocket for live updates.

```yaml
fastapi_gateway:
  build: ./backend
  ports:
    - "5000:5000"
  environment:
    MONGODB_URI: mongodb://mongodb:27017/vitalstream
    KAFKA_BOOTSTRAP_SERVERS: kafka:9092
    CASSANDRA_HOST: cassandra
    CASSANDRA_KEYSPACE: vitalstream
  volumes:
    - ./backend:/app
  command: uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

**Key endpoints:**

```python
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REST Endpoints ---

@app.get("/api/cases/active")
async def get_active_cases():
    """Get all in-progress cases."""
    db = get_mongo_db()
    cases = list(db.cases.find({"case_status": "in_progress"}))
    return cases

@app.post("/api/cases")
async def create_case(case_data: dict):
    """Start a new case. Reserves an OR."""
    db = get_mongo_db()
    # Check OR is free
    if db.cases.find_one({"or_id": case_data["or_id"], "case_status": "in_progress"}):
        raise HTTPException(400, "OR already occupied")
    # Insert case
    result = db.cases.insert_one(case_data)
    return {"case_id": str(result.inserted_id)}

@app.post("/api/beds/reserve")
async def reserve_bed(case_id: str, bed_id: str):
    """Reserve a recovery bed for a case (ACID transaction)."""
    db = get_mongo_db()
    client = get_mongo_client()
    
    with client.start_session() as session:
        with session.start_transaction():
            bed = db.beds.find_one({"bed_id": bed_id, "available": True}, session=session)
            if not bed:
                raise HTTPException(400, "Bed not available")
            
            db.beds.update_one(
                {"bed_id": bed_id},
                {"$set": {"available": False, "current_occupant_case_id": case_id}},
                session=session
            )
            db.cases.update_one(
                {"case_id": case_id},
                {"$set": {"recovery_bed_reserved": bed_id}},
                session=session
            )
    
    return {"reserved": True, "bed_id": bed_id}

@app.post("/api/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, nurse_name: str):
    """Nurse acknowledges an alert."""
    db = get_mongo_db()
    from datetime import datetime
    
    db.alerts.update_one(
        {"alert_id": alert_id},
        {
            "$set": {
                "acknowledged": True,
                "acknowledged_by": nurse_name,
                "acknowledged_at": datetime.utcnow()
            }
        }
    )
    return {"acknowledged": True}

@app.get("/api/alerts/unacknowledged")
async def get_unacknowledged_alerts():
    """Get all unacknowledged alerts (for the queue on the UI)."""
    db = get_mongo_db()
    alerts = list(db.alerts.find({"acknowledged": False}).sort("raised_at", -1))
    return alerts

@app.get("/api/beds/available")
async def get_available_beds():
    """Get all free recovery beds."""
    db = get_mongo_db()
    beds = list(db.beds.find({"available": True}))
    return beds

# --- WebSocket for Live Vitals & Alerts ---

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """
    Client connects here.
    Pushes:
    - New vitals (every second for each OR)
    - New alerts
    - Escalations
    """
    await websocket.accept()
    
    # Watch MongoDB alerts collection for changes
    db = get_mongo_db()
    
    try:
        async with db.alerts.watch() as stream:
            async for change in stream:
                await websocket.send_json({
                    "type": "alert",
                    "data": change
                })
    except Exception as e:
        await websocket.close()

# Health check
@app.get("/health")
async def health():
    return {"status": "ok"}
```

---

## FRONTEND (Web UI)

### Stack
- **Framework:** React 18 + Vite 5.0 (handles HMR in Antigravity)
- **State:** React Context + WebSocket hook
- **Charts:** uPlot (lightweight, <10KB, real-time waveforms) or Recharts (easier)
- **Styling:** Tailwind CSS 3 + custom pastel palette
- **HTTP:** Fetch API (built-in)

```
frontend/
├── src/
│   ├── components/
│   │   ├── ORWall.jsx         (grid of 6 ORs, live vitals)
│   │   ├── PatientDetail.jsx   (waveforms, orders, allergy alerts)
│   │   ├── AlertQueue.jsx      (unacknowledged alerts, severity color)
│   │   ├── BedBoard.jsx        (recovery beds, availability)
│   │   ├── VitalWaveform.jsx   (uPlot chart)
│   │   └── PipelineHealth.jsx  (Kafka lag, Flink uptime, MongoDB ops/sec)
│   ├── hooks/
│   │   └── useWebSocket.js     (connect, auto-reconnect)
│   ├── context/
│   │   └── CasesContext.jsx    (global state for cases, alerts, beds)
│   └── App.jsx
├── package.json
├── vite.config.js
└── tailwind.config.js
```

### Design System (Pastel, Trustworthy, Minimal)

**Inspired by:** Jinga Life (warm, welcoming), MediSafe (clean, focused), but stripped to essentials.

**Color Palette:**
```css
:root {
  /* Neutral base */
  --bg-primary: #f8f9fa;      /* Soft off-white */
  --bg-secondary: #f0f2f5;    /* Very light gray */
  --bg-tertiary: #e9ecef;     /* Light gray */
  --text-primary: #2c3e50;    /* Deep blue-gray */
  --text-secondary: #7f8c8d;  /* Medium gray */
  
  /* Pastel alert colors */
  --pastel-green: #d4edda;    /* Calm green (normal) */
  --pastel-yellow: #fff3cd;   /* Warm yellow (warning) */
  --pastel-red: #f8d7da;      /* Soft red (alert) */
  --pastel-blue: #d1ecf1;     /* Cool blue (info) */
  
  /* Accent */
  --accent-green: #28a745;    /* For checkmarks, acks */
  --accent-orange: #fd7e14;   /* For medium severity */
  --accent-red: #dc3545;      /* For high severity */
  --border: #dee2e6;          /* Subtle borders */
  
  /* Typography */
  --font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.25rem;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-bold: 600;
}
```

**Component Examples:**

```jsx
// ORWall.jsx - Grid of 6 operating rooms
export function ORWall() {
  const { cases } = useContext(CasesContext);
  
  return (
    <div className="grid grid-cols-3 gap-4 p-6 bg-primary">
      {Array.from({ length: 6 }).map((_, i) => {
        const or_id = `OR-${i + 1}`;
        const caseData = cases.find(c => c.or_id === or_id && c.case_status === 'in_progress');
        
        return (
          <div key={or_id} className="p-4 rounded-lg border border-gray-300 bg-white shadow-sm">
            <div className="text-sm font-bold text-text-primary">{or_id}</div>
            {caseData ? (
              <div>
                <div className="text-xs text-text-secondary">{caseData.patient_id}</div>
                <div className="mt-2 space-y-1">
                  <VitalLine label="HR" value={caseData.latest_hr} unit="bpm" />
                  <VitalLine label="BP" value={`${caseData.latest_systbp}/${caseData.latest_diasbp}`} unit="mmHg" />
                  <VitalLine label="O₂" value={caseData.latest_o2} unit="%" />
                </div>
                <div className={`mt-3 px-2 py-1 rounded text-xs font-medium ${
                  caseData.latest_o2 < 94 ? 'bg-pastel-red text-red-700' :
                  caseData.latest_systbp < 90 ? 'bg-pastel-yellow text-orange-700' :
                  'bg-pastel-green text-green-700'
                }`}>
                  {caseData.latest_o2 < 94 ? '⚠ Low O₂' :
                   caseData.latest_systbp < 90 ? '⚠ Low BP' :
                   '✓ Stable'}
                </div>
              </div>
            ) : (
              <div className="text-sm text-text-secondary italic">Idle</div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function VitalLine({ label, value, unit }) {
  return (
    <div className="flex justify-between text-xs">
      <span className="text-text-secondary">{label}</span>
      <span className="font-medium text-text-primary">{value} {unit}</span>
    </div>
  );
}
```

```jsx
// AlertQueue.jsx - Unacknowledged alerts
export function AlertQueue() {
  const { alerts } = useContext(CasesContext);
  const unacked = alerts.filter(a => !a.acknowledged);
  
  return (
    <div className="p-6 bg-primary rounded-lg border border-gray-300">
      <div className="text-lg font-bold text-text-primary mb-4">Alerts ({unacked.length})</div>
      <div className="space-y-2">
        {unacked.map(alert => (
          <div
            key={alert.alert_id}
            className={`p-3 rounded flex items-center justify-between ${
              alert.severity === 'critical' ? 'bg-red-100 border-l-4 border-red-500' :
              alert.severity === 'high' ? 'bg-yellow-100 border-l-4 border-orange-500' :
              'bg-blue-100 border-l-4 border-blue-500'
            }`}
          >
            <div>
              <div className="text-sm font-medium text-text-primary">{alert.alert_type}</div>
              <div className="text-xs text-text-secondary">{alert.reason}</div>
            </div>
            <button
              onClick={() => acknowledgeAlert(alert.alert_id)}
              className="px-3 py-1 bg-accent-green text-white rounded text-xs font-medium hover:opacity-90"
            >
              ACK
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
```

```jsx
// useWebSocket.js - Live connection
export function useWebSocket(url) {
  const [data, setData] = useState(null);
  const ws = useRef(null);

  useEffect(() => {
    ws.current = new WebSocket(url);

    ws.current.onmessage = (event) => {
      const parsed = JSON.parse(event.data);
      setData(parsed);
    };

    ws.current.onerror = () => {
      console.error("WebSocket error");
      setTimeout(() => {
        // Auto-reconnect
        ws.current = new WebSocket(url);
      }, 3000);
    };

    return () => ws.current?.close();
  }, [url]);

  return data;
}
```

---

## DEPLOYMENT (docker-compose.yml)

```yaml
version: "3.8"

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.6.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_SYNC_LIMIT: 2
      ZOOKEEPER_INIT_LIMIT: 5

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

  mongodb:
    image: mongo:7.0
    command: --replSet rs0 --bind_ip_all
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
      - ./scripts/mongo-init.js:/docker-entrypoint-initdb.d/init.js

  cassandra:
    image: cassandra:4.1
    ports:
      - "9042:9042"
    environment:
      CASSANDRA_CLUSTER_NAME: vitalstream
      CASSANDRA_DC: datacenter1
      JVM_HEAP_SIZE: 2G
    volumes:
      - cassandra_data:/var/lib/cassandra
      - ./scripts/cassandra-init.cql:/docker-entrypoint-initdb.d/init.cql

  flink_jobmanager:
    image: flink:1.18.1-java17
    command: jobmanager
    ports:
      - "8081:8081"
    environment:
      - JOB_MANAGER_RPC_ADDRESS=flink_jobmanager
    volumes:
      - ./flink/jobs:/opt/flink/jars
      - flink_data:/tmp/flink-checkpoints

  flink_taskmanager:
    image: flink:1.18.1-java17
    command: taskmanager
    depends_on:
      - flink_jobmanager
    environment:
      - JOB_MANAGER_RPC_ADDRESS=flink_jobmanager
    volumes:
      - ./flink/jobs:/opt/flink/jars
      - flink_data:/tmp/flink-checkpoints

  fastapi_gateway:
    build: ./backend
    ports:
      - "5000:5000"
    depends_on:
      - mongodb
      - kafka
      - cassandra
    environment:
      MONGODB_URI: mongodb://mongodb:27017/vitalstream
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
      CASSANDRA_HOST: cassandra
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend/src:/app/src
    command: npm run dev -- --host 0.0.0.0

volumes:
  kafka_data:
  mongo_data:
  cassandra_data:
  flink_data:

networks:
  default:
    name: vitalstream
```

**Startup:**
```bash
docker-compose up -d

# Init MongoDB replica set (one time)
docker-compose exec mongodb mongosh --eval "rs.initiate()"

# Verify services
curl http://localhost:8081     # Flink
curl http://localhost:5000/health  # FastAPI
curl http://localhost:5173     # Frontend (Vite)
```

---

## Team Distribution

| Member | Component | Deliverable |
|---|---|---|
| **Pushkar** | MongoDB | Schema design, transaction logic (bed reservation, order entry, alert logging), test bed conflicts |
| **Member 2** | Kafka + Cassandra Consumer | Topic schema, monitor simulator → Kafka producer, Kafka → Cassandra pipeline, load test |
| **Member 3** | Flink | Alert detection job (BP low, O₂ falling, escalation timer), PyFlink setup, scenario testing |
| **Member 4** | Cassandra | Table design, partitioning (patient + date), index strategy, retention policy, scaling config |
| **All** | Frontend + FastAPI | Shared: endpoints, WebSocket, UI components. Divvy up screens: ORWall, AlertQueue, BedBoard, PatientDetail. |

---

## Medium-Effort Features (Visible on UI)

1. **ORWall:** Live 6-bed grid, each showing HR, BP, O₂ with color-coded status.
2. **AlertQueue:** Real-time unacknowledged alerts, one-click acknowledgement.
3. **BedBoard:** Recovery beds, free/occupied, reservation on a case.
4. **PatientDetail:** Click an OR → see patient allergies, recent orders, 30-min vital waveform.
5. **VitalWaveform:** Last 30 minutes of HR/BP/O₂ as a line chart (uPlot).
6. **PipelineHealth:** Show Flink uptime, MongoDB ops/sec, Cassandra write latency, Kafka consumer lag.
7. **Escalation Demo:** Unack'd alert > 10 min automatically escalates, visible in UI.
8. **Bed Conflict:** Try to book the same bed twice in parallel → one fails, UI shows error.

---

## Machine Requirements

- **RAM:** 8 GB (Cassandra 2GB, Flink 2GB, Kafka 1GB, MongoDB 500MB, rest 2.5GB).
- **Disk:** 20 GB (vital data accumulates).
- **CPU:** 4 cores, 2.5 GHz.

If RAM is lower, swap Cassandra for TimescaleDB (PostgreSQL extension, <500MB).

