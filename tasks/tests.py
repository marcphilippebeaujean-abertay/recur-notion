import datetime
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from workspaces.models import NotionWorkspace, NotionWorkspaceAccess
from .models import RecurringTask

from .jobs import create_notion_tasks_from_recurring_user_tasks

from .notion_api_mock import VALID_NOTION_TASK_ID, VALID_DATABASE_ID, VALID_ACCESS_TOKEN, \
    create_or_get_mocked_oauth_notion_client, VALID_ACCESS_TOKEN_2


class TasksTestCase(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email.com',
            password='secret'
        )
        self.init_workspace = NotionWorkspace.objects.create(
            name='WORKSPACE_NAME',
            notion_id='WORKSPACE_ID',
            icon_url='icon.svg'
        )
        self.init_workspace_access = NotionWorkspaceAccess.objects.create(
            access_token=VALID_ACCESS_TOKEN,
            workspace=self.init_workspace,
            owner=self.user
        )

    def test_client_no_existing_workspace_user(self):
        self.client.force_login(get_user_model().objects.get_or_create(username='newtestuser')[0])
        response = self.client.get('/tasks')
        self.assertEqual(response.status_code, 302)

    @mock.patch('tasks.jobs.notion_client.Client', side_effect=create_or_get_mocked_oauth_notion_client)
    def test_create_scheduled_task_in_notion(self, m):
        # create new recurring task
        task = RecurringTask.objects.create(interval='1',
                                            start_date=datetime.date.today() - datetime.timedelta(days=1),
                                            cloned_task_notion_id=VALID_NOTION_TASK_ID,
                                            owner=self.user,
                                            database_id=VALID_DATABASE_ID)
        # run the tasks method
        create_notion_tasks_from_recurring_user_tasks()

    @mock.patch('tasks.jobs.notion_client.Client', side_effect=create_or_get_mocked_oauth_notion_client)
    def test_create_one_scheduled_task(self, m):
        # create new recurring task
        task = RecurringTask.objects.create(interval='1',
                                            start_date=datetime.date.today() - datetime.timedelta(days=1),
                                            cloned_task_notion_id=VALID_NOTION_TASK_ID,
                                            owner=self.user,
                                            database_id=VALID_DATABASE_ID)
        # run the tasks method
        create_notion_tasks_from_recurring_user_tasks()
        m.assert_called_once_with(auth=VALID_ACCESS_TOKEN)

    @mock.patch('tasks.jobs.notion_client.Client', side_effect=create_or_get_mocked_oauth_notion_client)
    def test_no_scheduled_task_for_today(self, m):
        # create new recurring task
        task = RecurringTask.objects.create(interval='1',
                                            start_date=datetime.date.today() - datetime.timedelta(days=2),
                                            cloned_task_notion_id=VALID_NOTION_TASK_ID,
                                            owner=self.user,
                                            database_id=VALID_DATABASE_ID)
        # run the tasks method
        create_notion_tasks_from_recurring_user_tasks()
        m.assert_not_called()

    @mock.patch('tasks.jobs.notion_client.Client', side_effect=create_or_get_mocked_oauth_notion_client)
    def test_create_scheduled_task_from_one_week_ago(self, m):
        # create new recurring task
        task = RecurringTask.objects.create(interval='7',
                                            start_date=datetime.date.today() - datetime.timedelta(days=7),
                                            cloned_task_notion_id=VALID_NOTION_TASK_ID,
                                            owner=self.user,
                                            database_id=VALID_DATABASE_ID)
        # run the tasks method
        create_notion_tasks_from_recurring_user_tasks()
        m.assert_called_once_with(auth=VALID_ACCESS_TOKEN)

    @mock.patch('tasks.jobs.notion_client.Client', side_effect=create_or_get_mocked_oauth_notion_client)
    def test_user_has_no_recurring_tasks(self, m):
        # run the tasks method
        create_notion_tasks_from_recurring_user_tasks()
        m.assert_not_called()

    @mock.patch('tasks.jobs.notion_client.Client', side_effect=create_or_get_mocked_oauth_notion_client)
    def test_user_has_no_workspace_access(self, m):
        # create new recurring task
        task = RecurringTask.objects.create(interval='1',
                                            start_date=datetime.date.today() - datetime.timedelta(days=2),
                                            cloned_task_notion_id=VALID_NOTION_TASK_ID,
                                            owner=self.user,
                                            database_id=VALID_DATABASE_ID)
        NotionWorkspaceAccess.objects.all().delete()
        # run the tasks method
        create_notion_tasks_from_recurring_user_tasks()
        m.assert_called_once_with()

    @mock.patch('tasks.jobs.notion_client.Client', side_effect=create_or_get_mocked_oauth_notion_client)
    def test_two_users_scheduled_tasks_for_today(self, m):
        new_user = get_user_model().objects.create_user(
            username='testuser2',
            email='test2@email.com',
            password='secret'
        )
        new_workspace = NotionWorkspace.objects.create(
            name='WORKSPACE_NAME2',
            notion_id='WORKSPACE_ID2',
            icon_url='icon.svg'
        )
        new_workspace_access = NotionWorkspaceAccess.objects.create(
            access_token=VALID_ACCESS_TOKEN_2,
            workspace=new_workspace,
            owner=new_user
        )
        # create new recurring task
        RecurringTask.objects.create(interval='1',
                                     start_date=datetime.date.today() - datetime.timedelta(days=1),
                                     cloned_task_notion_id=VALID_NOTION_TASK_ID,
                                     owner=self.user,
                                     database_id=VALID_DATABASE_ID)
        RecurringTask.objects.create(interval='1',
                                     start_date=datetime.date.today() - datetime.timedelta(days=1),
                                     cloned_task_notion_id=VALID_NOTION_TASK_ID,
                                     owner=new_user,
                                     database_id=VALID_DATABASE_ID)
        # run the tasks method
        create_notion_tasks_from_recurring_user_tasks()
        self.assertEqual(m.call_count, 2)

    @mock.patch('tasks.jobs.notion_client.Client', side_effect=create_or_get_mocked_oauth_notion_client)
    def test_two_users_scheduled_one_has_no_tasks(self, m):
        new_user = get_user_model().objects.create_user(
            username='testuser2',
            email='test2@email.com',
            password='secret'
        )
        new_workspace = NotionWorkspace.objects.create(
            name='WORKSPACE_NAME2',
            notion_id='WORKSPACE_ID2',
            icon_url='icon.svg'
        )
        new_workspace_access = NotionWorkspaceAccess.objects.create(
            access_token=VALID_ACCESS_TOKEN_2,
            workspace=new_workspace,
            owner=new_user
        )
        # create new recurring task
        RecurringTask.objects.create(interval='1',
                                     start_date=datetime.date.today() - datetime.timedelta(days=1),
                                     cloned_task_notion_id=VALID_NOTION_TASK_ID,
                                     owner=self.user,
                                     database_id=VALID_DATABASE_ID)
        # run the tasks method
        create_notion_tasks_from_recurring_user_tasks()
        self.assertEqual(m.call_count, 1)
        m.assert_called_once_with(auth=VALID_ACCESS_TOKEN)
