import asyncio
import aiohttp
import time
import random
import logging
import statistics
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "http://localhost:8000/api/rides/request-ride/"
TOTAL_REQUESTS = 10000
CONCURRENCY_LIMIT = 100  # Target requests per second
TIMEOUT_SECONDS = 30

# Mock Data Generation
def generate_ride_data():
    # Bangalore coordinates approx
    lat_base, lng_base = 12.9716, 77.5946
    return {
        "user_id": random.randint(1, 100),  # Assumes some users exist
        "pickup_lat": lat_base + random.uniform(-0.1, 0.1),
        "pickup_lng": lng_base + random.uniform(-0.1, 0.1),
        "drop_lat": lat_base + 0.2 + random.uniform(-0.05, 0.05),
        "drop_lng": lng_base + 0.2 + random.uniform(-0.05, 0.05),
        "seats_required": random.randint(1, 3),
        "luggage_units": random.randint(0, 2),
        "detour_tolerance_minutes": random.choice([15, 20, 30])
    }

async def send_request(session, request_id, latencies):
    data = generate_ride_data()
    start_time = time.perf_counter()
    try:
        async with session.post(BASE_URL, json=data, timeout=TIMEOUT_SECONDS) as response:
            end_time = time.perf_counter()
            latency = (end_time - start_time) * 1000 # to ms
            
            if response.status == 201:
                latencies.append(latency)
                if request_id % 500 == 0:
                    logger.info(f"Progress: {request_id}/{TOTAL_REQUESTS} requests sent. Current Latency: {latency:.2f}ms")
            else:
                resp_text = await response.text()
                logger.error(f"Request {request_id} failed with status {response.status}: {resp_text}")
    except Exception as e:
        logger.error(f"Request {request_id} encountered an error: {e}")

async def run_simulation():
    latencies = []
    logger.info(f"Starting simulation: {TOTAL_REQUESTS} total requests at ~{CONCURRENCY_LIMIT} RPS")
    
    start_sim = time.perf_counter()
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(1, TOTAL_REQUESTS + 1):
            tasks.append(send_request(session, i, latencies))
            
            # Simple rate limiting logic
            if i % CONCURRENCY_LIMIT == 0:
                await asyncio.gather(*tasks)
                tasks = []
                logger.info(f"Completed batch up to {i}")
                # Optional: Add small sleep if server is overwhelmed
                # await asyncio.sleep(0.1) 
        
        if tasks:
            await asyncio.gather(*tasks)

    end_sim = time.perf_counter()
    total_time = end_sim - start_sim
    
    # Results Calculation
    if latencies:
        avg_latency = statistics.mean(latencies)
        p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
        p99_latency = statistics.quantiles(latencies, n=100)[98] # 99th percentile
        
        logger.info("=== Simulation Results ===")
        logger.info(f"Total Requests Processed: {len(latencies)}")
        logger.info(f"Total Time Taken: {total_time:.2f} seconds")
        logger.info(f"Actual Throughput: {len(latencies)/total_time:.2f} requests/sec")
        logger.info(f"Average Latency: {avg_latency:.2f} ms")
        logger.info(f"P95 Latency: {p95_latency:.2f} ms")
        logger.info(f"P99 Latency: {p99_latency:.2f} ms")
    else:
        logger.error("No successful requests recorded.")

if __name__ == "__main__":
    if TOTAL_REQUESTS > 0:
        asyncio.run(run_simulation())
