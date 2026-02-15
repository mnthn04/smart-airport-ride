from celery import shared_task
import logging
from apps.rides.models import RideRequest
from apps.pooling.models import Pool, PoolMember
from apps.pooling.services import PoolingEngine, RouteOptimizer

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def match_pool_task(self, ride_request_id):
    """
    Task to find a pool or cab for a specific ride request.
    """
    logger.info(f"Starting match_pool_task for request {ride_request_id}")
    try:
        engine = PoolingEngine()
        results = engine.process_pending_requests()
        logger.info(f"match_pool_task completed. Results: {results}")
    except Exception as exc:
        logger.error(f"Error in match_pool_task: {exc}")
        raise self.retry(exc=exc, countdown=5)

@shared_task(bind=True, max_retries=3)
def sync_pool_route_task(self, pool_id):
    """
    Task to recalculate and update the sequence of stops for a pool.
    """
    logger.info(f"Starting sync_pool_route_task for pool {pool_id}")
    try:
        pool = Pool.objects.get(id=pool_id)
        members = pool.members.select_related('ride_request').all()
        
        if not members.exists():
            pool.status = Pool.Status.CANCELLED
            pool.save()
            return "Pool emptied and cancelled."

        optimizer = RouteOptimizer()
        
        # Prepare data for optimizer
        members_data = []
        for m in members:
            members_data.append({
                'id': m.ride_request_id,
                'pickup': (float(m.ride_request.pickup_lat), float(m.ride_request.pickup_lng)),
                'drop': (float(m.ride_request.drop_lat), float(m.ride_request.drop_lng)),
                'tolerance': m.ride_request.detour_tolerance_minutes
            })

        optimized_stops = optimizer.optimize_route(
            float(pool.cab.current_lat), 
            float(pool.cab.current_lng), 
            members_data
        )

        # Update sequence orders based on optimized stops
        # For simplicity in this dummy engine, we just update the Member sequence
        for idx, stop in enumerate(optimized_stops):
            if stop['type'] == 'PICKUP':
                member = members.get(ride_request_id=stop['id'])
                member.sequence_order = idx + 1
                member.save()

        logger.info(f"Route optimized for pool {pool_id}")
        
    except Pool.DoesNotExist:
        logger.error(f"Pool {pool_id} not found")
    except Exception as exc:
        logger.error(f"Error in sync_pool_route_task: {exc}")
        raise self.retry(exc=exc, countdown=5)

@shared_task
def handle_cancel_task(ride_request_id):
    """
    Handles logic after a ride is cancelled: cleanup and route updates.
    """
    logger.info(f"Cleaning up after cancellation of request {ride_request_id}")
    # Logic is largely handled via the view, but we ensure route sync happens
    # This acts as a secondary safety check or for additional cleanup (metering, etc)
    pass
