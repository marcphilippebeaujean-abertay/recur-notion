import datetime
import logging

import httpx
import notion_client
from django.utils import timezone
from notion_client import APIResponseError

from notion_database.service import (
    convert_notion_database_resp_dict_to_simple_database_dict_list,
)
from notion_properties.dto import NotionPropertyDto
from notion_properties.service import (
    create_properties_dict_for_create_page_api_request_from_property_dto_list,
)
from tasks.service import create_notion_task_property_list_from_db_schema

from .models import RecurringTask

logger = logging.getLogger(__name__)


def create_recurring_task_in_notion(task_pk):
    logger.info(f"Creating new task for PK: {task_pk}")
    try:
        task_model = RecurringTask.objects.all().filter(pk=task_pk)[0]
    except IndexError:
        raise Exception(
            f"Task with id {task_pk} be created because it did not exist in Database anymore."
        )
    job_time_difference_in_seconds = abs(
        task_model.scheduler_job.next_run - timezone.now()
    ).total_seconds()
    if task_model.scheduler_job is None or job_time_difference_in_seconds > 2:
        return
    notion_db_model = task_model.database
    if (
        notion_db_model is None
        or notion_db_model.database_id is None
        or notion_db_model.database_id == ""
    ):
        logger.info(
            f"Database id was not set for Recurring Task with PK {task_pk}! Cannot handle request."
        )
        return
    user = task_model.owner
    workspace_access_queryset = user.workspace_access.all()
    if workspace_access_queryset.count == 0:
        raise Exception("User did not have a workspace access.")
    try:
        client = notion_client.Client(
            auth=list(workspace_access_queryset)[0].access_token
        )
    except IndexError:
        logger.error("User did not have a workspace access")
        raise Exception("User did not have a workspace access.")
    # Fetch the given database from Notion
    try:
        notion_db_schema_resp_dict = client.databases.retrieve(
            database_id=notion_db_model.database_id
        )
    except (httpx.HTTPStatusError, APIResponseError) as error:
        if error.code == "unauthorized":
            raise Exception("invalid api token")
        logger.info("Failed to retrieve Database for Task!")
        task_model.database = None
        task_model.save()
        return
    database_dict = convert_notion_database_resp_dict_to_simple_database_dict_list(
        notion_db_schema_resp_dict
    )
    current_task_properties_value_by_id_dict = {
        property_dict["id"]: property_dict["value"]
        for property_dict in task_model.properties_json
    }
    # Check which properties are still in the Database
    property_dict_list = create_notion_task_property_list_from_db_schema(
        db_schema_dict_list=[
            property_dto.dto_dict() for property_dto in database_dict["properties"]
        ],
        property_value_by_id_dict=current_task_properties_value_by_id_dict,
    )
    # check if the provided property type is that in the schema
    request_properties_dict = (
        create_properties_dict_for_create_page_api_request_from_property_dto_list(
            [
                NotionPropertyDto.from_dto_dict(property_dict)
                for property_dict in property_dict_list
            ]
        )
    )
    page_parent_dict = {"database_id": notion_db_model.database_id}
    client.pages.create(parent=page_parent_dict, properties=request_properties_dict)

    notion_db_model.properties_schema_json = property_dict_list
    notion_db_model.save()
    # Call the create Notion Page Method
    logger.debug(f"Created recurring task with id {task_model.pk} successfully.")
