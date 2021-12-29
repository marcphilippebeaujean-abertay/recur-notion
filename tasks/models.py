from datetime import datetime

from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.db import models

from django_q.models import Schedule

# Create your models here.
from accounts.models import CustomUser


class RecurringTask(models.Model):
    class TaskIntervals(models.TextChoices):
        EVERY_DAY = '1', _('Every Day')
        EVERY_7_DAYS = '7', _('Every 7 Days')
        EVERY_30_DAYS = '30', _('Every 30 Days')
        EVERY_365_DAYS = '365', _('Every 365 Days')

    name = models.CharField(max_length=255)
    # ID used to find original task this one is being cloned from
    cloned_task_notion_id = models.CharField(max_length=255)
    cloned_task_url = models.CharField(max_length=255)
    database_id = models.CharField(max_length=255)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tasks')
    start_date = models.DateField(default=now)
    start_time = models.DateTimeField(default=now)
    scheduler_job = models.OneToOneField(
        Schedule,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None,
        related_name='related_recurring_task'
    )
    interval = models.CharField(
        max_length=30,
        choices=TaskIntervals.choices,
        default=TaskIntervals.EVERY_DAY,
    )

    @property
    def days_till_next_task(self):
        date_difference = (now() - datetime.fromisoformat(self.start_time.isoformat())).days
        if date_difference < 0:
            return max(1, abs(date_difference))
        return int(self.interval) - (date_difference % int(self.interval))

    def get_interval_as_djangoq_schedule_type(self):
        interval_value_string = str(self.interval)
        if interval_value_string is self.TaskIntervals.EVERY_DAY.value:
            return Schedule.DAILY
        if interval_value_string is self.TaskIntervals.EVERY_7_DAYS.value:
            return Schedule.WEEKLY
        if interval_value_string is self.TaskIntervals.EVERY_30_DAYS.value:
            return Schedule.MONTHLY
        if interval_value_string is self.TaskIntervals.EVERY_365_DAYS.value:
            return Schedule.YEARLY
        raise Exception(f'Invalid Task Interval, cannot convert {interval_value_string} to Schedule')

    def save(self, *args, **kwargs):
        interval_as_schedule_type = self.get_interval_as_djangoq_schedule_type()
        if self.scheduler_job is not None:
            self.scheduler_job.delete()
        self.scheduler_job = Schedule.objects.create(
            func='tasks.jobs.create_recurring_task_in_notion',
            args=f'{self.pk}',
            schedule_type=interval_as_schedule_type,
            next_run=self.start_time
        )
        super(RecurringTask, self).save(self)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        if self.scheduler_job:
            self.scheduler_job.delete()
