from django.db import models
from apps.core.models import BaseModel

class User(BaseModel):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, unique=True, db_index=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-created_at']
