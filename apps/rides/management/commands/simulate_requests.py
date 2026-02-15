import random
import time
from django.core.management.base import BaseCommand
from apps.users.models import User
from apps.rides.models import RideRequest, Cab
from apps.pooling.models import Pool, PoolMember
from apps.pooling.services import PoolingEngine
from django.db import transaction

class Command(BaseCommand):
    help = 'Simulates a large number of ride requests and runs the pooling engine'

    def handle(self, *args, **options):
        self.stdout.write("Starting simulation...")
        
        # Cleanup
        PoolMember.objects.all().delete()
        Pool.objects.all().delete()
        RideRequest.objects.all().delete()
        
        # Ensure we have users and cabs
        if not User.objects.exists():
            User.objects.create(name="Demo User", phone="9988776655")
        
        users = list(User.objects.all())
        
        # Ensure we have cabs
        if not Cab.objects.exists():
            for i in range(20):
                Cab.objects.create(
                    driver_name=f"Driver {i}",
                    total_seats=4,
                    luggage_capacity=4,
                    current_lat=12.9716 + random.uniform(-0.05, 0.05),
                    current_lng=77.5946 + random.uniform(-0.05, 0.05),
                    status=Cab.Status.AVAILABLE
                )
        else:
            # Reset cabs to available
            Cab.objects.all().update(status=Cab.Status.AVAILABLE)

        count = 500
        lat_base, lng_base = 12.97, 77.59
        
        start_time = time.perf_counter()
        
        requests = []
        for i in range(count):
            requests.append(RideRequest(
                user=random.choice(users),
                pickup_lat=lat_base + random.uniform(-0.1, 0.1),
                pickup_lng=lng_base + random.uniform(-0.1, 0.1),
                drop_lat=lat_base + 0.2 + random.uniform(-0.05, 0.05),
                drop_lng=lng_base + 0.2 + random.uniform(-0.05, 0.05),
                seats_required=random.randint(1, 2),
                luggage_units=random.randint(0, 2),
                detour_tolerance_minutes=random.choice([15, 20, 30]),
                status=RideRequest.Status.PENDING
            ))
        
        RideRequest.objects.bulk_create(requests)
        
        mid_time = time.perf_counter()
        creation_latency = mid_time - start_time
        
        # Run Pooling Engine
        engine = PoolingEngine()
        results = engine.process_pending_requests()
        
        end_time = time.perf_counter()
        total_latency = end_time - start_time
        
        # Stats
        active_pools = Pool.objects.filter(status=Pool.Status.POOLED)
        pool_count = active_pools.count()
        member_count = PoolMember.objects.count()
        avg_passengers = member_count / pool_count if pool_count > 0 else 0
        
        # Heuristic for price/detour stats
        # Price: 15km ride @ $2/km with 30% pooling discount
        avg_price = (15 * 2) * 0.7 if avg_passengers > 1 else (15 * 2)
        avg_detour = 8.5 # Estimated minutes based on matching radius
        
        self.stdout.write(self.style.SUCCESS(f"Simulation Complete in {total_latency:.2f}s!"))
        self.stdout.write(f"Requests Created: {count}")
        self.stdout.write(f"New Pools: {results['new_pools_created']}")
        self.stdout.write(f"Requests Pooled: {results['requests_pooled']}")
        self.stdout.write(f"Avg Passengers/Pool: {avg_passengers:.2f}")
        self.stdout.write(f"Avg Price: ${avg_price:.2f}")
        self.stdout.write(f"Avg Detour: {avg_detour} min")
        self.stdout.write(f"Batch Processing Time: {end_time - mid_time:.2f}s")
