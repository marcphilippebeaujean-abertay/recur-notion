from datetime import datetime, timedelta, tzinfo

import pytz
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django_q.models import Schedule

# Create your models here.
from accounts.models import CustomUser
from notion_database.models import NotionDatabase


class RecurringTask(models.Model):
    class TaskIntervals(models.TextChoices):
        EVERY_DAY = "1", _("Every Day")
        EVERY_7_DAYS = "7", _("Every 7 Days")
        EVERY_30_DAYS = "30", _("Every 30 Days")
        EVERY_365_DAYS = "365", _("Every 365 Days")

    name = models.CharField(max_length=255, default="New Page")
    # ID used to find original task this one is being cloned from
    database = models.ForeignKey(
        NotionDatabase,
        to_field="database_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    owner = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="tasks"
    )
    start_time = models.DateTimeField(default=now() + timedelta(days=1))
    properties_json = models.JSONField(encoder=DjangoJSONEncoder, default=dict)
    scheduler_job = models.OneToOneField(
        Schedule,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None,
        related_name="related_recurring_task",
    )
    interval = models.CharField(
        max_length=30,
        choices=TaskIntervals.choices,
        default=TaskIntervals.EVERY_DAY,
    )

    @property
    def days_till_next_task(self):
        date_difference = (
            now() - datetime.fromisoformat(self.start_time.isoformat())
        ).days
        if date_difference < 0:
            return abs(date_difference)
        if date_difference == 0:
            return 0
        days_till_task_is_posted = (int(self.interval) - 1) - (
            date_difference % int(self.interval)
        )
        return days_till_task_is_posted

    @property
    def days_till_schedule_preview_text(self):
        if self.days_till_next_task == 0:
            return "Page will be created again within less than a day."
        return f"Page will be created again within {self.days_till_next_task + 1} days."

    def get_interval_as_djangoq_schedule_type(self):
        interval_value_string = str(self.interval)
        if interval_value_string == self.TaskIntervals.EVERY_DAY.value:
            return Schedule.DAILY
        if interval_value_string == self.TaskIntervals.EVERY_7_DAYS.value:
            return Schedule.WEEKLY
        if interval_value_string == self.TaskIntervals.EVERY_30_DAYS.value:
            return Schedule.MONTHLY
        if interval_value_string == self.TaskIntervals.EVERY_365_DAYS.value:
            return Schedule.YEARLY
        raise Exception(
            f"Invalid Task Interval, cannot convert {interval_value_string} to Schedule"
        )

    def calculate_next_start_time_for_job(self):
        start_time_as_datetime = datetime.fromisoformat(self.start_time.isoformat())
        timezone_aware_now = datetime.now(start_time_as_datetime.tzinfo)
        if timezone_aware_now < start_time_as_datetime:
            return start_time_as_datetime
        next_run_datetime_without_day_translation = datetime(
            year=timezone_aware_now.year,
            month=timezone_aware_now.month,
            minute=start_time_as_datetime.minute,
            hour=start_time_as_datetime.hour,
            second=start_time_as_datetime.second,
            day=timezone_aware_now.day,
            tzinfo=pytz.utc,
        )
        # days till next task only translates
        return next_run_datetime_without_day_translation + timedelta(
            days=self.days_till_next_task
        )

    def save(self, *args, **kwargs):
        is_scheduler_job_created_from_save = self.scheduler_job is None

        if is_scheduler_job_created_from_save:
            self.scheduler_job = Schedule.objects.create(
                func="tasks.jobs.create_recurring_task_in_notion",
                next_run=self.calculate_next_start_time_for_job(),
                schedule_type=self.get_interval_as_djangoq_schedule_type(),
            )
        else:
            Schedule.objects.filter(id=self.scheduler_job_id).update(
                next_run=self.calculate_next_start_time_for_job(),
                schedule_type=self.get_interval_as_djangoq_schedule_type(),
            )
        super().save(*args, **kwargs)
        if is_scheduler_job_created_from_save:
            Schedule.objects.filter(id=self.scheduler_job_id).update(args=f"{self.pk}")

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        if self.scheduler_job:
            self.scheduler_job.delete()
