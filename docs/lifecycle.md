# 🧱 Step 3 — Incident Lifecycle, RCA Validation & MTTR

## 📌 Objective

Enhance the Incident Management System to:

* Implement a **structured incident lifecycle**
* Enforce **mandatory RCA before closing**
* Automatically calculate **MTTR (Mean Time To Repair)**

---

## 🚨 Problem Before Step 3

Previously:

* Incidents were directly closed when RCA was added
* No proper lifecycle management
* No validation rules
* No MTTR calculation

---

## ✅ Solution (Step 3)

We introduced:

* Defined incident lifecycle states
* Separation of RCA and status updates
* Validation rule to block closing without RCA
* Automatic MTTR calculation on closure

---

## 🧠 Incident Lifecycle Design

```text
OPEN → INVESTIGATING → RESOLVED → CLOSED
```

---

## 🛠️ Implementation Steps

---

### 🔹 Step 3.1 — Add MTTR Field

📂 File:

```bash
backend/app/models.py
```

Add `mttr` column:

```python
from sqlalchemy import Float

mttr = Column(Float, nullable=True)
```

---

### 🔹 Step 3.2 — Update Database

Since schema changed:

* Drop old tables OR recreate database
* Restart application

---

### 🔹 Step 3.3 — Separate RCA from Closure

📂 File:

```bash
backend/app/main.py
```

---

### ✔ Updated RCA Endpoint

```python
@app.post("/incident/{id}/rca")
def add_rca(id: int, rca: schemas.RCARequest, db: Session = Depends(get_db)):

    work_item = db.query(models.WorkItem).filter(models.WorkItem.id == id).first()

    if not work_item:
        raise HTTPException(status_code=404, detail="Incident not found")

    new_rca = models.RCA(
        work_item_id=id,
        root_cause=rca.root_cause,
        fix=rca.fix
    )

    db.add(new_rca)
    db.commit()

    return {"message": "RCA added successfully"}
```

---

### 🔹 Step 3.4 — Add Status Update API

```python
@app.put("/incident/{id}/status")
def update_status(id: int, status: str, db: Session = Depends(get_db)):

    work_item = db.query(models.WorkItem).filter(models.WorkItem.id == id).first()

    if not work_item:
        raise HTTPException(status_code=404, detail="Incident not found")

    # ❗ Enforce RCA before closing
    if status == "CLOSED":
        rca = db.query(models.RCA).filter(models.RCA.work_item_id == id).first()
        if not rca:
            raise HTTPException(status_code=400, detail="RCA required before closing")

        work_item.closed_at = datetime.utcnow()

        # MTTR Calculation
        mttr = (work_item.closed_at - work_item.created_at).total_seconds()
        work_item.mttr = mttr

    work_item.status = status
    db.commit()

    return {
        "message": "Status updated",
        "status": work_item.status,
        "mttr": work_item.mttr
    }
```

---

## 🔁 Updated Workflow

```text
Signal → Incident Created (OPEN)
        ↓
Add RCA (no status change)
        ↓
Update Status → CLOSED (only if RCA exists)
        ↓
MTTR calculated automatically
```

---

## 🧪 Testing

---

### 🔹 1. Create Incident

```http
POST /signals
```

---

### 🔹 2. Try Closing Without RCA (Should Fail)

```http
PUT /incident/1/status?status=CLOSED
```

Expected:

```json
{
  "detail": "RCA required before closing"
}
```

---

### 🔹 3. Add RCA

```http
POST /incident/1/rca
```

```json
{
  "root_cause": "Database overload",
  "fix": "Scaled resources"
}
```

---

### 🔹 4. Close Incident

```http
PUT /incident/1/status?status=CLOSED
```

Expected:

```json
{
  "message": "Status updated",
  "status": "CLOSED",
  "mttr": 120.5
}
```

---

## 📊 MTTR Calculation

```text
MTTR = closed_at - created_at
```

* Automatically calculated in seconds
* Stored in database

---

## ⚠️ Validation Rule

```text
❌ Incident cannot be CLOSED without RCA
```

This ensures:

* Proper root cause documentation
* Accurate incident tracking
* Real-world SRE workflow compliance

---

## 🧠 SRE Design Thinking

* Separation of concerns:

  * RCA storage vs incident lifecycle
* Enforced operational discipline
* Automated metrics (MTTR)
* Prevents premature closure of incidents

---

## 🚀 Outcome

After Step 3, the system supports:

* Structured incident lifecycle
* Mandatory RCA validation
* Automated MTTR calculation
* Production-like incident workflow

---

## 💬 Interview Explanation

> “I implemented a state-based incident lifecycle with strict validation rules, ensuring incidents cannot be closed without RCA, and automatically calculated MTTR based on lifecycle timestamps.”

---
