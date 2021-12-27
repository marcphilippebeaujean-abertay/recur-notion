from notion_client import Client

from workspaces.models import NotionWorkspaceAccess

import logging
import pytz
from datetime import date, datetime, timezone

# Get an instance of a logger
logger = logging.getLogger(__name__)


class NotionApiException(Exception):
    pass


class RecurringTaskNotFound(Exception):
    pass


class RecurringTaskBadFormData(Exception):
    pass


def fetch_notion_workspace_pages_and_convert_to_task_dict(user_model, query_string):
    logger.info(f'Fetching workspace pages')
    notion_workspace_access_grant_model = NotionWorkspaceAccess.objects.filter(owner=user_model).first()
    if notion_workspace_access_grant_model is None:
        raise NotionApiException(f'User {user_model.username} does not have any access grants!')

    logger.info(f'Fetching Notion Pages with Access Token {notion_workspace_access_grant_model.access_token}')
    client = Client(auth=notion_workspace_access_grant_model.access_token)
    request_filter_dict = {"filter": {"property": "object", "value": "page"}, "page_size": 20}
    if query_string is not None and len(query_string) > 0:
        request_filter_dict['query'] = query_string
    api_response_object_dict_list = client.search(**request_filter_dict).get("results")

    api_resp_non_pages_filtered = [api_object_dict for api_object_dict in api_response_object_dict_list
                                   if api_object_dict['object'] == 'page']

    is_page_in_database = lambda page_dict: 'parent' in page_dict and page_dict['parent']['type'] == 'database_id'
    pages_in_database_list = [task for task in api_resp_non_pages_filtered if is_page_in_database(task)]

    all_user_recurring_tasks_list = list(user_model.tasks.all())
    recurring_task_by_notion_task_id_dict = {}

    for recurring_task in all_user_recurring_tasks_list:
        recurring_task_list = recurring_task_by_notion_task_id_dict.get(recurring_task.cloned_task_notion_id, [])
        recurring_task_list.append(recurring_task)
        recurring_task_by_notion_task_id_dict[recurring_task.cloned_task_notion_id] = recurring_task_list

    return [convert_api_page_response_dict_to_task_dict(page_dict=page_dict,
                                                        recurring_task_by_notion_task_id_dict=recurring_task_by_notion_task_id_dict)
            for page_dict in pages_in_database_list][:10]


def convert_api_page_response_dict_to_task_dict(page_dict, recurring_task_by_notion_task_id_dict):
    task_title_string = 'Invalid Name'
    properties_dict = page_dict['properties']
    for key in properties_dict:
        property_info_dict = properties_dict[key]
        if 'title' in property_info_dict['type']:
            task_title_string = property_info_dict['title'][0]['plain_text']
    return {
        'title': task_title_string,
        'id': page_dict['id'],
        'url': page_dict['url'],
        'db_id': page_dict['parent']['database_id'],
        'recurring_tasks': recurring_task_by_notion_task_id_dict.get(page_dict['id'], [])
    }


def update_recurring_task_from_request_data(request_dict, task_pk):
    try:
        recurring_task_to_update_model = request_dict.user.tasks.all().filter(pk=task_pk)[0]
    except IndexError:
        raise RecurringTaskNotFound()
    if 'interval' in request_dict.POST:
        recurring_task_to_update_model.interval = request_dict.POST['interval']
    elif 'start-time' in request_dict.POST and 'client-timezone' in request_dict.POST:
        # this variable format is probably breaking the template
        user_unlocalized_start_datetime = datetime.strptime(request_dict.POST['start-time'], '%Y-%m-%dT%H:%M')
        # convert from client local timezone to UTC
        user_timezone = pytz.timezone(request_dict.POST['client-timezone'])
        localized_user_start_datetime = user_timezone.localize(user_unlocalized_start_datetime)
        # localize back to UTC
        start_date_utc_datetime = datetime.fromtimestamp(localized_user_start_datetime.timestamp(), tz=timezone.utc)
        recurring_task_to_update_model.start_date = start_date_utc_datetime
    else:
        raise RecurringTaskBadFormData()
    recurring_task_to_update_model.save()
    return recurring_task_to_update_model
