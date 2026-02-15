from django.urls import path
from .views import request_ride, cancel_ride, pool_status

urlpatterns = [
    path('request-ride/', request_ride, name='request_ride'),
    path('cancel-ride/<int:ride_id>/', cancel_ride, name='cancel_ride'),
    path('pool-status/<int:ride_id>/', pool_status, name='pool_status'),
]
