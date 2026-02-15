# 🧠 Pooling Algorithm Explained

## Overview
The Smart Airport Ride Pooling system uses a **Greedy Spatio-Temporal Heuristic** to group riders. This approach was chosen for its balance between computational efficiency and high match rates in high-concurrency environments.

## How Grouping Works
1.  **Request Arrival**: When a request arrives, it is placed in a `PENDING` state.
2.  **Batch Processing**: The `PoolingEngine` retrieves a batch of pending requests ordered by their arrival time (`created_at`).
3.  **Active Pool Check**: For each request, the engine searches for existing `Active Pools` within a defined **Pickup Radius** (default 3km).
4.  **Constraint Validation**:
    *   **Capacity**: Current seats + Requested seats $\leq$ Cab Capacity.
    *   **Luggage**: Current luggage + Requested luggage $\leq$ Cab Luggage limit.
    *   **Detour**: The distance to the new pickup must not exceed a heuristic threshold based on the user's `detour_tolerance_minutes`.
5.  **New Pool Creation**: If no existing pool is suitable, the system finds the nearest available `Cab` and initializes a new pool.

## Why Greedy?
*   **Latency**: Real-time ride-sharing requires sub-second response times. An optimal Global Optimization (like solving the VRP - Vehicle Routing Problem) is NP-Hard and takes too long for real-time APIs.
*   **Scale**: Greedy algorithms permit O(N) or O(N log N) scaling, making them suitable for thousands of concurrent users.
*   **Incremental Updates**: New riders can join existing routes without recalculating the entire city's schedule.

## Detour Calculation
The engine uses the **Haversine formula** to calculate Great Circle distances. 
*   **Heuristic**: Detour is estimated as the extra distance the cab must travel to reach the new pickup point.
*   **Threshold**: $max\_detour\_km = tolerance\_minutes \times speed\_factor$.

## Complexity Analysis
*   **Time Complexity**: $O(R \times (P + C))$
    *   $R$: Pending Requests
    *   $P$: Active Pools
    *   $C$: Available Cabs
*   **Space Complexity**: $O(N)$ where $N$ is the total number of objects in the database.

## Scalability to 10k Users
To handle 10k users, the following patterns are implemented:
1.  **Asynchronous Processing**: Heavy math is moved to Celery workers.
2.  **Indexing**: Database indexes on `status`, `pickup_lat`, and `pickup_lng`.
3.  **Distributed Locking**: Redis locks ensure that two workers don't assign the same cab to different riders simultaneously.
4.  **Database WAL**: SQLite's Write-Ahead Logging allows concurrent reads/writes for higher throughput.
