from django.db import models

# Create your models here.
from django.utils import timezone

from accounts.models import CustomUser


class Embeddable(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=255, default="New Embeddable iFrame")
    creator = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="embeddable_widgets"
    )
