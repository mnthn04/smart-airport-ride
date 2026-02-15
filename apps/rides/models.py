from django.db import models
from apps.core.models import BaseModel
from apps.users.models import User

class RideRequest(BaseModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        POOLED = 'pooled', 'Pooled'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ride_requests'
    )
    pickup_lat = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        db_index=True
    )
    pickup_lng = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        db_index=True
    )
    drop_lat = models.DecimalField(max_digits=9, decimal_places=6)
    drop_lng = models.DecimalField(max_digits=9, decimal_places=6)
    seats_required = models.PositiveSmallIntegerField(default=1)
    luggage_units = models.PositiveSmallIntegerField(default=1)
    detour_tolerance_minutes = models.PositiveSmallIntegerField(default=15)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )

    def __str__(self):
        return f"RideRequest {self.id} - {self.user.name} ({self.status})"

    class Meta:
        verbose_name = "Ride Request"
        verbose_name_plural = "Ride Requests"
        ordering = ['-created_at']


class Cab(BaseModel):
    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        BUSY = 'busy', 'Busy'
        OFFLINE = 'offline', 'Offline'

    driver_name = models.CharField(max_length=255)
    total_seats = models.PositiveSmallIntegerField(default=4)
    luggage_capacity = models.PositiveSmallIntegerField(default=4)
    current_lat = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        db_index=True
    )
    current_lng = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
        db_index=True
    )

    def __str__(self):
        return f"{self.driver_name} - {self.status}"

    class Meta:
        verbose_name = "Cab"
        verbose_name_plural = "Cabs"
