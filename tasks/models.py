from datetime import datetime

from django.utils.timezone import now, template_localtime
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils import timezone


# Create your models here.
from accounts.models import CustomUser


class RecurringTask(models.Model):
    name = models.CharField(max_length=255)
    # ID used to find original task this one is being cloned from
    cloned_task_notion_id = models.CharField(max_length=255)
    cloned_task_url = models.CharField(max_length=255)
    database_id = models.CharField(max_length=255)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tasks')
    start_date = models.DateField(default=now)
    start_time = models.DateTimeField(default=timezone.now)

    class TaskIntervals(models.TextChoices):
        EVERY_DAY = '1', _('Every Day')
        EVERY_7_DAYS = '7', _('Every 7 Days')
        EVERY_30_DAYS = '30', _('Every 30 Days')
        EVERY_365_DAYS = '365', _('Every 365 Days')

    interval = models.CharField(
        max_length=30,
        choices=TaskIntervals.choices,
        default=TaskIntervals.EVERY_DAY,
    )

    @property
    def days_till_next_task(self):
        date_difference = (datetime.now() - datetime.fromisoformat(self.start_date.isoformat())).days
        if date_difference < 0:
            return max(1, abs(date_difference))
        return int(self.interval) - (date_difference % int(self.interval))

    @property
    def should_create_task_today(self):
        date_difference = (datetime.now() - datetime.fromisoformat(self.start_date.isoformat())).days
        if date_difference < 0:
            return False
        if date_difference is 0:
            return True
        if int(self.interval) is 1:
            return True
        return (int(self.interval) % date_difference) is 0
