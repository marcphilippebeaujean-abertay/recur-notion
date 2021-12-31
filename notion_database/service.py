from tasks.service import NotionApiException
from workspaces.models import NotionWorkspaceAccess

from notion_client import Client
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


def query_user_notion_databases(user_model, query_string):
    logger.info(f'Fetching workspace pages')
    notion_workspace_access_grant_model = NotionWorkspaceAccess.objects.filter(owner=user_model).first()
    if notion_workspace_access_grant_model is None:
        raise NotionApiException(f'User {user_model.username} does not have any access grants!')
    logger.info(f'Fetching Notion Database with Access Token {notion_workspace_access_grant_model.access_token}')
    client = Client(auth=notion_workspace_access_grant_model.access_token)
    request_filter_dict = {"filter": {"property": "object", "value": "database"}, "page_size": 100}
    if query_string is not None and len(query_string) > 0:
        request_filter_dict['query'] = query_string
    api_response_object_dict_list = client.search(**request_filter_dict).get("results")
    ## TODO: fetch and turn into a dict?