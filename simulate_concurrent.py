import asyncio
import aiohttp
import time
import statistics

BASE_URL = "http://localhost:8000/api/rides/request-ride/"
CONCURRENT_REQUESTS = 100

async def send_request(session, idx):
    data = {
        "user_id": 1,
        "pickup_lat": 12.97,
        "pickup_lng": 77.59,
        "drop_lat": 13.19,
        "drop_lng": 77.70,
        "seats_required": 1,
        "luggage_units": 1,
        "detour_tolerance_minutes": 15
    }
    start = time.perf_counter()
    try:
        async with session.post(BASE_URL, json=data) as response:
            latency = (time.perf_counter() - start) * 1000
            return response.status, latency
    except Exception as e:
        return str(e), 0

async def main():
    print(f"Starting concurrency Stress Test: {CONCURRENT_REQUESTS} requests...")
    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session, i) for i in range(CONCURRENT_REQUESTS)]
        results = await asyncio.gather(*tasks)
    
    statuses = [r[0] for r in results]
    latencies = [r[1] for r in results if r[1] > 0]
    
    success_count = statuses.count(201)
    error_count = len(statuses) - success_count
    
    print("\n=== Stress Test Report ===")
    print(f"Total Requests: {CONCURRENT_REQUESTS}")
    print(f"Successful (201 Created): {success_count}")
    print(f"Errors: {error_count}")
    
    if latencies:
        print(f"Avg Latency: {statistics.mean(latencies):.2f}ms")
        print(f"Min Latency: {min(latencies):.2f}ms")
        print(f"Max Latency: {max(latencies):.2f}ms")

if __name__ == "__main__":
    asyncio.run(main())
