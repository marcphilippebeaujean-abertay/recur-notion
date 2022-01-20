import logging

import notion_client

from notion_database.service import (
    convert_notion_database_resp_dict_to_simple_database_dict,
)
from notion_properties.dto import NotionPropertyDto
from notion_properties.service import (
    create_properties_dict_for_create_page_api_request_from_property_dto_list,
)

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
    task_notion_db_model = task_model.database
    if (
        task_notion_db_model is None
        or task_notion_db_model.database_id is None
        or task_notion_db_model.database_id == ""
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
    notion_db_schema_resp_dict = client.databases.retrieve(
        database_id=task_notion_db_model.database_id
    )
    database_dict = convert_notion_database_resp_dict_to_simple_database_dict(
        notion_db_schema_resp_dict
    )
    # Check which properties are still in the Database
    notion_database_property_id_set = {
        property_dto.id for property_dto in database_dict["properties"]
    }
    property_dto_list = [
        NotionPropertyDto.from_dto_dict(property_dto)
        for property_dto in task_model.properties_json
        if property_dto["id"] in notion_database_property_id_set
    ]
    request_properties_dict = (
        create_properties_dict_for_create_page_api_request_from_property_dto_list(
            property_dto_list
        )
    )
    page_parent_dict = {"database_id": task_notion_db_model.database_id}
    client.pages.create(parent=page_parent_dict, properties=request_properties_dict)

    # task_notion_db_model.properties_schema_json = database_dict
    task_notion_db_model.save()
    # Call the create Notion Page Method
    logger.debug(f"Created recurring task with id {task_model.pk} successfully.")
