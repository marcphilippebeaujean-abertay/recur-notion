import logging

import notion_client

from notion_database.models import NotionDatabase
from notion_properties.service import (
    get_list_of_property_dtos_from_notion_database_resp_dict,
)
from workspaces.models import NotionWorkspaceAccess

# Get an instance of a logger
logger = logging.getLogger(__name__)


class NotionApiException(Exception):
    pass


def load_user_notion_client(user_model):
    notion_workspace_access_grant_model = NotionWorkspaceAccess.objects.filter(
        owner=user_model
    ).first()
    if notion_workspace_access_grant_model is None:
        raise NotionApiException(
            f"User {user_model.username} does not have any access grants!"
        )
    logger.info(
        f"Fetching Notion Database with Access Token {notion_workspace_access_grant_model.access_token}"
    )
    return notion_client.Client(auth=notion_workspace_access_grant_model.access_token)


def query_user_notion_databases_list(user_model, query_string):
    logger.info(f"Fetching workspace pages")
    request_filter_dict = {
        "filter": {"property": "object", "value": "database"},
        "page_size": 100,
    }
    if query_string is not None and len(query_string) > 0:
        request_filter_dict["query"] = query_string
    response_dict = load_user_notion_client(user_model=user_model).search(
        **request_filter_dict
    )
    if "results" not in response_dict:
        raise NotionApiException("Unable to retrieve Database data!")
    properties_dict = response_dict.get("results")
    return [
        convert_notion_database_resp_dict_to_simple_database_dict(database_dict)
        for database_dict in properties_dict
    ]


def query_user_notion_database_with_api_by_id_as_dict(user_model, database_id_str):
    database_dict = load_user_notion_client(user_model=user_model).databases.retrieve(
        database_id=database_id_str
    )
    return convert_notion_database_resp_dict_to_simple_database_dict(database_dict)


def convert_notion_database_resp_dict_to_simple_database_dict(notion_db_dict):
    return {
        "name": notion_db_dict["title"][0]["text"]["content"],
        "id": notion_db_dict["id"],
        "properties": get_list_of_property_dtos_from_notion_database_resp_dict(
            notion_db_dict=notion_db_dict
        ),
    }


def get_or_update_database_from_simple_database_dict_returning_model(
    simple_database_dict,
):
    db_id_str = simple_database_dict["id"]
    notion_database_model, was_created = NotionDatabase.objects.get_or_create(
        database_id=db_id_str
    )
    notion_database_model.database_name = simple_database_dict["name"]
    notion_database_model.database_id = db_id_str
    notion_database_model.properties_schema_json = [
        properties_dto.dto_dict()
        for properties_dto in simple_database_dict["properties"]
    ]
    notion_database_model.save()
    return notion_database_model
