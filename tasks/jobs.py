import notion_client
from notion_client import APIResponseError

from accounts.models import CustomUser

import logging

logger = logging.getLogger(__name__)


def create_notion_tasks_from_recurring_user_tasks():
    logger.info("Creating all scheduled tasks...")
    users = CustomUser.objects.filter(workspace_access__isnull=False,
                                      workspace_access__access_token__isnull=False)
    for user in users:
        tasks_to_create = [task for task in list(user.tasks.all()) if task.should_create_task_today]
        workspace_access_queryset = user.workspace_access.all()
        if workspace_access_queryset.count is 0:
            continue
        for task in tasks_to_create:
            client = notion_client.Client(auth=list(workspace_access_queryset)[0].access_token)
            notion_page_resp_dict = client.pages.retrieve(task.cloned_task_notion_id)
            page_properties_dict = notion_page_resp_dict['properties']
            parent_database_dict = {'database_id': task.database_id}
            client.pages.create(properties=page_properties_dict, parent=parent_database_dict)
            logger.debug(f'Created recurring task with id{task.cloned_task_notion_id}')
