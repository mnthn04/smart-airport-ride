from rest_framework import serializers
from .models import RideRequest

class RideRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideRequest
        fields = [
            'id', 'user', 'pickup_lat', 'pickup_lng', 'drop_lat', 'drop_lng',
            'seats_required', 'luggage_units', 'detour_tolerance_minutes', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'created_at']

class RequestRideInputSerializer(serializers.Serializer):
    pickup_lat = serializers.DecimalField(max_digits=9, decimal_places=6)
    pickup_lng = serializers.DecimalField(max_digits=9, decimal_places=6)
    drop_lat = serializers.DecimalField(max_digits=9, decimal_places=6)
    drop_lng = serializers.DecimalField(max_digits=9, decimal_places=6)
    seats_required = serializers.IntegerField(min_value=1, default=1)
    luggage_units = serializers.IntegerField(min_value=0, default=1)
    detour_tolerance_minutes = serializers.IntegerField(min_value=0, default=15)
    user_id = serializers.IntegerField() # Temporary for now since we don't have auth fully setup
