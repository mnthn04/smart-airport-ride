from django.contrib import admin
from .models import RideRequest, Cab

@admin.register(RideRequest)
class RideRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'status', 'seats_required', 
        'pickup_lat', 'pickup_lng', 'created_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = ('user__name', 'user__phone', 'id')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Cab)
class CabAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'driver_name', 'status', 'total_seats', 
        'current_lat', 'current_lng'
    )
    list_filter = ('status',)
    search_fields = ('driver_name',)
    readonly_fields = ('created_at', 'updated_at')
