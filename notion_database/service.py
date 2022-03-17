import logging

import notion_client

from notion_database.models import NotionDatabase, NotionPropertyMetaData
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


def query_user_notion_databases_from_api_as_model_list(user_model, query_string=None):
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
    notion_db_response_dict_list = response_dict.get("results")
    return [
        convert_notion_database_resp_dict_to_unsaved_model(
            notion_db_dict=db_response_dict,
            notion_workspace=NotionWorkspaceAccess.objects.filter(owner=user_model)[
                0
            ].workspace,
        )
        for db_response_dict in notion_db_response_dict_list
    ]


def query_saved_notion_database_model_with_api_update(user_model, database_id_str):
    database_dict = load_user_notion_client(user_model=user_model).databases.retrieve(
        database_id=database_id_str
    )
    workspace = NotionWorkspaceAccess.objects.filter(owner=user_model)[0].workspace
    database_resp_as_notion_model = convert_notion_database_resp_dict_to_saved_model(
        notion_db_dict=database_dict, notion_workspace=workspace
    )
    return database_resp_as_notion_model


def convert_notion_database_resp_dict_to_unsaved_model(
    notion_db_dict, notion_workspace
):
    title = (
        notion_db_dict["title"][0]["text"]["content"]
        if "title" in notion_db_dict and len(notion_db_dict["title"]) > 0
        else ""
    )
    unsaved_notion_database_model = NotionDatabase(
        notion_id=notion_db_dict["id"],
        database_name=title,
        notion_workspace=notion_workspace,
    )
    return unsaved_notion_database_model


def convert_notion_database_resp_dict_to_saved_model(notion_db_dict, notion_workspace):
    notion_database_unsaved_model = convert_notion_database_resp_dict_to_unsaved_model(
        notion_db_dict=notion_db_dict, notion_workspace=notion_workspace
    )
    unsaved_property_model_list = (
        get_list_of_unsaved_property_model_from_notion_database_resp_dict(
            notion_db_dict
        )
    )
    return get_or_save_notion_database_model(
        notion_database_model_unsaved=notion_database_unsaved_model,
        notion_property_meta_model_unsaved_list=unsaved_property_model_list,
    )


def get_list_of_unsaved_property_model_from_notion_database_resp_dict(notion_db_dict):
    property_dict_list = []
    for property_name in notion_db_dict["properties"].keys():
        notion_property_dict = notion_db_dict["properties"][property_name]
        # certain property types are not supported
        property_meta_data = NotionPropertyMetaData(
            property_type=notion_property_dict["type"],
            name=property_name,
            notion_id=notion_property_dict["id"],
        )
        property_dict_list.append(property_meta_data)
    return property_dict_list


def get_or_save_notion_database_model(
    notion_database_model_unsaved, notion_property_meta_model_unsaved_list
):
    db_id_str = notion_database_model_unsaved.notion_id
    (
        notion_database_model,
        notion_db_model_was_created,
    ) = NotionDatabase.objects.get_or_create(
        notion_id=db_id_str,
        notion_workspace=notion_database_model_unsaved.notion_workspace,
    )
    notion_database_model.database_name = notion_database_model_unsaved.database_name
    notion_database_model.database_id = db_id_str
    if notion_db_model_was_created:
        notion_database_model.notion_properties.set(
            [
                NotionPropertyMetaData.objects.create(
                    notion_id=notion_property_meta_data.notion_id,
                    name=notion_property_meta_data.name,
                    property_type=notion_property_meta_data.property_type,
                    database=notion_database_model,
                )
                for notion_property_meta_data in notion_property_meta_model_unsaved_list
            ]
        )
    else:
        final_notion_properties_list = []
        for property_meta_data_container in notion_property_meta_model_unsaved_list:
            (
                property_meta_data_model,
                property_db_model_was_created,
            ) = NotionPropertyMetaData.objects.get_or_create(
                database=notion_database_model,
                notion_id=property_meta_data_container.notion_id,
            )
            property_meta_data_model.name = property_meta_data_container.name
            property_meta_data_model.property_type = (
                property_meta_data_container.property_type
            )
            property_meta_data_model.save()
            final_notion_properties_list.append(property_meta_data_model)
        notion_database_model.notion_properties.set(final_notion_properties_list)
    notion_database_model.save()
    return notion_database_model
