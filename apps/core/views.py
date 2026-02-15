from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.rides.models import RideRequest, Cab
from apps.pooling.models import Pool, PoolMember
from apps.users.models import User
from apps.rides.tasks import match_pool_task, sync_pool_route_task
from .tasks import sample_async_task

# --- Dashboard Views (Templates) ---

def dashboard(request):
    rides = RideRequest.objects.all().order_by('-created_at')[:10]
    return render(request, 'core/dashboard.html', {'rides': rides})

def create_ride_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        
        ride = RideRequest.objects.create(
            user=user,
            pickup_lat=request.POST.get('pickup_lat'),
            pickup_lng=request.POST.get('pickup_lng'),
            drop_lat=request.POST.get('drop_lat'),
            drop_lng=request.POST.get('drop_lng'),
            seats_required=request.POST.get('seats_required'),
            luggage_units=request.POST.get('luggage_units'),
            detour_tolerance_minutes=request.POST.get('detour_tolerance_minutes')
        )
        
        match_pool_task.delay(ride.id)
        messages.success(request, f"Ride #{ride.id} created successfully! Pooling started.")
        return redirect('dashboard')
    
    users = User.objects.all()
    if not users.exists():
        User.objects.create(name="Demo User", phone="9988776655")
        users = User.objects.all()
        
    return render(request, 'core/create_ride.html', {'users': users})

def view_pools_view(request):
    pools = Pool.objects.all().prefetch_related('members__ride_request__user', 'cab')
    return render(request, 'core/view_pools.html', {'pools': pools})

def cancel_ride_view(request, ride_id):
    if request.method == 'POST':
        ride = get_object_or_404(RideRequest, id=ride_id)
        ride.status = RideRequest.Status.CANCELLED
        ride.save()
        
        memberships = PoolMember.objects.filter(ride_request=ride)
        pool_ids = list(memberships.values_list('pool_id', flat=True))
        memberships.delete()
        
        for pid in pool_ids:
            sync_pool_route_task.delay(pid)
            
        messages.info(request, f"Ride #{ride_id} has been cancelled.")
    return redirect('dashboard')

# --- API Endpoints ---

@swagger_auto_schema(
    method='get',
    responses={200: openapi.Response('Health status', openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status': openapi.Schema(type=openapi.TYPE_STRING),
            'project': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ))},
    operation_description="Check the health of the API service."
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({"status": "healthy", "project": "smart_airport_pooling"})

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, default='World'),
        }
    ),
    responses={200: openapi.Response('Task triggered', openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'task_id': openapi.Schema(type=openapi.TYPE_STRING),
            'status': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ))},
    operation_description="Trigger a sample asynchronous background task."
)
@api_view(['POST'])
@permission_classes([AllowAny])
def trigger_task(request):
    name = request.data.get('name', 'World')
    task = sample_async_task.delay(name)
    return Response({"task_id": task.id, "status": "Task triggered!"})

@api_view(['GET'])
@permission_classes([AllowAny])
def debug_stats(request):
    """
    Interview Debug Endpoint: Returns system performance and pooling metrics.
    """
    import time
    total_reqs = RideRequest.objects.count()
    pooled_reqs = RideRequest.objects.filter(status=RideRequest.Status.POOLED).count()
    active_pools = Pool.objects.filter(status=Pool.Status.POOLED).count()
    
    avg_passengers = pooled_reqs / active_pools if active_pools > 0 else 0
    
    return Response({
        "total_requests": total_reqs,
        "pooled_requests": pooled_reqs,
        "active_pools": active_pools,
        "avg_passengers_per_pool": round(avg_passengers, 2),
        "system_status": "Healthy",
        "timestamp": time.time()
    })
    return Response({
        "total_requests": total_reqs,
        "pooled_requests": pooled_reqs,
        "active_pools": active_pools,
        "avg_passengers_per_pool": round(avg_passengers, 2),
        "system_status": "Healthy",
        "timestamp": time.time()
    })
