# VitalStream — Start Here 🚀

**Deadline:** Tomorrow (24 hours)  
**Status:** Ready to launch  
**Time to demo-ready:** ~8 hours (with parallel work)  

---

## WHAT TO DO RIGHT NOW (5 minutes)

1. **Read this file** (you're doing it ✓)

2. **Understand the project:** Read `TOOL_ROLES_SIMPLE.md`
   - What does each tool do? (MongoDB, Kafka, Flink, Cassandra)
   - Why aren't we "just using Excel"?
   - What will the screen look like?

3. **Share with your team:**
   - Pushkar (MongoDB): Read `TEAM_CONTRACTS.md` → Your section
   - Member 2 (Kafka): Read `TEAM_CONTRACTS.md` → Your section
   - Member 3 (Flink): Read `TEAM_CONTRACTS.md` → Your section
   - Member 4 (Cassandra/TimescaleDB): Read `TEAM_CONTRACTS.md` → Your section

4. **Launch automation:** Follow `ANTIGRAVITY_SETUP.md`
   - Copy decision prompts into Antigravity
   - Answer 4 questions (yes/no)
   - Let agents run phases automatically
   - You confirm milestones (yes/no)

---

## THE 4-DECISION FLOW (2 minutes)

When you open Antigravity, you'll be asked:

```
1️⃣  Clean up old HealthInsight files?
    → YES (recommended): start fresh
    → NO: keep old files

2️⃣  Data source: synthetic vitals or real VitalDB?
    → SYNTHETIC (fast): ready in 2 min, good for tomorrow
    → VITALDB (credible): need 5+ min to download

3️⃣  Time-series DB: Cassandra or TimescaleDB?
    → CASSANDRA (if RAM ≥ 6GB): distributed, scale-out
    → TIMESCALEDB (if RAM < 6GB): lighter, simpler

4️⃣  Start Phase 1 now?
    → YES: begin immediately (takes 45 min)
    → NO: pause, resume later
```

That's it. After that, **AG automates everything.**

---

## THE 5-PHASE TIMELINE

| Phase | What AG Does | Time | You Do |
|---|---|---|---|
| **1** | Folders + Docker setup + databases | 45 min | Confirm: "Services up?" → YES |
| **2** | Member implementations (parallel) | 5 hours | Each member works on their task |
| **3** | E2E testing | 1 hour | Confirm: "All tests passed?" → YES |
| **4** | Demo prep + talking points | 20 min | Read script, memorize points |
| **5** | Final checks | 5 min | Confirm: "Ready for viva?" → YES |
| **TOTAL** | | ~8 hours | ~5 minutes of decisions |

---

## YOUR ROLE (During Automation)

- **You:** Answer yes/no prompts
- **AG:** Do all the coding, setup, testing
- **Members:** Implement your assigned component (Pushkar → MongoDB, etc.)

---

## KEY FILES (Read in This Order)

1. **TOOL_ROLES_SIMPLE.md** ← Start here (understand the project)
2. **ANTIGRAVITY_SETUP.md** ← Then here (how to launch)
3. **PROMPT_BOOK.md** ← Reference (what each phase does)
4. **TEAM_CONTRACTS.md** ← Share with team (each member's task)
5. **TECH_STACK.md** ← Technical reference (don't need to memorize)

---

## MEMBER QUICK REFERENCE

### Pushkar (MongoDB)
**Your job:** Patient records, cases, beds, orders, alerts. **Critical:** bed reservation must be atomic (no double-booking).

**What to expect:**
- AG generates MongoDB schemas
- AG generates FastAPI endpoints
- You test bed-conflict (book REC-04 twice in parallel → one fails)
- You test allergy blocking (order penicillin for allergic patient → rejected)

**Time commitment:** ~1.5 hours (mostly testing generated code)

### Member 2 (Kafka + Cassandra/TimescaleDB)
**Your job:** Stream vitals from monitors (6 readings/sec), archive to database, expose lag metrics.

**What to expect:**
- AG generates monitor simulator (outputs 6 vitals/sec to Kafka)
- AG generates Kafka → DB consumer (batched writes)
- You verify: 300 readings appear in database in 30 sec
- You test query latency: "Last 10 min of Patient X" returns in <100ms

**Time commitment:** ~1.5 hours (mostly verification + load test)

### Member 3 (Flink)
**Your job:** Watch vitals, detect patterns (low BP, falling O₂), raise alerts, auto-escalate after 10 min.

**What to expect:**
- AG generates alert detection job (30-sec window, thresholds)
- AG generates escalation timer job (track lifecycle)
- You submit jobs to Flink cluster
- You test: low BP alert triggers in <3 sec
- You test: unack'd alert escalates after 10 min

**Time commitment:** ~1.5 hours (job submission + scenario testing)

### Member 4 (Cassandra/TimescaleDB)
**Your job:** Schema design, partitioning strategy, prove it handles 518k readings/day.

**What to expect:**
- AG generates time-series schema (optimized partitions)
- AG generates load test (simulate 6 ORs for 10 min)
- You run load test: measure writes/sec and latency
- You report: "6 writes/sec, p95 latency 8ms" ✓

**Time commitment:** ~1 hour (mostly observation + reporting)

### All Members (Frontend)
**Your job:** Build React components (ORWall, AlertQueue, BedBoard, etc.), wire up WebSocket, show live data.

**What to expect:**
- AG generates skeleton components
- Each member implements their screen
- You verify WebSocket connects and data flows live
- You test: with simulator running, vitals appear on screen in real-time

**Time commitment:** ~2 hours (parallel, so overlaps with other phases)

---

## DEMO SCRIPT (5 minutes)

Tomorrow, you'll present this:

1. **ORWall live** (30 sec)
   - "Every second, monitors send vitals to Kafka. We're streaming 6 readings/sec."
   - Show ORWall with 3 live ORs, vitals updating every second.

2. **Alert detection** (60 sec)
   - Trigger low BP alert.
   - "Flink detected it in 2 seconds. See it on screen now."
   - Leave unacknowledged, wait 10 min (fast-forward in demo).
   - "Unacknowledged after 10 min → auto-escalated."

3. **Bed conflict** (30 sec)
   - Show recovery beds in BedBoard.
   - Click "Book REC-04" twice in parallel.
   - One succeeds, one fails.
   - "MongoDB ACID transaction made sure."

4. **Time-series query** (30 sec)
   - Click a patient → PatientDetail.
   - Show waveform chart (last 30 min of vitals).
   - "Cassandra stores 518k readings/day. This query returns in <100ms."

5. **Closing** (30 sec)
   - "MongoDB = transactions (safe). Kafka = streaming (durable). Flink = smart logic (stateful). Cassandra = scalable storage (fast). Four tools, not just Excel."

---

## TALKING POINTS (Per Member, ~30 seconds each)

### Pushkar
"I built the transaction layer. Every surgery has a case, and every case needs a bed. Two surgeries can't use the same recovery bed. I use MongoDB's ACID transactions to make sure exactly one gets each bed. [Show test output: one succeeds, one fails.] That's why we don't use Excel: spreadsheets can't enforce this safety."

### Member 2
"I'm the data pipes. Kafka brings in 6 readings per second from the 6 monitors. Those readings are ordered, durable, and replayable. If Flink crashes at 9:46, it resumes from 9:46 in Kafka — no readings are lost. And Cassandra is the archive. We write 518k readings a day and query recent ones in <100ms. Spreadsheets would be 100x slower."

### Member 3
"I wrote the alert logic. Every 30 seconds, I aggregate vitals for each patient. If blood pressure is low for the whole 30 seconds, I raise an alert. If oxygen is falling, I raise an alert. And if a nurse doesn't acknowledge in 10 minutes, it escalates automatically. [Show Flink UI, show escalation in MongoDB.] Spreadsheets can't do stateful stream processing."

### Member 4
"I designed the time-series database. We partition by patient and date, so no single partition gets slammed with 518k readings. One week of data is ~3.6 million readings. I can query any patient's last 30 minutes in <100ms. [Show load test results: 6 writes/sec, p95 latency 8ms.] That's why we use Cassandra: traditional databases choke on this volume."

---

## EMERGENCY PLAN (If Time Runs Out)

**At 6 hours left:** Skip these
- Deep testing (just do one scenario per phase)
- Frontend polish (minimal design is fine)
- Multi-partition queries (single-day only)

**Keep these (demo-critical):**
- Kafka + simulator working (vitals streaming)
- MongoDB bed transaction (one demo of success/failure)
- Flink alert detection (low BP → alert in 2 sec)
- Frontend ORWall (show live vitals)

**Result:** You can do a 5-minute demo with 4 core pieces instead of all 6 screens.

---

## TROUBLESHOOTING

**"Docker won't start"**
- Check: `docker-compose logs` for errors
- Solution: Usually requires restart (`docker-compose down && docker-compose up -d`)

**"Flink job failed"**
- Check: http://localhost:8081 → Failed jobs
- Solution: Check PyFlink installation, retry job submission

**"No data in database"**
- Check: Is simulator running? (`ps aux | grep simulator`)
- Check: Is Kafka flowing? (`kafkacat -b localhost:9092 -t vitals.raw`)
- Solution: Restart simulator and consumer

**"Frontend won't connect"**
- Check: Is FastAPI running? (`curl http://localhost:5000/health`)
- Check: WebSocket URL in `frontend/src/hooks/useWebSocket.js`
- Solution: Restart FastAPI and refresh browser

---

## FINAL CHECKLIST (Before Viva)

```
✓ All services running (docker-compose ps)
✓ Simulator flowing data (6 readings/sec in Kafka)
✓ Alerts appearing (check MongoDB)
✓ Frontend loads (http://localhost:5173)
✓ WebSocket connected (browser console: "Connected")
✓ One bed-conflict test passes
✓ One alert scenario works (<3 sec latency)
✓ One escalation demo (10 min timer)
✓ Demo script memorized
✓ Each member's talking points ready
✓ Laptop plugged in (battery not reliable)
```

---

## GO TIME ⏰

1. **Right now:** Read `TOOL_ROLES_SIMPLE.md` (15 min)
2. **Next:** Share `TEAM_CONTRACTS.md` with team (10 min)
3. **Then:** Open `ANTIGRAVITY_SETUP.md` and answer 4 questions (5 min)
4. **AG runs:** Phases 1–5 automate over next 8 hours (parallel work)
5. **Tomorrow morning:** Demo-ready. You present in 5 minutes. ✓

---

**Questions?** Refer back to:
- `PROMPT_BOOK.md` → How each phase works
- `TECH_STACK.md` → Technical details
- `TEAM_CONTRACTS.md` → Your specific task

Good luck! 🚀

