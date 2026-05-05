# Architecture — Incident Management System (IMS)

## Overview

The Incident Management System (IMS) is designed to handle high-throughput signal ingestion, process events asynchronously, and manage incident lifecycle efficiently.

The system follows a layered architecture with clear separation between ingestion, processing, and storage to ensure scalability and resilience.

---

## High-Level Architecture

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
│ (Source Truth)│ (Cache + TTL) │ (Data Lake)   │
└───────────────┴───────────────┴───────────────┘
```

---

## Core Components

### 1. Frontend Layer

* Built using HTML and JavaScript
* Provides:

  * Incident list view
  * RCA submission
  * Status updates

---

### 2. Backend Layer (FastAPI)

Responsible for:

* Signal ingestion
* Incident lifecycle management
* RCA validation
* Aggregation APIs

Key design choices:

* Async endpoints for non-blocking behavior
* Modular code structure

---

### 3. Ingestion Layer

* Receives signals via `/signals`
* Applies rate limiting
* Uses Redis-based debouncing:

  * Multiple signals within 10 seconds for same component
  * Only one WorkItem is created

---

### 4. Processing Layer

* Uses an in-memory queue (`deque`)
* Signals are pushed immediately to queue
* Background worker processes signals

This decouples ingestion from database operations.

---

### 5. Storage Layer

#### PostgreSQL (Source of Truth)

* Stores WorkItems
* Stores RCA records
* Supports transactional updates

#### Redis (Hot Path)

* Debouncing (TTL-based keys)
* Caching `/incidents`
* Reduces database load

#### Signal Store (Data Lake)

* Stores raw signals in memory
* Acts as an audit log
* Supports querying by incident

---

## Data Flow

1. Signal arrives → `/signals`
2. Redis checks debounce key
3. If new → WorkItem created in database
4. Signal added to queue
5. Background worker processes signal
6. Signal stored in signal_store
7. UI fetches incidents

---

## Key Design Decisions

* Async ingestion for high throughput
* Queue-based buffering for backpressure
* Redis debouncing to reduce duplicates
* Separation of storage layers (data lake, DB, cache)

---

## Limitations

* Signal store is in-memory (not persistent)
* Single worker (no horizontal scaling)
* Basic rate limiting

---

## Future Improvements

* Replace queue with Kafka or RabbitMQ
* Use MongoDB for persistent data lake
* Add monitoring (Prometheus, Grafana)
* Implement distributed rate limiting

---

## Summary

The system demonstrates high-throughput ingestion, backpressure handling, and clean separation of concerns aligned with real-world SRE design principles.
