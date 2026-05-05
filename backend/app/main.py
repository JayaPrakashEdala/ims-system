from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app import models, schemas
from app.redis_client import redis_client
from datetime import datetime
from collections import deque
import asyncio
import json
from app.alerting import get_alert_strategy

# =========================
# GLOBALS
# =========================
signal_queue = deque()
signal_store = []
rate_limit = {}
counter = 0

Base.metadata.create_all(bind=engine)

app = FastAPI()

# =========================
# CORS
# =========================
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# DB DEPENDENCY
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# BASIC ROUTES
# =========================
@app.get("/")
def root():
    return {"message": "IMS Backend Running"}

@app.get("/health")
def health():
    return {"status": "ok"}

# =========================
# SIGNAL INGESTION (ASYNC + RATE LIMIT + DEBOUNCE)
# =========================
@app.post("/signals")
async def ingest_signal(signal: schemas.Signal, db: Session = Depends(get_db)):
    global counter

    # 🔥 Rate Limiting
    ip = "global"
    rate_limit[ip] = rate_limit.get(ip, 0) + 1
    if rate_limit[ip] > 100:
        raise HTTPException(status_code=429, detail="Too many requests")

    key = f"debounce:{signal.component_id}"
    existing = redis_client.get(key)

    # Strategy Pattern
    strategy = get_alert_strategy(signal.component_id)
    severity = strategy.get_severity()

    # CASE 1: Existing incident
    if existing:
        incident_id = int(existing)

        signal_queue.append({
            "component_id": signal.component_id,
            "severity": severity,
            "incident_id": incident_id
        })

        return {
            "message": "Signal queued (attached to existing incident)",
            "incident_id": incident_id
        }

    # CASE 2: New incident
    work_item = models.WorkItem(
        component_id=signal.component_id,
        severity=severity
    )

    db.add(work_item)
    db.commit()
    db.refresh(work_item)

    redis_client.set(key, work_item.id, ex=10)

    signal_queue.append({
        "component_id": signal.component_id,
        "severity": severity,
        "incident_id": work_item.id
    })

    return {
        "message": "New incident created (signal queued)",
        "incident_id": work_item.id
    }

# =========================
# BACKGROUND WORKER (QUEUE PROCESSING)
# =========================
async def process_queue():
    global counter

    while True:
        if signal_queue:
            signal = signal_queue.popleft()

            signal_store.append({
                "component_id": signal["component_id"],
                "severity": signal["severity"],
                "incident_id": signal["incident_id"],
                "timestamp": datetime.utcnow()
            })

            counter += 1

        await asyncio.sleep(0.05)

# =========================
# OBSERVABILITY (THROUGHPUT)
# =========================
async def log_metrics():
    global counter
    while True:
        print(f"🚀 Signals/sec: {counter}")
        counter = 0
        await asyncio.sleep(5)

# =========================
# INCIDENT STATUS (STATE + RCA VALIDATION)
# =========================
@app.put("/incident/{id}/status")
def update_status(id: int, status: str, db: Session = Depends(get_db)):

    work_item = db.query(models.WorkItem).filter(models.WorkItem.id == id).first()

    if not work_item:
        raise HTTPException(status_code=404, detail="Incident not found")

    # State transitions
    valid_transitions = {
        "OPEN": "INVESTIGATING",
        "INVESTIGATING": "RESOLVED",
        "RESOLVED": "CLOSED"
    }

    # Enforce RCA before closing
    if status == "CLOSED":
        rca = db.query(models.RCA).filter(models.RCA.work_item_id == id).first()
        if not rca:
            raise HTTPException(status_code=400, detail="RCA required before closing")

        work_item.closed_at = datetime.utcnow()
        mttr = (work_item.closed_at - work_item.created_at).total_seconds()
        work_item.mttr = mttr

    work_item.status = status
    db.commit()

    return {
        "message": "Status updated",
        "status": work_item.status,
        "mttr": work_item.mttr
    }

# =========================
# RCA
# =========================
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

# =========================
# INCIDENTS (WITH REDIS CACHE + SORT)
# =========================
@app.get("/incidents")
def get_incidents(db: Session = Depends(get_db)):

    cached = redis_client.get("incidents")
    if cached:
        return json.loads(cached)

    incidents = db.query(models.WorkItem).all()

    # Sort by severity priority
    severity_order = {"P0": 1, "P1": 2, "P2": 3, "P3": 4}
    incidents = sorted(incidents, key=lambda x: severity_order.get(x.severity, 5))

    data = [
        {
            "id": i.id,
            "component_id": i.component_id,
            "severity": i.severity,
            "status": i.status
        }
        for i in incidents
    ]

    redis_client.set("incidents", json.dumps(data), ex=5)

    return data

# =========================
# SIGNAL APIs (DATA LAKE)
# =========================
@app.get("/signals")
def get_signals():
    return signal_store

@app.get("/incident/{id}/signals")
def get_signals_by_incident(id: int):
    return [s for s in signal_store if s["incident_id"] == id]

# =========================
# AGGREGATION
# =========================
@app.get("/metrics/signals-per-component")
def signals_per_component():
    result = {}
    for s in signal_store:
        comp = s["component_id"]
        result[comp] = result.get(comp, 0) + 1
    return result

# =========================
# STARTUP
# =========================
@app.on_event("startup")
async def start_workers():
    asyncio.create_task(process_queue())
    asyncio.create_task(log_metrics())