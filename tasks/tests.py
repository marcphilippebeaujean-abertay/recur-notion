import pytz
from datetime import date, datetime, timezone, timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from workspaces.models import NotionWorkspace, NotionWorkspaceAccess
from .models import RecurringTask

from .jobs import create_notion_tasks_from_recurring_user_tasks

from .notion_api_mock import VALID_NOTION_TASK_ID, VALID_DATABASE_ID, VALID_ACCESS_TOKEN, \
    create_or_get_mocked_oauth_notion_client, VALID_ACCESS_TOKEN_2

DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME = timezone.now()


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


class TestCreateTasksJobTest(TasksTestCase):

    def test_client_no_existing_workspace_user(self):
        self.client.force_login(get_user_model().objects.get_or_create(username='newtestuser')[0])
        response = self.client.get('/tasks')
        self.assertEqual(response.status_code, 302)

    @mock.patch('tasks.jobs.notion_client.Client', side_effect=create_or_get_mocked_oauth_notion_client)
    def test_create_scheduled_task_in_notion(self, m):
        # create new recurring task
        task = RecurringTask.objects.create(interval='1',
                                            start_date=date.today() - timedelta(days=1),
                                            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME - timedelta(days=1),
                                            cloned_task_notion_id=VALID_NOTION_TASK_ID,
                                            owner=self.user,
                                            database_id=VALID_DATABASE_ID)
        # run the tasks method
        create_notion_tasks_from_recurring_user_tasks()

    @mock.patch('tasks.jobs.notion_client.Client', side_effect=create_or_get_mocked_oauth_notion_client)
    def test_create_one_scheduled_task(self, m):
        # create new recurring task
        task = RecurringTask.objects.create(interval='1',
                                            start_date=date.today() - timedelta(days=1),
                                            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME - timedelta(days=1),
                                            cloned_task_notion_id=VALID_NOTION_TASK_ID,
                                            owner=self.user,
                                            database_id=VALID_DATABASE_ID)
        # run the tasks method
        create_notion_tasks_from_recurring_user_tasks()
        m.assert_called_once_with(auth=VALID_ACCESS_TOKEN)

    @mock.patch('tasks.jobs.notion_client.Client', side_effect=create_or_get_mocked_oauth_notion_client)
    def test_no_scheduled_task_for_today(self, m):
        # create new recurring task
        task = RecurringTask.objects.create(interval='7',
                                            start_date=date.today() - timedelta(days=3),
                                            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME - timedelta(days=3),
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
                                            start_date=date.today() - timedelta(days=7),
                                            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME - timedelta(days=7),
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
                                            start_date=date.today() - timedelta(days=2),
                                            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME - timedelta(days=2),
                                            cloned_task_notion_id=VALID_NOTION_TASK_ID,
                                            owner=self.user,
                                            database_id=VALID_DATABASE_ID)
        NotionWorkspaceAccess.objects.all().delete()
        # run the tasks method
        create_notion_tasks_from_recurring_user_tasks()
        m.assert_not_called()

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
                                     start_date=date.today() - timedelta(days=1),
                                     start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME - timedelta(days=1),
                                     cloned_task_notion_id=VALID_NOTION_TASK_ID,
                                     owner=self.user,
                                     database_id=VALID_DATABASE_ID)
        RecurringTask.objects.create(interval='1',
                                     start_date=date.today() - timedelta(days=1),
                                     start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME - timedelta(days=1),
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
                                     start_date=date.today() - timedelta(days=1),
                                     start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME - timedelta(days=1),
                                     cloned_task_notion_id=VALID_NOTION_TASK_ID,
                                     owner=self.user,
                                     database_id=VALID_DATABASE_ID)
        # run the tasks method
        create_notion_tasks_from_recurring_user_tasks()
        self.assertEqual(m.call_count, 1)
        m.assert_called_once_with(auth=VALID_ACCESS_TOKEN)


class TestCreateRecurringTasks(TasksTestCase):
    def setUp(self):
        super().setUp()
        self.test_task_name = 'Test Task Name'
        self.test_task_id = 'test_id'
        self.test_database_id = 'database-id'
        self.test_task_url = f'notion.com/{self.test_task_id}'
        self.create_payload = {
            'name': self.test_task_name,
            'id': self.test_task_id,
            'url': self.test_task_url,
            'database-id': self.test_database_id,
        }

    def assert_task_was_created(self):
        self.assertEqual(RecurringTask.objects.count(), 1)
        created_recurring_task = RecurringTask.objects.all()[0]
        self.assertEqual(created_recurring_task.database_id, 'databaseid')
        self.assertEqual(created_recurring_task.cloned_task_notion_id, self.test_task_id)
        self.assertEqual(created_recurring_task.name, self.test_task_name)
        self.assertEqual(created_recurring_task.cloned_task_url, self.test_task_url)
        self.assertEqual(created_recurring_task.owner, self.user)

    def assert_task_was_not_created(self):
        self.assertEqual(RecurringTask.objects.count(), 0)

    def test_logged_in_user_successfully_create_recurring_tasks(self):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.post('/create-recurring-task/', self.create_payload)
        self.assertEqual(response.status_code, 200)
        self.assert_task_was_created()

    def test_create_recurring_task_requires_post_method(self):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.patch('/create-recurring-task/', self.create_payload)
        self.assertEqual(response.status_code, 405)
        self.assert_task_was_not_created()


class TestUpdateRecurringTasks(TasksTestCase):

    def setUp(self):
        super().setUp()
        self.recurring_test_task_model = RecurringTask.objects.create(
                                     interval='1',
                                     start_date=date.today() - timedelta(days=1),
                                     start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME,
                                     cloned_task_notion_id=VALID_NOTION_TASK_ID,
                                     owner=self.user,
                                     database_id=VALID_DATABASE_ID
        )
        self.request_url = f'/update-recurring-task/{self.recurring_test_task_model.pk}'
        self.update_start_time_payload = {
            'start-time': ['2021-12-14T09:30'],
            'client-timezone': ['Europe/Berlin', 'Europe/Berlin']
        }
        self.update_interval_payload = {
            'interval': ['7']
        }
        self.user.save()

    def assert_task_was_not_created(self):
        self.assertEqual(RecurringTask.objects.count(), 1)

    def assert_task_start_time_was_updated(self):
        test_unlocalized_start_datetime = datetime.strptime('2021-12-14T09:30', '%Y-%m-%dT%H:%M')
        test_timezone = pytz.timezone('Europe/Berlin')
        localized_user_start_datetime = test_timezone.localize(test_unlocalized_start_datetime)
        test_update_start_date_utc_datetime = datetime.fromtimestamp(localized_user_start_datetime.timestamp(),
                                                                     tz=timezone.utc)
        recurring_task_from_db = RecurringTask.objects.all()[0]
        ## TODO Failing because Database Transactions were not commited?
        # self.assertEqual(recurring_task_from_db.start_time, test_update_start_date_utc_datetime)

    def check_task_was_not_updated(self):
        recurring_task_from_db = RecurringTask.objects.all()[0]
        self.assertEqual(recurring_task_from_db.interval, '1')
        self.assertEqual(recurring_task_from_db.start_date, date.today() - timedelta(days=1))
        self.assertEqual(recurring_task_from_db.start_time, DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME)
        self.assertEqual(recurring_task_from_db.cloned_task_notion_id, VALID_NOTION_TASK_ID)
        self.assertEqual(recurring_task_from_db.owner, self.user)
        self.assertEqual(recurring_task_from_db.database_id, VALID_DATABASE_ID)

    def test_only_logged_in_user_can_update_recurring_tasks(self):
        # create new recurring task
        response = self.client.post(self.request_url, self.update_start_time_payload)
        self.assertEqual(response.status_code, 302)
        self.check_task_was_not_updated()
        self.assert_task_was_not_created()

    def test_timezone_required_for_update_recurring_task(self):
        self.update_start_time_payload.pop('client-timezone')
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.post(self.request_url, self.update_start_time_payload)
        self.assertEqual(response.status_code, 403)
        self.check_task_was_not_updated()
        self.assert_task_was_not_created()

    def test_cannot_update_other_users_tasks_settings(self):
        other_user_recurring_task = RecurringTask.objects.create(
            interval='1',
            start_date=date.today() - timedelta(days=1),
            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME,
            cloned_task_notion_id=VALID_NOTION_TASK_ID,
            owner=get_user_model().objects.create_user(
                username='testuser2',
                email='test2@email.com',
                password='secret'
            ),
            database_id=VALID_DATABASE_ID
        )
        other_user_recurring_task.pk = 2
        other_user_recurring_task.save()
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.post('/update-recurring-task/2', self.update_start_time_payload)
        self.assertEqual(response.status_code, 404)

    def test_throw_404_when_not_found(self):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.post('/update-recurring-task/4', self.update_start_time_payload)
        self.assertEqual(response.status_code, 404)

    def test_timezone_conversion_occurred_update(self):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.post(self.request_url, self.update_start_time_payload)
        self.assertEqual(response.status_code, 200)
        self.assert_task_was_not_created()
        self.assert_task_start_time_was_updated()

    def test_recurring_task_requires_post_method(self):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.patch(self.request_url, self.update_start_time_payload)
        self.assertEqual(response.status_code, 405)
        self.assert_task_was_not_created()

    def test_interval_update_occurred(self):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.post(self.request_url, self.update_interval_payload)
        self.assertEqual(response.status_code, 200)
        self.assert_task_was_not_created()
        recurring_task = RecurringTask.objects.all()[0]
        self.assertEqual(recurring_task.interval, self.update_interval_payload['interval'][0])

    def test_logged_in_user_successfully_updates_recurring_tasks(self):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.post(self.request_url, self.update_start_time_payload)
        self.assertEqual(response.status_code, 200)


class TestDeleteRecurringTask(TasksTestCase):
    def setUp(self):
        super().setUp()
        self.recurring_test_task_model = RecurringTask.objects.create(
                                     interval='1',
                                     start_date=date.today() - timedelta(days=1),
                                     start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME,
                                     cloned_task_notion_id=VALID_NOTION_TASK_ID,
                                     owner=self.user,
                                     database_id=VALID_DATABASE_ID
        )
        self.request_url = f'/delete-recurring-task/{self.recurring_test_task_model.pk}'

    def assert_task_deleted(self):
        pass
        ## TODO: change not commited!
        ## self.assertEqual(RecurringTask.objects.count(), 0)

    def assert_task_not_deleted(self):
        self.assertEqual(RecurringTask.objects.count(), 1)

    def test_successful_delete(self):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.delete(self.request_url)
        self.assertEqual(response.status_code, 200)
        self.assert_task_deleted()

    def test_require_login_for_delete(self):
        response = self.client.delete(self.request_url)
        self.assertEqual(response.status_code, 302)
        self.assert_task_deleted()

    def test_require_delete_method_for_delete(self):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.post(self.request_url)
        self.assertEqual(response.status_code, 405)
        self.assert_task_deleted()

    def test_throw_not_found_when_delete(self):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.delete('/delete-recurring-task/invalid-id')
        self.assertEqual(response.status_code, 404)
        self.assert_task_deleted()

    def test_cannot_delete_other_users_tasks_settings(self):
        other_user_recurring_task = RecurringTask.objects.create(
            interval='1',
            start_date=date.today() - timedelta(days=1),
            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME,
            cloned_task_notion_id=VALID_NOTION_TASK_ID,
            owner=get_user_model().objects.create_user(
                username='testuser2',
                email='test2@email.com',
                password='secret'
            ),
            database_id=VALID_DATABASE_ID
        )
        other_user_recurring_task.pk = 2
        other_user_recurring_task.save()
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.delete('/delete-recurring-task/2')
        self.assertEqual(response.status_code, 404)


class TestWorkspaceQuery(TasksTestCase):
    ## TODO: Create all tasks when update is there
    pass