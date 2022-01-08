import notion_client

from .models import RecurringTask
from notion_database.service import query_user_notion_database_by_id

import logging

logger = logging.getLogger(__name__)


def create_recurring_task_in_notion(task_pk):
    try:
        task_model = RecurringTask.objects.all().filter(pk=task_pk)[0]
    except IndexError:
        raise Exception(f'Task with id {task_pk} be created because it did not exist in Database anymore.')
    user = task_model.owner
    workspace_access_queryset = user.workspace_access.all()
    if workspace_access_queryset.count is 0:
        raise Exception('User did not have a workspace access.')
    try:
        client = notion_client.Client(auth=list(workspace_access_queryset)[0].access_token)
    except IndexError:
        logger.error("User did not have a workspace access")
        raise Exception('User did not have a workspace access.')
    # TODO: Logic
    # Fetch the given database from Notion
    database_dict = query_user_notion_database_by_id(user_model=user, database_id_str=task_model.database_id)
    # Check which properties are still in the Database
    notion_database_property_id_set = set([property_container.id for property_container in database_dict['properties']])

    properties_to_add_dict = [property_dict for property_dict in task_model.properties_json
                              if property_dict.id in notion_database_property_id_set]
    # Convert some fields into their notion values
        # Checkbox

        # Select/Multi Select
    # Call the create Notion Page Method
    logger.debug(f'Created recurring task with id {task_model.pk} successfully.')
