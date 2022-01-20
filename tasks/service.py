import logging
from datetime import datetime, timezone

import pytz

from notion_database.service import (
    get_or_update_database_from_simple_database_dict_returning_model,
    query_user_notion_database_by_id,
)
from notion_properties.constants import IGNORED_PROPERTIES_SET
from notion_properties.dto import NotionPropertyDto

from .models import RecurringTask

# Get an instance of a logger
logger = logging.getLogger(__name__)


class RecurringTaskNotFoundException(Exception):
    pass


class RecurringTaskBadFormData(Exception):
    pass


def update_recurring_task_property_title_from_name(recurring_task):
    property_json_includes_title = False
    for property_dict in recurring_task.properties_json:
        if property_dict["id"] == "title":
            property_json_includes_title = True
            property_dict["value"] = recurring_task.name
    if not property_json_includes_title:
        task_title_property_dto = NotionPropertyDto(
            name_str="Name",
            id_str="title",
            notion_type_str="title",
            value=recurring_task.name,
            assign_default_value=False,
        )
        recurring_task.properties_json = [task_title_property_dto.dto_dict()]


def update_recurring_task_schedule_from_request_data(request, task_pk):
    try:
        updated_recurring_task = RecurringTask.objects.filter(
            owner=request.user, pk=task_pk
        ).prefetch_related("scheduler_job")[0]
    except IndexError:
        raise RecurringTaskNotFoundException(
            f"Could not find recurring task that was updated with pk {task_pk}"
        )
    if "interval" in request.POST:
        updated_recurring_task.interval = request.POST["interval"]
    elif "task-name" in request.POST:
        updated_recurring_task.name = request.POST["task-name"]
        update_recurring_task_property_title_from_name(
            recurring_task=updated_recurring_task
        )
    elif "start-time" in request.POST and "X-Client-Timezone" in request.headers:
        # this variable format is probably breaking the template
        user_unlocalized_start_datetime = datetime.strptime(
            request.POST["start-time"], "%Y-%m-%dT%H:%M"
        )
        # convert from client local timezone to UTC
        user_timezone = pytz.timezone(request.headers["X-Client-Timezone"])
        localized_user_start_datetime = user_timezone.localize(
            user_unlocalized_start_datetime
        )
        # localize back to UTC
        start_date_utc_datetime = datetime.fromtimestamp(
            localized_user_start_datetime.timestamp(), tz=timezone.utc
        )
        updated_recurring_task.start_time = start_date_utc_datetime
        updated_recurring_task.start_date = start_date_utc_datetime
    else:
        raise RecurringTaskBadFormData()
    updated_recurring_task.save()
    return updated_recurring_task


def update_task_notion_properties_from_request_dict(request_dict, task_pk):
    try:
        updated_recurring_task = RecurringTask.objects.filter(
            owner=request_dict.user, pk=task_pk
        ).prefetch_related("scheduler_job")[0]
    except IndexError:
        raise RecurringTaskNotFoundException(
            f"Could not find recurring task that was updated with pk {task_pk}"
        )
    if "X-Selected-Database-Id" not in request_dict.headers:
        raise RecurringTaskBadFormData("No selected database id in the request header!")
    notion_db_id_str = request_dict.headers["X-Selected-Database-Id"]
    database_dict = query_user_notion_database_by_id(
        user_model=request_dict.user, database_id_str=notion_db_id_str
    )
    updated_recurring_task.database = (
        get_or_update_database_from_simple_database_dict_returning_model(
            simple_database_dict=database_dict
        )
    )
    notion_properties_as_dict_list = []
    notion_properties_container_list = database_dict["properties"]
    for property_container in notion_properties_container_list:
        # In the Request form data, each value is associated by the id of the Notion property.
        # The ID of the property is the key.
        property_type_str = property_container.notion_type
        if property_type_str in IGNORED_PROPERTIES_SET:
            continue
        # special case checkbox property: input forms only include the field if checkbox is checked. Thus, to get the
        # right value, we need to just check if the expected checkbox property was in our request dictionary
        property_is_in_request_form = property_container.id in request_dict.POST
        if property_type_str == "checkbox":
            if property_is_in_request_form:
                property_container.value = True
            else:
                property_container.value = False
        elif property_is_in_request_form:
            property_container.value = request_dict.POST[property_container.id]
        notion_properties_as_dict_list.append(property_container.dto_dict())
    updated_recurring_task.properties_json = notion_properties_as_dict_list
    update_recurring_task_property_title_from_name(
        recurring_task=updated_recurring_task
    )
    should_persist_changes = request_dict.headers.get("X-Persist-Changes", "false")
    if should_persist_changes == "true":
        updated_recurring_task.save()
    return updated_recurring_task
