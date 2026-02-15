# ⚡ Performance & Scalability Notes

## 🛠️ The Choice of SQLite
- **Why it's okay locally**: SQLite is a serverless, single-file database. With **Write-Ahead Logging (WAL)** enabled, it supports multiple concurrent readers and handles the load of an interview-scale demo perfectly without extra infra.
- **Production Transition**: For a real production environment, switching to **PostgreSQL** is as simple as changing the `DATABASES` setting. Django's ORM abstracts the specific SQL differences.

## 🚀 Scaling Strategy

### 1. Database Optimization
- **Indexing**: Composite indexes on `(pickup_lat, pickup_lng)` and `(status)` ensure spatial queries remain $O(log N)$.
- **Partitioning**: As the `RideRequest` table grows to millions, we would partition by `created_at` (Monthly/Weekly).

### 2. Horizontal Scaling
- **Stateless App Servers**: The Django application is stateless, allowing multiple pods behind a Load Balancer.
- **Worker Pools**: Add more Celery workers across multiple nodes to handle spikes in ride requests.
- **Redis Cluster**: For massive scale, Redis itself can be clustered to handle millions of locks/tasks.

### 3. Caching & Latency
- **Real-time Geo-Indexing**: For global scale, we would integrate **Redis Geospatial (GeoSets)** to find nearby cabs in $O(1)$ time, bypassing the initial SQL spatial check.
- **Expected Latency**: 
  - API response: < 50ms
  - Pooling completion: < 200ms

## 🏗️ Deployment Plan
- **Containerization**: Use the provided `Dockerfile` and `docker-compose.yml`.
- **Orchestration**: Kubernetes for managing auto-scaling workers.
- **Monitoring**: Prometheus + Grafana for tracking pool match rates and worker latency.
