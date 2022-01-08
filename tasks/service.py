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


def update_recurring_task_schedule_from_request_data(request, task_pk):
    try:
        updated_recurring_task = RecurringTask.objects.filter(owner=request.user,
                                                              pk=task_pk).prefetch_related('scheduler_job')[0]
    except IndexError:
        raise RecurringTaskNotFoundException(f'Could not find recurring task that was updated with pk {task_pk}')
    if 'interval' in request.POST:
        updated_recurring_task.interval = request.POST['interval']
    elif 'task-name' in request.POST:
        updated_recurring_task.name = request.POST['task-name']
    elif 'start-time' in request.POST and 'X-Client-Timezone' in request.headers:
        # this variable format is probably breaking the template
        user_unlocalized_start_datetime = datetime.strptime(request.POST['start-time'], '%Y-%m-%dT%H:%M')
        # convert from client local timezone to UTC
        user_timezone = pytz.timezone(request.headers['X-Client-Timezone'])
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
    if 'X-Selected-Database-Id' not in request_dict.headers:
        raise RecurringTaskBadFormData('No selected database id in the request header!')
    notion_db_id_str = request_dict.headers['X-Selected-Database-Id']
    database_dict = query_user_notion_database_by_id(user_model=request_dict.user, database_id_str=notion_db_id_str)
    updated_recurring_task.database_id = notion_db_id_str
    updated_recurring_task.database_name = database_dict['name']

    notion_properties_as_dict_list = []
    notion_properties_container_list = database_dict['properties']
    for property_container in notion_properties_container_list:
        # In the Request form data, each value is associated by the id of the Notion property.
        # The ID of the property is the key.
        if property_container.notion_type == 'checkbox':
            if property_container.id in request_dict.POST:
                property_container.value = True
            else:
                property_container.value = False
        else:
            property_container.value = request_dict.POST.get(property_container.id,
                                                             get_default_value_by_notion_property_type(property_container.notion_type))
        notion_properties_as_dict_list.append(property_container.dict())
    updated_recurring_task.properties_json = notion_properties_as_dict_list

    should_persist_changes = request_dict.headers.get('X-Persist-Changes', 'false')
    if should_persist_changes == 'true':
        updated_recurring_task.save()
    return updated_recurring_task
