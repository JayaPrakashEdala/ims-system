# Prompts and Development Notes

## Overview

This document captures the design thinking, prompts, and decisions that guided the development of the Incident Management System (IMS).

The goal was to build a system that can handle high-throughput signal ingestion, ensure resilience under load, and follow clean system design principles.

---

## Initial Problem Understanding

**Prompt:**
Design a system to ingest high-volume error signals and create incidents while avoiding duplication.

**Decision:**

* Use FastAPI for asynchronous request handling
* Use Redis to implement debouncing logic
* Use PostgreSQL as the source of truth for structured data

---

## Handling High Throughput

**Prompt:**
How to handle bursts of incoming signals without overwhelming the database?

**Decision:**

* Introduce an in-memory queue (deque)
* Push incoming signals to the queue immediately
* Process signals asynchronously using a background worker

This ensures that ingestion is non-blocking and resilient under load.

---

## Debouncing Logic

**Prompt:**
Prevent multiple incidents being created for the same component within a short time window.

**Decision:**

* Use Redis keys with TTL (10 seconds)
* If a key exists, reuse the same incident
* Otherwise, create a new WorkItem

---

## Backpressure Strategy

**Prompt:**
How to prevent system failure when signal rate exceeds processing capacity?

**Decision:**

* Decouple ingestion from persistence using a queue
* Use asynchronous endpoints
* Process signals in the background

This allows the system to handle spikes without crashing.

---

## Storage Design

**Prompt:**
How to separate different types of data efficiently?

**Decision:**

* Raw signals → stored in in-memory signal store (data lake concept)
* WorkItems and RCA → stored in PostgreSQL (transactional system)
* Cache → handled using Redis

---

## Design Patterns

**Prompt:**
How to make the system flexible and extensible?

**Decision:**

### Strategy Pattern

* Used to determine alert severity based on component type
* Example:

  * RDBMS → P0
  * Cache → P2

### State Pattern

* Used to manage incident lifecycle:

  * OPEN → INVESTIGATING → RESOLVED → CLOSED

---

## Observability

**Prompt:**
How to monitor system behavior?

**Decision:**

* Implement `/health` endpoint
* Log throughput (signals processed per second) every 5 seconds

---

## Resilience

**Prompt:**
How to prevent cascading failures?

**Decision:**

* Implement rate limiting on the ingestion API
* Use debouncing to reduce duplicate signals
* Use queue to absorb traffic spikes

---

## Frontend Decisions

**Prompt:**
How to build a UI without spending too much time on frontend complexity?

**Decision:**

* Use simple HTML and JavaScript
* Focus on API integration rather than UI styling

---

## Trade-offs

* Used in-memory signal store instead of persistent NoSQL for simplicity
* Implemented basic rate limiting instead of distributed rate limiting
* Used single worker instead of scalable queue system

---

## Summary

The development process focused on:

* Clear separation of system responsibilities
* Handling high-throughput ingestion safely
* Applying appropriate design patterns
* Balancing simplicity with correctness
