from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import RequestRideInputSerializer
from .models import RideRequest
from apps.users.models import User
from .tasks import match_pool_task, sync_pool_route_task, handle_cancel_task

class RideRequestResponseSerializer(serializers.Serializer):
    request_id = serializers.IntegerField()
    status = serializers.CharField()

class PoolStatusResponseSerializer(serializers.Serializer):
    pool_id = serializers.IntegerField()
    cab_id = serializers.IntegerField()
    pickup_eta = serializers.DateTimeField()
    drop_eta = serializers.DateTimeField()
    price = serializers.FloatField()
    passenger_count = serializers.IntegerField()
    status = serializers.CharField()

@swagger_auto_schema(
    method='post',
    request_body=RequestRideInputSerializer,
    responses={201: RideRequestResponseSerializer, 400: 'Bad Request', 404: 'User Not Found'},
    operation_description="Submit a new ride request and start the pooling process."
)
@api_view(['POST'])
@permission_classes([AllowAny])
def request_ride(request):
    serializer = RequestRideInputSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        try:
            user = User.objects.get(id=data.pop('user_id'))
            
            ride_request = RideRequest.objects.create(
                user=user,
                **data
            )
            
            # Trigger async pooling task
            match_pool_task.delay(ride_request.id)
            
            return Response({
                "request_id": ride_request.id,
                "status": "Ride request received and pooling started."
            }, status=status.HTTP_201_CREATED)
            
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    responses={200: RideRequestResponseSerializer, 400: 'Bad Request', 404: 'Ride Request Not Found'},
    operation_description="Cancel an existing ride request."
)
@api_view(['POST'])
@permission_classes([AllowAny])
def cancel_ride(request, ride_id):
    try:
        ride_request = RideRequest.objects.get(id=ride_id)
        
        # Check if already cancelled
        if ride_request.status == RideRequest.Status.CANCELLED:
            return Response({"error": "Ride already cancelled"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update status
        ride_request.status = RideRequest.Status.CANCELLED
        ride_request.save()

        # Handle Pool memberships
        from apps.pooling.models import PoolMember
        memberships = PoolMember.objects.filter(ride_request=ride_request)
        
        pool_ids_to_recalculate = list(memberships.values_list('pool_id', flat=True))
        
        # Remove from pools
        memberships.delete()
        
        # Trigger route recalculation for affected pools
        for pool_id in pool_ids_to_recalculate:
            sync_pool_route_task.delay(pool_id)
        
        handle_cancel_task.delay(ride_id)
            
        return Response({
            "request_id": ride_id,
            "status": "Ride cancelled and pools updated."
        })
        
    except RideRequest.DoesNotExist:
        return Response({"error": "Ride request not found"}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    method='get',
    responses={200: PoolStatusResponseSerializer, 404: 'Ride Request Not Found'},
    operation_description="Get the current status of a ride request including its pool assignment."
)
@api_view(['GET'])
@permission_classes([AllowAny])
def pool_status(request, ride_id):
    try:
        ride_request = RideRequest.objects.get(id=ride_id)
        
        # Find the pool membership for this ride
        from apps.pooling.models import PoolMember
        membership = PoolMember.objects.filter(ride_request=ride_request).first()
        
        if not membership:
            return Response({
                "status": ride_request.status,
                "message": "Ride is not currently assigned to a pool."
            })

        pool = membership.pool
        
        # Construct response
        # Note: 'price' is a placeholder for now as pricing app is empty
        return Response({
            "pool_id": pool.id,
            "cab_id": pool.cab.id,
            "pickup_eta": membership.pickup_eta,
            "drop_eta": membership.drop_eta,
            "price": 0.0, # Placeholder
            "passenger_count": pool.members.count(),
            "status": ride_request.status
        })
        
    except RideRequest.DoesNotExist:
        return Response({"error": "Ride request not found"}, status=status.HTTP_404_NOT_FOUND)
