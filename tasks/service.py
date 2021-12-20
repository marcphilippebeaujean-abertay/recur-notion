from notion_client import Client

from workspaces.models import NotionWorkspaceAccess

import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)


class NotionApiException(Exception):
    pass


def fetch_notion_workspace_pages_and_convert_to_task_dict(user_model, query_string):
    logger.info(f'Fetching workspace pages')
    logger.info(f'Getting Workspace Access')
    notion_workspace_access_grant_model = NotionWorkspaceAccess.objects.filter(owner=user_model).first()
    if notion_workspace_access_grant_model is None:
        raise NotionApiException(f'User {user_model.username} does not have any access grants!')

    logger.info(f'Fetching Notion Pages with Access Token {notion_workspace_access_grant_model.access_token}')
    client = Client(auth=notion_workspace_access_grant_model.access_token)
    request_filter_dict = {"filter": {"property": "object", "value": "page"}, "page_size": 20}
    if query_string is not None and len(query_string) > 0:
        request_filter_dict['query'] = query_string
    api_response_object_dict_list = client.search(**request_filter_dict).get("results")

    is_api_dict_page = lambda page_dict: 'properties' in page_dict and 'Name' in page_dict['properties']
    api_resp_non_pages_filtered = [api_object_dict for api_object_dict in api_response_object_dict_list
                                   if is_api_dict_page(api_object_dict)]

    is_page_in_database = lambda page_dict: 'parent' in page_dict and page_dict['parent']['type'] == 'database_id'
    pages_in_database_list = [task for task in api_resp_non_pages_filtered if is_page_in_database(task)]

    all_user_recurring_tasks_list = list(user_model.tasks.all())
    recurring_task_by_notion_task_id_dict = {}

    for recurring_task in all_user_recurring_tasks_list:
        recurring_task_list = recurring_task_by_notion_task_id_dict.get(recurring_task.cloned_task_notion_id, [])
        recurring_task_list.append(recurring_task)
        recurring_task_by_notion_task_id_dict[recurring_task.cloned_task_notion_id] = recurring_task_list

    convert_page_to_task_dict = lambda page_dict: {
        'title': page_dict['properties']['Name']['title'][0]['plain_text'],
        'id': page_dict['id'],
        'url': page_dict['url'],
        'db_id': page_dict['parent']['database_id'],
        'recurring_tasks': recurring_task_by_notion_task_id_dict.get(page_dict['id'], [])
    }
    return [convert_page_to_task_dict(task) for task in pages_in_database_list][:10]
