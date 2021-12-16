from notion_client import Client

from workspaces.models import NotionWorkspaceAccess


class NotionApiException(Exception):
    pass


def fetch_tasks_for_notion_workspace(user, query):
    notion_workspace_access_grant = NotionWorkspaceAccess.objects.filter(owner=user).first()
    if notion_workspace_access_grant is None:
        raise NotionApiException(f'User {user.username} does not have any access grants!')
    client = Client(auth=notion_workspace_access_grant.access_token)
    request_filter_dict = {"filter": {"property": "object", "value": "page"}, "page_size": 20}
    if query is not None and len(query) > 0:
        request_filter_dict['query'] = query
    response = client.search(**request_filter_dict).get("results")
    api_resp_non_pages_filtered = [api_object for api_object in response if api_object_is_normal_page(api_object)]
    api_page_with_database = [task for task in api_resp_non_pages_filtered if page_has_a_database_assigned(task)]
    return [convert_api_page_to_task_object_for_rendering(task) for task in api_page_with_database][:10]


def page_has_a_database_assigned(api_page):
    return 'parent' in api_page and api_page['parent']['type'] == 'database_id'


def api_object_is_normal_page(api_page):
    return 'properties' in api_page and 'Name' in api_page['properties']


def convert_api_page_to_task_object_for_rendering(api_task):
    return {
        'title': api_task['properties']['Name']['title'][0]['plain_text'],
        'id': api_task['id'],
        'url': api_task['url'],
        'db_id': api_task['parent']['database_id']
    }
