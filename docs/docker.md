# 🧱 Step 5 — Dockerization & Service Orchestration

## 📌 Objective

Containerize the entire system to ensure:

* Easy setup and execution
* Environment consistency
* One-command startup using Docker Compose

---

## 🎯 Goal

Run the complete system using:

```bash
docker-compose up --build
```

---

## 🧱 Architecture Overview

```text
User → FastAPI Backend → PostgreSQL
                         → Redis
```

* **Backend** → FastAPI application
* **PostgreSQL** → Stores incidents & RCA
* **Redis** → Handles debouncing & caching

---

## 📂 Project Structure

```text
ims-system/
│
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   └── index.html
│
└── docker-compose.yml
```

---

## 🛠️ Implementation Steps

---

### 🔹 Step 5.1 — Create Backend Dockerfile

📂 File:

```bash
backend/Dockerfile
```

Add:

```dockerfile
FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### 🔹 Step 5.2 — Create docker-compose.yml

📂 File:

```bash
docker-compose.yml
```

Add:

```yaml
version: "3.8"

services:

  backend:
    build: ./backend
    container_name: ims_backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/ims_db
      REDIS_URL: redis://redis:6379

  postgres:
    image: postgres:15
    container_name: ims_postgres
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: ims_db
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    container_name: ims_redis
    ports:
      - "6379:6379"
```

---

### 🔹 Step 5.3 — Update Configuration

📂 File:

```bash
backend/app/config.py
```

Update to use environment variables:

```python
import os

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
```

---

### 🔹 Step 5.4 — Update Dependencies

📂 File:

```bash
backend/requirements.txt
```

Ensure required packages:

```text
fastapi
uvicorn
sqlalchemy
psycopg2-binary
pydantic
redis
python-dotenv
```

---

### 🔹 Step 5.5 — Run the System

From root directory:

```bash
docker-compose up --build
```

---

## ▶️ Access Application

Once containers are running:

```text
http://localhost:8000/docs
```

---

## 🧪 Testing

Verify:

* `/health` endpoint works
* `/signals` creates incidents
* `/incidents` returns data
* Debouncing logic works

---

## ⚠️ Common Issues & Fixes

---

### ❌ Port Already in Use

```bash
sudo lsof -i :5432
sudo kill -9 <PID>
```

---

### ❌ Database Not Ready

* Wait a few seconds after startup
* PostgreSQL container needs time to initialize

---

### ❌ Dependency Errors

Rebuild containers:

```bash
docker-compose up --build
```

---

## 🧠 Design Decisions

* Used **Docker Compose** for multi-service orchestration
* Environment variables used for configuration
* Services are decoupled and independently scalable

---

## 🚀 Benefits

* One-command setup
* Consistent development environment
* Easy deployment
* Simplified testing

---

## ⚠️ Limitations

* No persistent volumes (data lost on container removal)
* No production-grade scaling yet

---

## 🔮 Future Improvements

* Add volumes for data persistence
* Add Nginx for routing
* Add monitoring (Prometheus, Grafana)

---

## 🧠 SRE Thinking

This setup simulates a real-world system where:

* Services are containerized
* Dependencies are managed independently
* System can be easily deployed and scaled

---

## 💬 Interview Explanation

> “I containerized the application using Docker and orchestrated services with Docker Compose, enabling a reproducible environment where backend, PostgreSQL, and Redis run together with a single command.”

---
