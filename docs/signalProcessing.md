# 🧱 Step 2 — Signal Storage & Incident Linking

## 📌 Objective

Enhance the system to:

* Store **all incoming signals**
* Link signals to a corresponding **incident**
* Maintain **debouncing** without losing data

---

## 🚨 Problem in Step 1

In the initial implementation:

* Duplicate signals within 10 seconds were **ignored**
* This caused **data loss**
* System did not reflect real-world monitoring behavior

---

## ✅ Solution (Step 2)

We updated the system to:

* Store **every signal**
* Link multiple signals to a **single incident**
* Continue using Redis for debouncing

---

## 🧠 Design Decision

Instead of installing MongoDB (time constraints), we used:

👉 **In-memory signal store (Python list)**

This simulates a NoSQL database for storing raw signals.

---

## 🛠️ Implementation Steps

---

### 🔹 Step 2.1 — Create Signal Store

In:

```bash
backend/app/main.py
```

Add:

```python
signal_store = []
```

---

### 🔹 Step 2.2 — Modify Signal Ingestion Logic

Update the `/signals` endpoint to:

* Check Redis for existing incident
* Attach signals if within debounce window
* Create new incident otherwise

---

### 🔹 Updated `/signals` Endpoint

```python
from datetime import datetime

signal_store = []

@app.post("/signals")
def ingest_signal(signal: schemas.Signal, db: Session = Depends(get_db)):

    key = f"debounce:{signal.component_id}"
    existing = redis_client.get(key)

    # 🔁 Existing incident (debounced window)
    if existing:
        incident_id = int(existing)

        signal_store.append({
            "component_id": signal.component_id,
            "severity": signal.severity,
            "incident_id": incident_id,
            "timestamp": datetime.utcnow()
        })

        return {
            "message": "Signal attached to existing incident",
            "incident_id": incident_id
        }

    # 🆕 New incident
    work_item = models.WorkItem(
        component_id=signal.component_id,
        severity=signal.severity
    )

    db.add(work_item)
    db.commit()
    db.refresh(work_item)

    # Store incident_id in Redis with TTL
    redis_client.set(key, work_item.id, ex=10)

    # Store first signal
    signal_store.append({
        "component_id": signal.component_id,
        "severity": signal.severity,
        "incident_id": work_item.id,
        "timestamp": datetime.utcnow()
    })

    return {
        "message": "New incident created",
        "incident_id": work_item.id
    }
```

---

## 🔁 Updated Signal Flow

```text
Signal → Redis Check → 
    ├── Existing Incident → Attach Signal
    └── New Incident → Create + Store Signal
```

---

## 🧪 Testing

### Request Body

```json
{
  "component_id": "CACHE_CLUSTER_01",
  "severity": "HIGH"
}
```

---

### Expected Behavior

| Request                | Result                           |
| ---------------------- | -------------------------------- |
| First                  | New incident created             |
| Second (within 10 sec) | Signal attached to same incident |
| After 10 sec           | New incident created             |

---

## 📊 Example Stored Signals

```json
[
  {
    "component_id": "CACHE_CLUSTER_01",
    "incident_id": 1,
    "severity": "HIGH",
    "timestamp": "2026-05-01T10:00:00"
  },
  {
    "component_id": "CACHE_CLUSTER_01",
    "incident_id": 1,
    "severity": "HIGH",
    "timestamp": "2026-05-01T10:00:02"
  }
]
```

---

## ⚠️ Limitations

* Signals are stored in memory (lost on restart)
* Not scalable for production
* No persistent NoSQL storage

---

## 🚀 Future Improvements

* Replace in-memory store with **MongoDB**
* Add query support for signals
* Implement signal aggregation

---

## 🧠 SRE Thinking

This approach ensures:

* No signal data loss
* Efficient incident grouping
* Reduced alert noise
* High-throughput handling

---

## 💬 Explanation (Interview Ready)

> “I implemented Redis-based debouncing while ensuring no signal loss by storing all incoming signals and linking them to a single incident. Due to time constraints, I simulated a NoSQL store using an in-memory structure, which can be replaced with MongoDB in production.”

---
