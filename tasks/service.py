from notion_client import Client

from workspaces.models import NotionWorkspaceAccess
from .models import RecurringTask

import logging
import pytz
from datetime import datetime, timezone

# Get an instance of a logger
logger = logging.getLogger(__name__)


class RecurringTaskNotFoundException(Exception):
    pass


class RecurringTaskBadFormData(Exception):
    pass


def update_recurring_task_from_request_data(request_dict, task_pk):
    try:
        updated_recurring_task = RecurringTask.objects.filter(owner=request_dict.user, pk=task_pk) \
            .prefetch_related('scheduler_job')[0]
    except IndexError:
        raise RecurringTaskNotFoundException(f'Could not find recurring task that was updated with pk {task_pk}')
    if 'interval' in request_dict.POST:
        updated_recurring_task.interval = request_dict.POST['interval']
    elif 'task-name' in request_dict.POST:
        updated_recurring_task.name = request_dict.POST['task-name']
    elif 'start-time' in request_dict.POST and 'client-timezone' in request_dict.POST:
        # this variable format is probably breaking the template
        user_unlocalized_start_datetime = datetime.strptime(request_dict.POST['start-time'], '%Y-%m-%dT%H:%M')
        # convert from client local timezone to UTC
        user_timezone = pytz.timezone(request_dict.POST['client-timezone'])
        localized_user_start_datetime = user_timezone.localize(user_unlocalized_start_datetime)
        # localize back to UTC
        start_date_utc_datetime = datetime.fromtimestamp(localized_user_start_datetime.timestamp(), tz=timezone.utc)
        updated_recurring_task.start_time = start_date_utc_datetime
        updated_recurring_task.start_date = start_date_utc_datetime
    else:
        raise RecurringTaskBadFormData()
    updated_recurring_task.save()
    return updated_recurring_task
