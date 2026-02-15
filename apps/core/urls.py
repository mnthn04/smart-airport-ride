from django.urls import path
from .views import (
    health_check, 
    trigger_task, 
    dashboard, 
    create_ride_view, 
    view_pools_view, 
    cancel_ride_view,
    debug_stats
)

urlpatterns = [
    # Dashboard (Templates)
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/create/', create_ride_view, name='create_ride_view'),
    path('dashboard/pools/', view_pools_view, name='view_pools_view'),
    path('dashboard/cancel/<int:ride_id>/', cancel_ride_view, name='cancel_ride_view'),
    
    # API
    path('health/', health_check, name='health_check'),
    path('trigger-task/', trigger_task, name='trigger_task'),
    path('debug/stats/', debug_stats, name='debug_stats'),
]
