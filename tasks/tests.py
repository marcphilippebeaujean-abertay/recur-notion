import json

import pytz
from datetime import date, datetime, timezone, timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from django_q.models import Schedule

from workspaces.models import NotionWorkspace, NotionWorkspaceAccess
from .models import RecurringTask
from .jobs import create_recurring_task_in_notion

from .notion_api_mock import VALID_DATABASE_ID, VALID_ACCESS_TOKEN, EXAMPLE_API_REQUEST,\
    create_or_get_mocked_oauth_notion_client

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
        task = RecurringTask.objects.create(interval=RecurringTask.TaskIntervals.EVERY_DAY.value,
                                            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME - timedelta(days=1),
                                            owner=self.user,
                                            properties_json=json.loads(EXAMPLE_API_REQUEST)['properties'],
                                            database_id=VALID_DATABASE_ID)
        # run the tasks method
        create_recurring_task_in_notion(task.pk)
        m.assert_called_once_with(auth=VALID_ACCESS_TOKEN)

    @mock.patch('tasks.jobs.notion_client.Client', side_effect=create_or_get_mocked_oauth_notion_client)
    def test_no_scheduled_task_in_database_throws_exception(self, m):
        # create new recurring task
        task = RecurringTask.objects.create(interval=RecurringTask.TaskIntervals.EVERY_7_DAYS.value,
                                            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME - timedelta(days=3),
                                            owner=self.user,
                                            properties_json=json.loads(EXAMPLE_API_REQUEST)['properties'],
                                            database_id=VALID_DATABASE_ID)
        # run the tasks method
        self.assertRaises(Exception, lambda x: create_recurring_task_in_notion('invalid_pk'))

    @mock.patch('tasks.jobs.notion_client.Client', side_effect=create_or_get_mocked_oauth_notion_client)
    def test_no_workspace_access_in_database_throws_exception(self, m):
        # create new recurring task
        task = RecurringTask.objects.create(interval=RecurringTask.TaskIntervals.EVERY_7_DAYS.value,
                                            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME - timedelta(days=7),
                                            owner=self.user,
                                            properties_json=json.loads(EXAMPLE_API_REQUEST)['properties'],
                                            database_id=VALID_DATABASE_ID)
        NotionWorkspaceAccess.objects.all().delete()
        # run the tasks method
        self.assertRaises(Exception, lambda x: create_recurring_task_in_notion(task.pk))


class TestDateUntilPreview(TasksTestCase):

    def test_1_day_till_posted_over_1_day_interval(self):
        # create new recurring task
        task = RecurringTask.objects.create(interval=RecurringTask.TaskIntervals.EVERY_DAY.value,
                                            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME - timedelta(days=7),
                                            owner=self.user,
                                            database_id=VALID_DATABASE_ID)
        self.assertEqual(task.days_till_next_task, 1)

    def test_1_day_till_posted_over_7_day_interval(self):
        # create new recurring task
        task = RecurringTask.objects.create(interval=RecurringTask.TaskIntervals.EVERY_7_DAYS.value,
                                            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME - timedelta(days=6),
                                            owner=self.user,
                                            database_id=VALID_DATABASE_ID)
        self.assertEqual(task.days_till_next_task, 1)


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
        self.assertEqual(created_recurring_task.name, 'New Recurring Task')
        self.assertEqual(created_recurring_task.owner, self.user)
        self.assertEqual(Schedule.objects.count(), 1)

    def assert_task_was_not_created(self):
        self.assertEqual(RecurringTask.objects.count(), 0)

    def test_logged_in_user_successfully_create_recurring_tasks(self):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.post('/create-recurring-task/', self.create_payload)
        self.assertEqual(response.status_code, 302)
        self.assert_task_was_created()

    def test_create_recurring_task_requires_post_method(self):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.patch('/create-recurring-task/', self.create_payload)
        self.assertEqual(response.status_code, 405)
        self.assert_task_was_not_created()

    def test_create_recurring_task_also_creates_djangoq_scheduler(self):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.post('/create-recurring-task/', self.create_payload)
        self.assertEqual(response.status_code, 302)
        self.assert_task_was_created()
        scheduled_job = Schedule.objects.all()[0]
        self.assertTrue(scheduled_job.next_run.timestamp() - (datetime.now() + timedelta(days=1)).timestamp() < 1000)
        self.assertEqual(scheduled_job.schedule_type, Schedule.DAILY)


class TestUpdateRecurringTasks(TasksTestCase):

    def setUp(self):
        super().setUp()
        self.recurring_test_task_model = RecurringTask.objects.create(
            interval=RecurringTask.TaskIntervals.EVERY_DAY.value,
            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME,
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

    def assert_task_was_not_created(self):
        self.assertEqual(RecurringTask.objects.count(), 1)

    def assert_task_start_time_was_updated(self):
        test_unlocalized_start_datetime = datetime.strptime('2021-12-14T09:30', '%Y-%m-%dT%H:%M')
        test_timezone = pytz.timezone('Europe/Berlin')
        localized_user_start_datetime = test_timezone.localize(test_unlocalized_start_datetime)
        test_update_start_date_utc_datetime = datetime.fromtimestamp(localized_user_start_datetime.timestamp(),
                                                                     tz=timezone.utc)
        recurring_task_from_db = RecurringTask.objects.all()[0]
        self.assertEqual(recurring_task_from_db.start_time, test_update_start_date_utc_datetime)

    def check_task_was_not_updated(self):
        recurring_task_from_db = RecurringTask.objects.all()[0]
        self.assertEqual(recurring_task_from_db.interval, '1')
        self.assertEqual(recurring_task_from_db.start_time, DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME)
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
            interval=RecurringTask.TaskIntervals.EVERY_DAY.value,
            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME,
            owner=get_user_model().objects.create_user(
                username='testuser2',
                email='test2@email.com',
                password='secret'
            ),
            database_id=VALID_DATABASE_ID
        )
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.post(f'/update-recurring-task/{other_user_recurring_task.pk}',
                                    self.update_start_time_payload)
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

    def test_logged_in_user_successfully_updates_interval(self):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.post(self.request_url, self.update_interval_payload)
        self.assertEqual(response.status_code, 200)
        self.assert_task_was_not_created()
        recurring_task = RecurringTask.objects.all()[0]
        self.assertEqual(recurring_task.interval, self.update_interval_payload['interval'][0])

    def test_logged_in_user_successfully_updates_start_time(self):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.post(self.request_url, self.update_start_time_payload)
        self.assertEqual(response.status_code, 200)

    def test_scheduled_task_start_time_same_as_recurring_task_start_time(self):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.post(self.request_url, self.update_start_time_payload)
        self.assertEqual(response.status_code, 200)
        schedule_task = Schedule.objects.all()[0]
        recurring_task = RecurringTask.objects.all()[0]
        self.assert_task_start_time_was_updated()
        self.assertEqual(recurring_task.start_time, schedule_task.next_run)


class TestDeleteRecurringTask(TasksTestCase):
    def setUp(self):
        super().setUp()
        self.recurring_test_task_model = RecurringTask.objects.create(
            interval=RecurringTask.TaskIntervals.EVERY_DAY.value,
            owner=self.user,
            database_id=VALID_DATABASE_ID
        )
        self.request_url = f'/delete-recurring-task/{self.recurring_test_task_model.pk}'

    def assert_task_deleted(self):
        self.assertEqual(RecurringTask.objects.count(), 0)

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
        self.assert_task_not_deleted()

    def test_require_delete_method_for_delete(self):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.post(self.request_url)
        self.assertEqual(response.status_code, 405)
        self.assert_task_not_deleted()

    def test_throw_not_found_when_delete(self):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.delete('/delete-recurring-task/invalid-id')
        self.assertEqual(response.status_code, 404)
        self.assert_task_not_deleted()

    def test_cannot_delete_other_users_tasks_settings(self):
        other_user_recurring_task = RecurringTask.objects.create(
            interval=RecurringTask.TaskIntervals.EVERY_DAY.value,
            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME,
            owner=get_user_model().objects.create_user(
                username='testuser2',
                email='test2@email.com',
                password='secret'
            ),
            database_id=VALID_DATABASE_ID
        )
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.delete(f'/delete-recurring-task/{other_user_recurring_task.pk}')
        self.assertEqual(response.status_code, 404)

    def test_delete_also_removes_scheduler_task(self):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.delete(self.request_url)
        self.assertEqual(response.status_code, 200)
        self.assert_task_deleted()
        self.assertEqual(Schedule.objects.count(), 0)


class TestWorkspaceQuery(TasksTestCase):
    ## TODO: Create all tasks when update is there
    pass
