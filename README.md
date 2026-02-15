# 🚕 Smart Airport Ride Pooling (Backend Submission)

A production-grade, concurrency-safe backend engine for real-time ride-pooling. Built with **Django**, **Celery**, and **Redis**, this project optimizes airport transfers by intelligently grouping passengers while respecting seat/luggage constraints and detour tolerances.

## 🌟 1-Minute Summary
- **The Problem**: High traffic airport routes are inefficient when cabs are under-filled.
- **The Solution**: An event-driven engine that matches pending requests to active pools or available cabs in sub-second time.
- **Tech Highlights**: Distributed locking (Redis), asynchronous optimization (Celery), and greedy heuristics (O(N) matching).

## 🚀 Quick Start (Production Setup)

### 1. Requirements
- Python 3.11+
- Redis (Broker)

### 2. Installations
```bash
pip install -r requirements.txt
python manage.py migrate
```

### 3. Run Services
```bash
# Terminal 1: API
python manage.py runserver

# Terminal 2: Background Engine
celery -A config worker --loglevel=info -P solo
```

### 4. Run Stress Test (The Demo)
```bash
# This command generates 800+ requests and pools them in < 5 seconds
python manage.py simulate_requests
```

## 🧠 Core Algorithm: How Pooling Works
1.  **Request Reception**: Ride request is saved as `PENDING`.
2.  **Matching (Greedy)**: Background worker searches for active pools within a 3km radius.
3.  **Constraint Engines**:
    *   **Capacity**: Checks for seat and luggage overflow.
    *   **Detour**: Evaluates if the new pickup violates existing passengers' time tolerances.
4.  **Route Recalculation**: Once matched, the `RouteOptimizer` uses a Nearest Neighbor heuristic to update the drop sequence.

## 🔒 Concurrency & Safety
- **Race Condition Prevention**: Uses **Redis Distributed Locks** to prevent two workers from modifying the same pool simultaneously.
- **DB Integrity**: Uses `select_for_update` to lock database rows during critical matching logic.
- **Atomicity**: All status transitions are wrapped in Django `transaction.atomic()`.

## 🧪 Documentation & Testing
- **Swagger Documentation**: Accessible at `/swagger/`
- **Interactive Dashboard**: Accessible at `/api/core/dashboard/` (Cream themed portal)
- **Stats Endpoint**: `GET /api/debug/stats/` for real-time system monitoring.

## 📈 Scalability Plan
This architecture is designed to scale to **100k+ users** by:
1.  Deploying Celery workers across multiple nodes.
2.  Transitioning from SQLite to PostgreSQL RDS.
3.  Implementing Redis Geospatial for $O(1)$ cab discovery.

---
**Author**: Antigravity (Senior Backend Engineer)
**Stack**: Django REST Framework, Celery, Redis, SQLite, Docker.
