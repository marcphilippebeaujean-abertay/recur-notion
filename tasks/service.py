from notion_client import Client

from .models import RecurringTask
from notion_database.service import query_user_notion_database_by_id, get_default_value_by_notion_property_type

import logging
import pytz
from datetime import datetime, timezone

# Get an instance of a logger
logger = logging.getLogger(__name__)


class RecurringTaskNotFoundException(Exception):
    pass


class RecurringTaskBadFormData(Exception):
    pass


def update_recurring_task_schedule_from_request_data(request_dict, task_pk):
    try:
        updated_recurring_task = RecurringTask.objects.filter(owner=request_dict.user,
                                                              pk=task_pk).prefetch_related('scheduler_job')[0]
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


def update_task_notion_properties_from_request_dict(request_dict, task_pk):
    try:
        updated_recurring_task = RecurringTask.objects.filter(owner=request_dict.user,
                                                              pk=task_pk).prefetch_related('scheduler_job')[0]
    except IndexError:
        raise RecurringTaskNotFoundException(f'Could not find recurring task that was updated with pk {task_pk}')
    if 'selectedDatabaseId' not in request_dict.POST:
        raise RecurringTaskBadFormData('Requiring notion db id to fetch parameters')
    notion_db_id_str = request_dict.POST['selectedDatabaseId']
    database_dict = query_user_notion_database_by_id(user_model=request_dict.user, database_id_str=notion_db_id_str)
    updated_recurring_task.database_id = notion_db_id_str
    updated_recurring_task.database_name = database_dict['name']

    notion_properties_as_dict_list = []
    notion_properties_container_list = database_dict['properties']
    request_body_dict = request_dict.POST.dict()
    request_body_dict.pop('selectedDatabaseId')
    for property_container in notion_properties_container_list:
        # In the Request form data, each value is associated by the id of the Notion property.
        # The ID of the property is the key.
        property_container.value = request_body_dict.get(property_container.id,
                                                         get_default_value_by_notion_property_type(property_container.notion_type))
        notion_properties_as_dict_list.append(property_container.dict())

    updated_recurring_task.properties_json = notion_properties_as_dict_list
    updated_recurring_task.save()
    return updated_recurring_task
