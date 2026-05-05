# 🚀 Incident Management System (IMS) — Backend Setup Guide

## 📌 Overview

This document describes the initial setup of the backend for the Incident Management System (IMS).

The goal of this step is to build a **working backend service** with:

* FastAPI server
* PostgreSQL database integration
* Redis for caching and debouncing
* Basic incident ingestion API

---

## 🧱 Step 0 — System Understanding

The system processes incoming signals and creates incidents.

### Flow:

```
Signal → Debounce → Incident → RCA → Close
```

---

## 📁 Step 1 — Project Setup

Create the root project directory:

```bash
mkdir ims-system
cd ims-system
```

---

## 📂 Step 2 — Folder Structure

Create required folders:

```bash
mkdir backend frontend docs sample-data
```

Navigate to backend:

```bash
cd backend
```

---

## 🧠 Step 3 — Backend Structure

Create application structure:

```bash
mkdir app

touch app/main.py
touch app/models.py
touch app/database.py
touch app/schemas.py
touch app/config.py
touch app/redis_client.py

touch requirements.txt
```

---

## 📦 Step 4 — Install Dependencies

Add the following to `requirements.txt`:

```txt
fastapi
uvicorn
sqlalchemy
psycopg2-binary
pydantic
redis
motor
python-dotenv
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Step 5 — Configuration

Create `app/config.py`:

```python
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ims_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
```

---

## 🗄️ Step 6 — Database Setup (PostgreSQL)

Create `app/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
```

---

## 🧱 Step 7 — Data Models

Create `app/models.py`:

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class WorkItem(Base):
    __tablename__ = "work_items"

    id = Column(Integer, primary_key=True, index=True)
    component_id = Column(String)
    severity = Column(String)
    status = Column(String, default="OPEN")
    created_at = Column(DateTime, default=func.now())
    closed_at = Column(DateTime, nullable=True)


class RCA(Base):
    __tablename__ = "rca"

    id = Column(Integer, primary_key=True, index=True)
    work_item_id = Column(Integer, ForeignKey("work_items.id"))
    root_cause = Column(String)
    fix = Column(String)
    created_at = Column(DateTime, default=func.now())
```

---

## 🧾 Step 8 — API Schemas

Create `app/schemas.py`:

```python
from pydantic import BaseModel

class Signal(BaseModel):
    component_id: str
    severity: str


class RCARequest(BaseModel):
    root_cause: str
    fix: str
```

---

## 🔴 Step 9 — Redis Setup

Create `app/redis_client.py`:

```python
import redis
from app.config import REDIS_URL

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
```

---

## 🌐 Step 10 — FastAPI Application

Create `app/main.py`:

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app import models, schemas
from app.redis_client import redis_client

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/signals")
def ingest_signal(signal: schemas.Signal, db: Session = Depends(get_db)):

    key = f"debounce:{signal.component_id}"

    # Debounce logic
    if redis_client.exists(key):
        return {"message": "Signal grouped (debounced)"}

    redis_client.setex(key, 10, "1")

    work_item = models.WorkItem(
        component_id=signal.component_id,
        severity=signal.severity
    )

    db.add(work_item)
    db.commit()
    db.refresh(work_item)

    return {"message": "New incident created", "id": work_item.id}


@app.get("/incidents")
def get_incidents(db: Session = Depends(get_db)):
    return db.query(models.WorkItem).all()


@app.post("/incident/{id}/rca")
def add_rca(id: int, rca: schemas.RCARequest, db: Session = Depends(get_db)):
    work_item = db.query(models.WorkItem).filter(models.WorkItem.id == id).first()

    if not work_item:
        raise HTTPException(status_code=404, detail="Not found")

    new_rca = models.RCA(
        work_item_id=id,
        root_cause=rca.root_cause,
        fix=rca.fix
    )

    db.add(new_rca)
    work_item.status = "CLOSED"

    db.commit()

    return {"message": "RCA added and incident closed"}
```

---

## ▶️ Step 11 — Run the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Access API documentation:

```
http://localhost:8000/docs
```

---

## 🧪 Step 12 — Testing

Send a test signal:

```json
{
  "component_id": "CACHE_CLUSTER_01",
  "severity": "HIGH"
}
```

### Expected Behavior:

* First request → Creates new incident
* Second request (within 10 seconds) → Debounced

---

## ✅ Checkpoint

Ensure the following are working:

* [ ] FastAPI server runs successfully
* [ ] `/health` endpoint returns status
* [ ] `/signals` endpoint creates incidents
* [ ] Redis debouncing works
* [ ] `/incidents` returns stored data

---

## 📌 Next Steps

* Implement proper signal storage (MongoDB)
* Add incident state transitions
* Enforce mandatory RCA before closing
* Implement MTTR calculation
* Add rate limiting and observability

---
