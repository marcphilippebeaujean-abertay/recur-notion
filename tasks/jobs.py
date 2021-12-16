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
        for task in tasks_to_create:
            client = notion_client.Client(auth=list(user.workspace_access.all())[0].access_token)
            try:
                notion_page_resp = client.pages.retrieve(task.cloned_task_notion_id)
                client.pages.create(properties=notion_page_resp['properties'], parent={
                    'database_id': task.database_id
                })
                logger.debug(f'Created recurring task with id{task.cloned_task_notion_id}')
            except APIResponseError as error:
                logger.debug("API Error occurred accessing Notion!")
