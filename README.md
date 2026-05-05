# Incident Management System (IMS)

## Overview

The Incident Management System (IMS) is designed to ingest high-volume signals, group them into incidents using debouncing, and manage the incident lifecycle efficiently.

The system focuses on scalability, resilience, and clean system design principles aligned with real-world SRE practices.

---

## Architecture Diagram

```text
Frontend (HTML + JS)
        ↓
FastAPI Backend (Async)
        ↓
┌───────────────────────────────┐
│ Ingestion Layer               │
│ - Async API (/signals)        │
│ - Rate Limiting               │
│ - Redis Debouncing            │
└───────────────────────────────┘
        ↓
┌───────────────────────────────┐
│ Processing Layer              │
│ - In-memory Queue (deque)     │
│ - Background Worker           │
└───────────────────────────────┘
        ↓
┌───────────────┬───────────────┬───────────────┐
│ PostgreSQL    │ Redis         │ Signal Store  │
│ (Source Truth)│ (Cache)       │ (Data Lake)   │
└───────────────┴───────────────┴───────────────┘
```

---

## Features

* Asynchronous signal ingestion using FastAPI
* Redis-based debouncing to prevent duplicate incidents
* Queue-based processing for handling burst traffic
* Incident lifecycle management with RCA validation
* MTTR calculation for incidents
* Aggregation APIs for signal metrics
* Rate limiting to prevent overload
* Observability via throughput logging

---

## Backpressure Handling

The system is designed to handle burst traffic without crashing:

* Signals are received asynchronously via non-blocking API endpoints
* Incoming signals are immediately pushed to an in-memory queue
* A background worker processes signals independently
* Redis debouncing reduces redundant processing

This ensures the system can handle spikes in traffic while maintaining stability.

---

## Tech Stack

* Backend: FastAPI (Python)
* Database: PostgreSQL
* Cache: Redis
* Containerization: Docker & Docker Compose
* Frontend: HTML + JavaScript

---

## Setup Instructions

### Prerequisites

* Docker
* Docker Compose

### Run the Application

```bash
docker-compose up --build
```

### Access

* Backend (API Docs): http://localhost:8000/docs
* Frontend: Open `frontend/index.html` in browser

---

## API Endpoints

* POST `/signals` — Ingest signal
* GET `/incidents` — List incidents
* GET `/incident/{id}/signals` — Get signals for an incident
* POST `/incident/{id}/rca` — Add RCA
* PUT `/incident/{id}/status` — Update incident status
* GET `/metrics/signals-per-component` — Aggregation

---

## Sample Data

Sample data is available in:

```
sample-data/signals.json
```

This can be used to simulate multiple signals for testing debouncing and incident creation.

---

## Project Structure

```
backend/
frontend/
docs/
sample-data/
docker-compose.yml
README.md
```

---

## Design Patterns

* Strategy Pattern: Used to determine alert severity based on component type
* State Pattern: Used to manage incident lifecycle transitions

---

## Limitations

* Signal store is in-memory and not persistent
* Single worker for processing
* Basic rate limiting (not distributed)

---

## Future Improvements

* Replace queue with Kafka or RabbitMQ
* Use MongoDB for persistent signal storage
* Add monitoring (Prometheus, Grafana)
* Improve UI/UX

---
The system was developed incrementally:

1. Basic backend setup with FastAPI, PostgreSQL, and Redis
2. Signal storage and debouncing with incident linking
3. Incident lifecycle management with RCA validation and MTTR
4. Lightweight frontend for interaction
5. Dockerization for full system orchestration

Detailed steps are documented in the /docs folder.

## Repository

https://github.com/JayaPrakashEdala/ims-system
