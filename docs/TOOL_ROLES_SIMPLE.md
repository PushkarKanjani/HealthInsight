# VitalStream: What Each Tool Does (Simple Explanation)

## The Application: Perioperative Command Center

You are watching 6 operating rooms. Inside each room, a patient is being monitored. Machines measure heart rate, blood pressure, oxygen, temperature every second. Nurses need to see this live. Surgeons need beds reserved without conflicts. Patients move from OR → Recovery → Ward. Everything must be reliable and fast.

---

## 1. MONGODB — The Patient & Case Record Store

**What it stores:** Patient information, surgery cases, OR schedules, medical orders, alerts, who acknowledged what.

**Example:**
- Patient John (age 52, allergies: penicillin)
- Case #5421: surgical start time 9:00 AM, surgeon Dr. Smith, OR-2, scheduled recovery bed REC-04
- Order: "Epinephrine 1mg if SystBP < 90" (written once, checked forever)
- Alert log: "SpO₂ dropped to 88% at 9:47 AM — acknowledged by Nurse Sarah at 9:49 AM"

**Why it's needed:**
- It is the source of truth. If you need to know "who is scheduled where", you ask MongoDB.
- It handles conflicts. Two surgeries can't use the same OR at the same time. MongoDB makes sure only one wins.
- It keeps history. Years later, you can ask "what happened during Case #5421?" and get the timeline.
- It is flexible. Patient records have different fields than cases, orders, or alerts. MongoDB doesn't force rigid tables.

**The simple job:** "Remember everything about patients, surgeries, and what nurses did."

---

## 2. KAFKA — The Live Vital Signs Stream

**What it carries:** Heart rate, blood pressure, oxygen, temperature readings from the monitors, one reading per second per patient.

**Example:**
```
9:45:32 → OR-2, Patient John, HR 72, SystBP 118, O2 98%
9:45:33 → OR-2, Patient John, HR 73, SystBP 119, O2 98%
9:45:34 → OR-2, Patient John, HR 74, SystBP 120, O2 97%
(6 ORs × 1 reading/sec = 6 readings/sec going all day)
```

**Why it's needed:**
- **Live, in order, and persistent.** If a CPU dies at 9:46, when it comes back at 9:47, it can ask "give me everything since 9:45" and resume. Nothing is lost.
- **Decoupling.** The monitors don't know about Flink or Cassandra. They just send to Kafka. Later, you can add new consumers (a new dashboard, a mobile app, a researcher) without changing the monitors.
- **Replay.** If the surgeon says "I want to review what happened between 9:45 and 9:50", Kafka has it. You can replay those 5 minutes as if they were happening again, at normal speed or 10x speed.
- **Fair load.** 6 ORs today. Maybe 10 ORs later. Kafka handles both without choking.

**The simple job:** "Stream every heartbeat, every breath, every pressure reading. Keep a tape of the whole day so nothing is lost."

---

## 3. FLINK — The Live Alert Engine

**What it does:** Watches the stream of readings. Detects problems. Raises alerts.

**Example logic:**
```
IF (SystBP < 90 for 30 seconds straight)
   THEN raise alert "LOW BLOOD PRESSURE"

IF (O2 drops 5 points in 60 seconds)
   THEN raise alert "OXYGEN FALLING"

IF (alert already raised and unacknowledged after 10 minutes)
   THEN escalate alert to charge nurse pager
```

**Why it's needed:**
- **Stateful.** Flink remembers "this patient's baseline O2 is usually 96%". When it sees 91%, it knows to worry. It keeps state across hours.
- **Windowed.** It checks "was SystBP low for the last 30 seconds?" Not a one-off reading, but a trend.
- **Timers.** It knows "this alert was raised at 9:45. Now it's 9:55, and nobody acknowledged it. Ring the escalation bell."
- **Fault-tolerant.** If Flink crashes at 9:46, it restarts and asks Kafka "resume from 9:45:30", and no alerts are missed.

**The simple job:** "Watch the live vitals, notice patterns, and raise alarms when something is wrong."

---

## 4. CASSANDRA — The Time-Series Vitals Archive

**What it stores:** Every single heart rate, pressure, and O2 reading, kept for months.

**Example:**
```
Partition: Patient John, Date 2026-10-25
  9:45:30 → HR 72
  9:45:31 → HR 73
  9:45:32 → HR 74
  ...
```

**Why it's needed:**
- **Write-heavy.** 6 ORs, 6 readings/sec, means 500,000 new readings per day. Traditional databases choke. Cassandra is designed for this.
- **Fast reads of recent data.** When the nurse says "show me the last 30 minutes of Patient John", Cassandra answers in <100ms. It knows exactly where to look.
- **Automatic aging.** Readings older than 90 days are deleted automatically. You don't manage this manually.
- **Distributed.** If you have 2 or 10 Cassandra machines, they all have copies, so if one fails, data is safe.

**The simple job:** "Archive every single reading. Keep it fast and cheap to access the recent stuff."

---

## How They Work Together

```
Real OR Monitor (every second)
         ↓
      KAFKA (tape of readings, ordered, safe)
         ↓
      ┌─────────────────────────┐
      │                         │
      ↓                         ↓
   FLINK                    CASSANDRA
  (Watch for                (Archive all
   problems,                 readings)
   raise alerts)
      ↓
      MONGODB (store alert)
      ↓
   Nurse sees alert on screen → Nurse clicks "Acknowledge"
      ↓
   MONGODB (log acknowledgement, cancel timer)
```

---

## The Splitting (4 members, 4 tools)

| Member | Tool | Their Task |
|---|---|---|
| **Pushkar** | MongoDB | Build the transaction logic (case creation, bed reservation, order entry, alert logging). Make sure two surgeries can't book the same OR. |
| **Member 2** | Kafka | Set up the monitor simulator to pump vitals into Kafka. Ensure ordering per patient. Set up a consumer that writes to Cassandra. |
| **Member 3** | Flink | Write the alert rules (low BP, falling O2, timer-based escalation). Test with scripted scenarios. |
| **Member 4** | Cassandra | Set up the cluster, define the schema (patient + date → readings), handle partitioning and retention. Load test it with 6 ORs of continuous writes. |

---

## What the Screen Shows (Live)

```
┌─ VITALSTREAM ─ OR Command Center ────────────────────────────────┐
│ ACTIVE CASES: 5   ALERTS: 2 UNACKED   BEDS FREE: 2/6 RECOVERY   │
├──────────────────────────────────────────────────────────────────┤
│ OR-1: Case 5421, John, 52y  │ HR 78  BP 118/76  O2 98%  ✓        │
│ OR-2: Case 5422, Sarah, 68y │ HR 85  BP 92/58   O2 94%  ⚠        │
│ OR-3: IDLE                  │                                    │
│ OR-4: Case 5423, Mike, 45y  │ HR 68  BP 125/82  O2 99%  ✓        │
│ OR-5: Case 5424, Emma, 55y  │ HR 92  BP 140/90  O2 96%  ✓        │
│ OR-6: IDLE                  │                                    │
├──────────────────────────────────────────────────────────────────┤
│ ALERTS                                                           │
│ [09:47] Case 5422 (Sarah): LOW BP 92/58 → [ACKNOWLEDGE]         │
│ [09:52] Case 5424 (Emma): HIGH HR 92 → [ACKNOWLEDGE]            │
├──────────────────────────────────────────────────────────────────┤
│ RECOVERY BEDS                        │ UPCOMING ADMISSIONS       │
│ REC-01: Empty                        │ Case 5421 → REC-01 (10m)  │
│ REC-02: Case 5420 (Tom) since 09:10  │ Case 5422 → REC-02 (45m)  │
│ REC-03: Case 5418 (Lisa) since 08:30 │                          │
│ REC-04: Empty                        │                          │
│ REC-05: Case 5419 (Bob) since 08:45  │                          │
│ REC-06: Empty                        │                          │
└──────────────────────────────────────────────────────────────────┘
```

---

## Data: Real + Synthetic Hybrid

- **Real:** Heart rate, BP, O2 readings come from VitalDB surgical cases (6,388 open-source cases).
- **Synthetic:** Patient names, ages, surgeon names, OR assignment, recovery bed assignment, and the scripted "what time do they move beds?"

Everything is labeled "Demo Data — Not Real Patients."

---

## Why This Isn't "Just Excel"

1. **Stream volume:** 6 ORs, 1 reading/sec, 86,400 seconds/day = 518,400 readings/day. Excel stops at 1 million rows (and that's before the second day).
2. **State machines:** Flink keeps sliding windows and timers. Excel doesn't know how to escalate an unacknowledged alert on a timer.
3. **Transactions:** MongoDB makes sure one bed gets one surgery. Excel allows double-booking.
4. **Replayability:** Kill Flink at 9:46, restart at 9:47, nothing lost. Excel has no recovery.
5. **Real data:** The vitals are from real surgical recordings, not synthetic nonsense.
