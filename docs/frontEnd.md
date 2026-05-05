# 🧱 Step 4 — Frontend Dashboard (Incident UI)

## 📌 Objective

Build a simple frontend dashboard to:

* View all incidents
* Inspect incident details
* Submit RCA (Root Cause Analysis)
* Close incidents (with validation)

---

## 🎯 Design Approach

To save time and focus on backend logic, we implemented a:

👉 **Lightweight frontend using HTML + JavaScript (Vanilla JS)**

This avoids unnecessary complexity while still fulfilling all functional requirements.

---

## 🧱 Features Implemented

### ✅ Incident List

* Displays all incidents
* Shows:

  * Incident ID
  * Component ID
  * Status
* Allows viewing details

---

### ✅ Incident Details

* Displays selected incident information
* Includes:

  * ID
  * Component
  * Status

---

### ✅ RCA Submission

* Input fields for:

  * Root Cause
  * Fix
* Sends data to backend API

---

### ✅ Close Incident

* Allows closing an incident using ID
* Backend enforces:

  * ❌ Cannot close without RCA
  * ✔ Valid lifecycle transition

---

## 📂 File Structure

```id="r7d1v5"
frontend/
└── index.html
```

---

## 🛠️ Implementation Steps

---

### 🔹 Step 4.1 — Create Frontend File

```bash id="3h9xgp"
mkdir frontend
cd frontend
touch index.html
```

---

### 🔹 Step 4.2 — Add UI Code

The `index.html` file includes:

* Basic HTML layout
* JavaScript functions for API calls
* Integration with backend endpoints

---

### 🔹 API Integration

Frontend communicates with backend using:

```text id="jz7rci"
http://127.0.0.1:8000
```

---

### 🔹 Key Functions

| Function         | Purpose                         |
| ---------------- | ------------------------------- |
| loadIncidents()  | Fetch and display all incidents |
| viewIncident(id) | Show incident details           |
| addRCA()         | Submit RCA data                 |
| closeIncident()  | Close incident via API          |

---

## ▶️ Running the Frontend

Simply open:

```bash id="0m6k6s"
frontend/index.html
```

In a browser.

---

## ⚠️ CORS Configuration (Important)

Since frontend and backend run separately, enable CORS in backend:

📂 File:

```bash id="j3h4s0"
backend/app/main.py
```

Add:

```python id="lw8t5g"
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🧪 Testing Workflow

---

### 🔹 1. Load Incidents

Click:

```text id="0t7ozt"
Refresh Incidents
```

---

### 🔹 2. View Details

Click:

```text id="q9f6gj"
View
```

---

### 🔹 3. Add RCA

Enter:

* Incident ID
* Root Cause
* Fix

Click:

```text id="1ch2r4"
Submit RCA
```

---

### 🔹 4. Close Incident

Enter Incident ID and click:

```text id="x2sl9h"
Close
```

---

### Expected Behavior

| Action            | Result           |
| ----------------- | ---------------- |
| Close without RCA | ❌ Error          |
| Close after RCA   | ✔ Success        |
| View incidents    | ✔ Data displayed |

---

## 🧠 Design Decisions

* Used **Vanilla JavaScript** for simplicity
* Focused on **functionality over UI design**
* Avoided heavy frameworks (React, Angular) to save time
* Ensured clear interaction with backend APIs

---

## ⚠️ Limitations

* Minimal UI (no styling)
* No pagination or filtering
* No real-time updates
* Manual refresh required

---

## 🚀 Future Improvements

* Replace with React-based UI
* Add real-time updates (WebSockets)
* Add filtering & search
* Improve UX design

---

## 🧠 SRE Thinking

This dashboard enables:

* Monitoring active incidents
* Performing RCA
* Managing incident lifecycle

It simulates a basic **incident response system** used in production environments.

---

## 💬 Interview Explanation

> “I implemented a lightweight frontend using vanilla JavaScript to interact with backend APIs for incident monitoring, RCA submission, and lifecycle management. The focus was on functionality and integration rather than UI complexity.”

---
