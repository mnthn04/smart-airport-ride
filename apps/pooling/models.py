from django.db import models
from apps.core.models import BaseModel
from apps.rides.models import Cab

class Pool(BaseModel):
    class Status(models.TextChoices):
        POOLED = 'pooled', 'Pooled'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    cab = models.ForeignKey(
        Cab,
        on_delete=models.CASCADE,
        related_name='pools'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.POOLED,
        db_index=True
    )

    def __str__(self):
        return f"Pool {self.id} - {self.cab.driver_name} ({self.status})"

    class Meta:
        verbose_name = "Pool"
        verbose_name_plural = "Pools"
        ordering = ['-created_at']


from apps.rides.models import RideRequest
from django.core.exceptions import ValidationError
from django.db.models import Sum

class PoolMember(BaseModel):
    pool = models.ForeignKey(
        Pool,
        on_delete=models.CASCADE,
        related_name='members'
    )
    ride_request = models.ForeignKey(
        RideRequest,
        on_delete=models.CASCADE,
        related_name='pool_memberships'
    )
    sequence_order = models.PositiveSmallIntegerField(default=1)
    pickup_eta = models.DateTimeField(null=True, blank=True)
    drop_eta = models.DateTimeField(null=True, blank=True)

    def clean(self):
        super().clean()
        
        # Calculate current usage in the pool (excluding self if already exists)
        current_members = self.pool.members.exclude(id=self.id)
        
        current_seats = current_members.aggregate(
            total=Sum('ride_request__seats_required')
        )['total'] or 0
        
        current_luggage = current_members.aggregate(
            total=Sum('ride_request__luggage_units')
        )['total'] or 0

        cab = self.pool.cab
        
        # Check seat constraints
        if current_seats + self.ride_request.seats_required > cab.total_seats:
            raise ValidationError(
                f"Adding this ride request would exceed the cab's seat capacity "
                f"({cab.total_seats}). Current: {current_seats}, Required: {self.ride_request.seats_required}"
            )

        # Check luggage constraints
        if current_luggage + self.ride_request.luggage_units > cab.luggage_capacity:
            raise ValidationError(
                f"Adding this ride request would exceed the cab's luggage capacity "
                f"({cab.luggage_capacity}). Current: {current_luggage}, Units: {self.ride_request.luggage_units}"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pool {self.pool.id} Member - {self.ride_request.user.name}"

    class Meta:
        verbose_name = "Pool Member"
        verbose_name_plural = "Pool Members"
        unique_together = ('pool', 'ride_request')
        ordering = ['sequence_order']
