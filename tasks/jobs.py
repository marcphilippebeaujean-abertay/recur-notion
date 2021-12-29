import notion_client

from .models import RecurringTask

import logging

logger = logging.getLogger(__name__)


def create_recurring_task_in_notion(task_pk):
    try:
        task_model = RecurringTask.objects.all().filter(pk=task_pk)[0]
    except IndexError:
        logger.error("Task that was created did not exist in Database anymore")
        raise Exception('Task could not be created because it did not exist in Database anymore.')
    user = task_model.owner
    workspace_access_queryset = user.workspace_access.all()
    if workspace_access_queryset.count is 0:
        raise Exception('User did not have a workspace access.')
    try:
        client = notion_client.Client(auth=list(workspace_access_queryset)[0].access_token)
    except IndexError:
        logger.error("User did not have a workspace access")
        raise Exception('User did not have a workspace access.')
    notion_page_resp_dict = client.pages.retrieve(task_model.cloned_task_notion_id)
    page_properties_dict = notion_page_resp_dict['properties']
    parent_database_dict = {'database_id': task_model.database_id}
    client.pages.create(properties=page_properties_dict, parent=parent_database_dict)
    logger.debug(f'Created recurring task with id{task_model.cloned_task_notion_id}')
