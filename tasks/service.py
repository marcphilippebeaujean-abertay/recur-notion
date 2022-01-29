import logging
from datetime import datetime, timezone

import pytz
from notion_client import APIResponseError

from notion_database.service import (
    get_or_update_database_from_simple_database_dict_returning_model,
    query_user_notion_database_with_api_by_id_as_dict,
)
from notion_properties.constants import IGNORED_PROPERTIES_SET
from notion_properties.dto import NotionPropertyDto
from workspaces.service import NotionAccessTokenInvalidException

from .models import RecurringTask

# Get an instance of a logger
logger = logging.getLogger(__name__)


class RecurringTaskNotFoundException(Exception):
    pass


class RecurringTaskBadFormData(Exception):
    pass


class RecurringTaskMissingDatabaseException(Exception):
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


def query_task_with_scheduler_job_prefetch(user, task_pk):
    try:
        return RecurringTask.objects.filter(owner=user, pk=task_pk).prefetch_related(
            "scheduler_job"
        )[0]
    except IndexError:
        raise RecurringTaskNotFoundException(
            f"Could not find recurring task that was updated with pk {task_pk}"
        )


def update_recurring_task_interval(user, task_pk, interval_value_str):
    updated_recurring_task = query_task_with_scheduler_job_prefetch(user, task_pk)
    updated_recurring_task.interval = interval_value_str
    updated_recurring_task.save()
    return updated_recurring_task


def update_recurring_task_name(user, task_pk, new_task_name_str):
    updated_recurring_task = query_task_with_scheduler_job_prefetch(user, task_pk)
    updated_recurring_task.name = new_task_name_str
    update_recurring_task_property_title_from_name(
        recurring_task=updated_recurring_task
    )
    updated_recurring_task.save()
    return updated_recurring_task


def update_recurring_task_start_time(
    user, task_pk, start_time_as_string, client_timezone
):
    updated_recurring_task = query_task_with_scheduler_job_prefetch(
        user=user, task_pk=task_pk
    )
    if start_time_as_string is None or client_timezone is None:
        raise RecurringTaskBadFormData()
    # this variable format is probably breaking the template
    user_unlocalized_start_datetime = datetime.strptime(
        start_time_as_string, "%Y-%m-%dT%H:%M"
    )
    # convert from client local timezone to UTC
    user_timezone = pytz.timezone(client_timezone)
    localized_user_start_datetime = user_timezone.localize(
        user_unlocalized_start_datetime
    )
    # localize back to UTC
    start_date_utc_datetime = datetime.fromtimestamp(
        localized_user_start_datetime.timestamp(), tz=timezone.utc
    )
    updated_recurring_task.start_time = start_date_utc_datetime
    updated_recurring_task.start_date = start_date_utc_datetime
    updated_recurring_task.save()
    return updated_recurring_task


def update_task_notion_database_from_request_dict(user, database_id, task_pk):
    try:
        recurring_task_model_to_be_updated = RecurringTask.objects.filter(
            owner=user, pk=task_pk
        ).prefetch_related("database")[0]
    except IndexError:
        raise RecurringTaskNotFoundException(
            f"Could not find recurring task that was updated with pk {task_pk}"
        )
    notion_db_id_str = database_id
    try:
        task_database_dict = query_user_notion_database_with_api_by_id_as_dict(
            user_model=user, database_id_str=notion_db_id_str
        )
        task_database = (
            get_or_update_database_from_simple_database_dict_returning_model(
                simple_database_dict=task_database_dict
            )
        )
        recurring_task_model_to_be_updated.database = task_database
        recurring_task_model_to_be_updated.properties_json = (
            create_notion_task_property_list(
                task_database.properties_schema_json, dict()
            )
        )
        recurring_task_model_to_be_updated.save()
    except APIResponseError as error:
        if error.code == "unauthorized":
            raise NotionAccessTokenInvalidException()
    return recurring_task_model_to_be_updated


def update_task_notion_properties_from_request_dict(
    user, property_value_by_id_dict, task_pk
):
    updated_recurring_task = query_task_with_scheduler_job_prefetch(
        user=user, task_pk=task_pk
    )
    task_database = updated_recurring_task.database
    if task_database is None:
        raise RecurringTaskMissingDatabaseException(
            f"Could not find a database for task with id {task_pk}"
        )
    updated_recurring_task.properties_json = create_notion_task_property_list(
        db_schema_dict_list=task_database.properties_schema_json,
        id_value_dict=property_value_by_id_dict,
    )
    update_recurring_task_property_title_from_name(
        recurring_task=updated_recurring_task
    )
    updated_recurring_task.save()
    return updated_recurring_task


def create_notion_task_property_list(db_schema_dict_list, id_value_dict):
    notion_properties_as_dict_list = []
    for notion_property_dict in db_schema_dict_list:
        # In the Request form data, each value is associated by the id of the Notion property.
        # The ID of the property is the key.
        notion_property_container_dto = NotionPropertyDto.from_dto_dict(
            notion_property_dict
        )
        property_type_str = notion_property_container_dto.notion_type
        if property_type_str in IGNORED_PROPERTIES_SET:
            continue
        # special case checkbox property: input forms only include the field if checkbox is checked. Thus, to get the
        # right value, we need to just check if the expected checkbox property was in our request dictionary
        property_is_in_request_form = notion_property_container_dto.id in id_value_dict
        if property_type_str == "checkbox":
            if property_is_in_request_form:
                notion_property_container_dto.value = True
            else:
                notion_property_container_dto.value = False
        elif property_is_in_request_form:
            notion_property_container_dto.value = id_value_dict[
                notion_property_container_dto.id
            ]
        notion_properties_as_dict_list.append(notion_property_container_dto.dto_dict())
    return notion_properties_as_dict_list
