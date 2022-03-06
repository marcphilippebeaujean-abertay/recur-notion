from datetime import datetime, timedelta, timezone
from unittest import mock

import pytz
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django_q.models import Schedule

import notion_database.notion_mock_api as notion_db_mock
from notion_database.models import NotionDatabase
from notion_database.notion_mock_api import VALID_ACCESS_TOKEN, VALID_DATABASE_ID
from workspaces.models import NotionWorkspace, NotionWorkspaceAccess

from .jobs import create_recurring_task_in_notion
from .models import RecurringTask

DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME = timezone.now()

CATEGORY_FIELD_ID = "epmG"
EXAMPLE_NOTION_PROPERTIES = [
    {
        "id": "_jFX",
        "name": "Mail",
        "type": "email",
        "value": "cali@gmail.com",
        "options": [],
    },
    # TODO: Support date
    # {
    #    "id": "Fq%3Ar",
    #    "name": "Deadline",
    #    "type": "date",
    #    "value": "2022-01-11T19:12:39+00:00",
    #    "options": [],
    # },
    {
        "id": "s%60lY",
        "name": "Phone Number",
        "type": "phone_number",
        "value": "12456",
        "options": [],
    },
    {"id": "g%3Cjh", "name": "Nr", "type": "number", "value": 3.3, "options": []},
    {
        "id": "s%60lddfY",
        "name": "None Existing Property",
        "type": "phone_number",
        "value": "12456",
        "options": [
            {
                "id": "a946e6f5-fa09-4d30-bb2e-ff91f639b77b",
                "name": "test1",
                "color": "green",
            },
            {
                "id": "7f7cce89-2594-40c8-8b8b-813c7cbf4f27",
                "name": "test2",
                "color": "red",
            },
        ],
    },
    {
        "id": "s%60lY",
        "name": "None Existing Property",
        "type": "none_existing_type",
        "value": "12456",
        "options": [
            {
                "id": "a946e6f5-fa09-4d30-bb2e-ff91f639b77b",
                "name": "test1",
                "color": "green",
            },
            {
                "id": "7f7cce89-2594-40c8-8b8b-813c7cbf4f27",
                "name": "test2",
                "color": "red",
            },
        ],
    },
    {
        "id": "%3E%5Dqm",
        "name": "Tags",
        "type": "multi_select",
        "value": "a946e6f5-fa09-4d30-bb2e-ff91f639b77b",
        "options": [
            {
                "id": "a946e6f5-fa09-4d30-bb2e-ff91f639b77b",
                "name": "test1",
                "color": "green",
            },
            {
                "id": "7f7cce89-2594-40c8-8b8b-813c7cbf4f27",
                "name": "test2",
                "color": "red",
            },
        ],
    },
    {
        "id": CATEGORY_FIELD_ID,
        "name": "Category",
        "type": "select",
        "value": "b7c6b95b-7142-4f0b-ad9c-a81b472503c6",
        "options": [
            {
                "id": "b7c6b95b-7142-4f0b-ad9c-a81b472503c6",
                "name": "test1",
                "color": "yellow",
            },
            {
                "id": "988be32c-6ec9-46fc-9665-d9e82dd8a96e",
                "name": "test2",
                "color": "yellow",
            },
        ],
    },
    # TODO: Support assigning
    # 'Assign': {
    #    'id': 'd%60Tf',
    #    'name': 'Assign',
    #    'type': 'people',
    #    'people': {}
    # },
    {
        "id": "atrI",
        "name": "URL",
        "type": "url",
        "options": [],
        "value": "http://helloworld.com",
    },
    {
        "id": "title",
        "name": "Name",
        "type": "title",
        "options": [],
        "value": "Rent",
    },
]


class TasksTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", email="test@email.com", password="secret"
        )
        self.init_workspace = NotionWorkspace.objects.create(
            name="WORKSPACE_NAME", notion_id="WORKSPACE_ID", icon_url="icon.svg"
        )
        self.init_workspace_access = NotionWorkspaceAccess.objects.create(
            access_token=VALID_ACCESS_TOKEN,
            workspace=self.init_workspace,
            owner=self.user,
        )
        self.sample_database = NotionDatabase.objects.create(
            database_id=VALID_DATABASE_ID, database_name="The Database"
        )


class TasksTestCalculateNextRun(TasksTestCase):
    def test_start_time_in_future(self):
        start_time_to_test_against = timezone.now() + timedelta(days=4)
        self.task = RecurringTask.objects.create(
            interval=RecurringTask.TaskIntervals.EVERY_DAY.value,
            start_time=start_time_to_test_against,
            owner=self.user,
            properties_json=EXAMPLE_NOTION_PROPERTIES,
            database=self.sample_database,
        )
        self.assertEqual(
            start_time_to_test_against, self.task.calculate_next_start_time_for_job()
        )

    def test_start_time_in_past(self):
        start_time = (
            datetime(
                year=timezone.now().year,
                month=timezone.now().month,
                minute=14,
                second=14,
                hour=timezone.now().hour - 1,
                day=timezone.now().day,
                tzinfo=pytz.utc,
            )
            - timedelta(days=3)
        )
        self.task = RecurringTask.objects.create(
            interval=RecurringTask.TaskIntervals.EVERY_DAY.value,
            start_time=start_time,
            owner=self.user,
            properties_json=EXAMPLE_NOTION_PROPERTIES,
            database=self.sample_database,
        )
        calculated_start_time = self.task.calculate_next_start_time_for_job()
        self.assertEqual(
            calculated_start_time.day, (timezone.now() + timedelta(days=1)).day
        )
        self.assertEqual(calculated_start_time.minute, 14)
        self.assertEqual(calculated_start_time.second, 14)
        self.assertEqual(
            calculated_start_time.hour, (timezone.now() - timedelta(hours=1)).hour
        )

    def test_start_time_in_past_but_daily_scheduling_means_should_post_today(self):
        start_time = (
            datetime(
                year=timezone.now().year,
                month=timezone.now().month,
                minute=14,
                second=14,
                hour=timezone.now().hour + 1,
                day=timezone.now().day - 1,
                tzinfo=pytz.utc,
            )
            - timedelta(days=3)
        )
        self.task = RecurringTask.objects.create(
            interval=RecurringTask.TaskIntervals.EVERY_DAY.value,
            start_time=start_time,
            owner=self.user,
            properties_json=EXAMPLE_NOTION_PROPERTIES,
            database=self.sample_database,
        )
        calculated_start_time = self.task.calculate_next_start_time_for_job()
        self.assertEqual(calculated_start_time.day, timezone.now().day)
        self.assertEqual(calculated_start_time.minute, 14)
        self.assertEqual(calculated_start_time.second, 14)
        self.assertEqual(calculated_start_time.hour, timezone.now().hour + 1)

    def test_interval_30_days(self):
        start_time = (
            datetime(
                year=timezone.now().year,
                month=timezone.now().month,
                minute=14,
                second=14,
                hour=timezone.now().hour - 1,
                day=timezone.now().day,
                tzinfo=pytz.utc,
            )
            - timedelta(days=3)
        )
        self.task = RecurringTask.objects.create(
            interval=RecurringTask.TaskIntervals.EVERY_30_DAYS.value,
            start_time=start_time,
            owner=self.user,
            properties_json=EXAMPLE_NOTION_PROPERTIES,
            database=self.sample_database,
        )
        calculated_start_time = self.task.calculate_next_start_time_for_job()
        self.assertEqual(
            calculated_start_time.day, (timezone.now() + timedelta(days=26)).day
        )
        self.assertEqual(calculated_start_time.minute, 14)
        self.assertEqual(calculated_start_time.second, 14)
        self.assertEqual(calculated_start_time.hour, timezone.now().hour - 1)

    def test_interval_7_days(self):
        start_time = (
            datetime(
                year=timezone.now().year,
                month=timezone.now().month,
                minute=14,
                second=14,
                hour=timezone.now().hour - 1,
                day=timezone.now().day,
                tzinfo=pytz.utc,
            )
            - timedelta(days=3)
        )
        self.task = RecurringTask.objects.create(
            interval=RecurringTask.TaskIntervals.EVERY_7_DAYS.value,
            start_time=start_time,
            owner=self.user,
            properties_json=EXAMPLE_NOTION_PROPERTIES,
            database=self.sample_database,
        )
        calculated_task_start_time = self.task.calculate_next_start_time_for_job()
        self.assertEqual(
            calculated_task_start_time.day, (timezone.now() + timedelta(days=3)).day
        )
        self.assertEqual(calculated_task_start_time.minute, 14)
        self.assertEqual(calculated_task_start_time.second, 14)
        self.assertEqual(calculated_task_start_time.hour, timezone.now().hour - 1)

    def test_interval_365_days(self):
        start_time = datetime(
            year=timezone.now().year,
            month=timezone.now().month,
            minute=14,
            second=14,
            hour=timezone.now().hour + 1,
            day=timezone.now().day,
            tzinfo=pytz.utc,
        )
        self.task = RecurringTask.objects.create(
            interval=RecurringTask.TaskIntervals.EVERY_365_DAYS.value,
            start_time=start_time,
            owner=self.user,
            properties_json=EXAMPLE_NOTION_PROPERTIES,
            database=self.sample_database,
        )

        self.assertEqual(
            self.task.calculate_next_start_time_for_job().day,
            (timezone.now() + timedelta(days=365)).day,
        )
        self.assertEqual(self.task.calculate_next_start_time_for_job().minute, 14)
        self.assertEqual(self.task.calculate_next_start_time_for_job().second, 14)
        self.assertEqual(
            self.task.calculate_next_start_time_for_job().hour, timezone.now().hour + 1
        )


class TestDateUntilPreview(TasksTestCase):
    def test_1_day_till_posted_over_1_day_interval(self):
        # create new recurring task
        task = RecurringTask.objects.create(
            interval=RecurringTask.TaskIntervals.EVERY_DAY.value,
            start_time=timezone.now() - timedelta(days=7),
            owner=self.user,
            database=self.sample_database,
        )
        self.assertEqual(task.days_till_next_task, 0)

    def test_1_day_till_posted_over_7_day_interval(self):
        # create new recurring task
        task = RecurringTask.objects.create(
            interval=RecurringTask.TaskIntervals.EVERY_7_DAYS.value,
            start_time=timezone.now() - timedelta(days=5, hours=6),
            owner=self.user,
            database=self.sample_database,
        )
        self.assertEqual(task.days_till_next_task, 1)


class TestCreateTasksJobTest(TasksTestCase):
    def setUp(self):
        super().setUp()
        # create new recurring task
        self.task = RecurringTask.objects.create(
            interval=RecurringTask.TaskIntervals.EVERY_DAY.value,
            start_time=timezone.now(),
            owner=self.user,
            properties_json=EXAMPLE_NOTION_PROPERTIES,
            database=self.sample_database,
        )

    def test_client_no_existing_workspace_user(self):
        self.client.force_login(
            get_user_model().objects.get_or_create(username="newtestuser")[0]
        )
        response = self.client.get("/tasks")
        self.assertEqual(response.status_code, 302)

    def test_create_scheduled_task_in_notion(self):
        # run the tasks method
        create_recurring_task_in_notion(self.task.pk)

    def test_create_scheduled_task_in_notion_despite_wrong_type_for_property(self):
        list_of_property_ids_to_change_back = []
        for property_dict in self.task.properties_json:
            if property_dict["type"] == "phone_number":
                property_dict["type"] = "multi_select"
                list_of_property_ids_to_change_back.append(property_dict["id"])
        self.task.save()
        # run the tasks method
        create_recurring_task_in_notion(self.task.pk)

    def test_invalid_option_id_in_recurring_task(self):
        properties_dict_list = self.task.properties_json
        for property_dict in properties_dict_list:
            if property_dict["type"] == "select":
                property_dict["value"] = "invalid_option_id"
        self.task.properties_json = properties_dict_list
        self.task.save()
        # run the tasks method
        create_recurring_task_in_notion(self.task.pk)

    def test_reset_database_for_scheduled_task_in_notion_with_wrong_database_id(self):
        self.sample_database.database_id = "wrong_database_id"
        self.sample_database.save()
        self.task.database = self.sample_database
        self.task.save()
        # run the tasks method
        create_recurring_task_in_notion(self.task.pk)
        self.assertEqual(RecurringTask.objects.get(pk=self.task.pk).database, None)

    def test_no_scheduled_task_in_database_throws_exception(self):
        # create new recurring task
        # run the tasks method
        self.assertRaises(
            Exception, lambda x: create_recurring_task_in_notion("invalid_pk")
        )

    def test_no_workspace_access_in_database_throws_exception(self):
        previous_pk = self.task.pk
        NotionWorkspaceAccess.objects.all().delete()
        # run the tasks method
        self.assertRaises(
            Exception, lambda x: create_recurring_task_in_notion(previous_pk)
        )


class TestCreateRecurringTasks(TasksTestCase):
    def setUp(self):
        super().setUp()
        self.test_task_name = "Test Task Name"
        self.test_task_id = "test_id"
        self.test_database_id = "database-id"
        self.test_task_url = f"notion.com/{self.test_task_id}"
        self.create_payload = {
            "name": self.test_task_name,
            "id": self.test_task_id,
            "url": self.test_task_url,
            "database-id": self.test_database_id,
        }

    def assert_task_was_created(self):
        self.assertEqual(RecurringTask.objects.count(), 1)
        created_recurring_task = RecurringTask.objects.all()[0]
        self.assertEqual(created_recurring_task.name, "New Page")
        self.assertEqual(created_recurring_task.owner, self.user)
        self.assertEqual(Schedule.objects.count(), 1)
        schedule_object = Schedule.objects.all()[0]
        self.assertEqual(schedule_object.args, f"{created_recurring_task.pk}")

    def assert_task_was_not_created(self):
        self.assertEqual(RecurringTask.objects.count(), 0)

    def test_logged_in_user_successfully_create_recurring_tasks(self):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.post("/create-recurring-task/", self.create_payload)
        self.assertEqual(response.status_code, 302)
        self.assert_task_was_created()

    def test_create_recurring_task_requires_post_method(self):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.patch("/create-recurring-task/", self.create_payload)
        self.assertEqual(response.status_code, 405)
        self.assert_task_was_not_created()

    def test_create_recurring_task_also_creates_djangoq_scheduler(self):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.post("/create-recurring-task/", self.create_payload)
        self.assertEqual(response.status_code, 302)
        self.assert_task_was_created()
        scheduled_job = Schedule.objects.all()[0]
        self.assertTrue(
            scheduled_job.next_run.timestamp()
            - (datetime.now() + timedelta(days=1)).timestamp()
            < 1000
        )
        self.assertEqual(scheduled_job.schedule_type, Schedule.DAILY)


class TestUpdateRecurringTasksSchedule(TasksTestCase):
    def setUp(self):
        super().setUp()
        self.recurring_test_task_model = RecurringTask.objects.create(
            interval=RecurringTask.TaskIntervals.EVERY_DAY.value,
            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME,
            owner=self.user,
            name="lino",
            database=self.sample_database,
        )
        self.request_url = (
            f"/update-recurring-task-schedule/{self.recurring_test_task_model.pk}"
        )
        self.update_start_time_payload = {
            "start-time": ["2021-12-14T09:30"],
        }
        self.update_interval_payload = {"interval": ["7"]}

    def assert_task_was_not_created(self):
        self.assertEqual(RecurringTask.objects.count(), 1)

    def assert_task_start_time_was_updated(self):
        test_unlocalized_start_datetime = datetime.strptime(
            "2021-12-14T09:30", "%Y-%m-%dT%H:%M"
        )
        test_timezone = pytz.timezone("Europe/Berlin")
        localized_user_start_datetime = test_timezone.localize(
            test_unlocalized_start_datetime
        )
        test_update_start_date_utc_datetime = datetime.fromtimestamp(
            localized_user_start_datetime.timestamp(), tz=timezone.utc
        )
        recurring_task_from_db = RecurringTask.objects.all()[0]
        self.assertEqual(
            recurring_task_from_db.start_time, test_update_start_date_utc_datetime
        )

    def check_task_was_not_updated(self):
        recurring_task_from_db = RecurringTask.objects.all()[0]
        self.assertEqual(recurring_task_from_db.interval, "1")
        self.assertEqual(
            recurring_task_from_db.start_time,
            DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME,
        )
        self.assertEqual(recurring_task_from_db.owner, self.user)
        self.assertEqual(recurring_task_from_db.database.database_id, VALID_DATABASE_ID)

    def test_only_logged_in_user_can_update_recurring_tasks(self):
        # create new recurring task
        response = self.client.post(
            self.request_url,
            self.update_start_time_payload,
            HTTP_X_CLIENT_TIMEZONE="Berlin/Europe",
        )
        self.assertEqual(response.status_code, 302)
        self.check_task_was_not_updated()
        self.assert_task_was_not_created()

    def test_timezone_required_for_update_recurring_task(self):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.post(self.request_url, self.update_start_time_payload)
        self.assertEqual(response.status_code, 400)
        self.check_task_was_not_updated()
        self.assert_task_was_not_created()

    def test_cannot_update_other_users_tasks_settings(self):
        other_user_recurring_task = RecurringTask.objects.create(
            interval=RecurringTask.TaskIntervals.EVERY_DAY.value,
            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME,
            owner=get_user_model().objects.create_user(
                username="testuser2", email="test2@email.com", password="secret"
            ),
            database=self.sample_database,
        )
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.post(
            f"/update-recurring-task-schedule/{other_user_recurring_task.pk}",
            self.update_start_time_payload,
            HTTP_X_CLIENT_TIMEZONE="Europe/Berlin",
        )
        self.assertEqual(response.status_code, 404)

    def test_throw_404_when_not_found(self):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.post(
            "/update-recurring-task-schedule/4",
            self.update_start_time_payload,
            HTTP_X_CLIENT_TIMEZONE="Europe/Berlin",
        )
        self.assertEqual(response.status_code, 404)

    def test_timezone_conversion_occurred_update(self):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.post(
            self.request_url,
            self.update_start_time_payload,
            HTTP_X_CLIENT_TIMEZONE="Europe/Berlin",
        )
        self.assertEqual(response.status_code, 200)
        self.assert_task_was_not_created()
        self.assert_task_start_time_was_updated()

    def test_title_logged_in_user(self):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        new_task_name = "new_task_name"
        payload = {
            "task-name": [new_task_name],
        }
        response = self.client.post(
            self.request_url, payload, HTTP_X_CLIENT_TIMEZONE="Europe/Berlin"
        )
        self.assertEqual(response.status_code, 200)
        self.assert_task_was_not_created()
        recurring_task_from_db = RecurringTask.objects.all()[0]
        self.assertEqual(recurring_task_from_db.name, new_task_name)

    def test_title_update_updates_properties(self):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        new_task_name = "new_task_name"
        payload = {
            "task-name": [new_task_name],
        }
        response = self.client.post(
            self.request_url, payload, HTTP_X_CLIENT_TIMEZONE="Europe/Berlin"
        )
        self.assertEqual(response.status_code, 200)
        self.assert_task_was_not_created()
        recurring_task_from_db = RecurringTask.objects.all()[0]
        self.assertEqual(len(recurring_task_from_db.properties_json), 1)
        self.assertEqual(
            recurring_task_from_db.properties_json[0],
            {
                "id": "title",
                "type": "title",
                "value": new_task_name,
                "name": "Name",
                "options": None,
                "html_form_type": "text",
                "html_value": "new_task_name",
            },
        )

    def test_recurring_task_requires_post_method(self):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.patch(
            self.request_url,
            self.update_start_time_payload,
            HTTP_X_CLIENT_TIMEZONE="Europe/Berlin",
        )
        self.assertEqual(response.status_code, 405)
        self.assert_task_was_not_created()

    def test_logged_in_user_successfully_updates_interval(self):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.post(
            self.request_url,
            self.update_interval_payload,
            HTTP_X_CLIENT_TIMEZONE="Europe/Berlin",
        )
        self.assertEqual(response.status_code, 200)
        self.assert_task_was_not_created()
        recurring_task = RecurringTask.objects.all()[0]
        self.assertEqual(
            recurring_task.interval, self.update_interval_payload["interval"][0]
        )

    def test_logged_in_user_successfully_updates_start_time(self):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.post(
            self.request_url,
            self.update_start_time_payload,
            HTTP_X_CLIENT_TIMEZONE="Europe/Berlin",
        )
        self.assertEqual(response.status_code, 200)


class TestDeleteRecurringTask(TasksTestCase):
    def setUp(self):
        super().setUp()
        self.recurring_test_task_model = RecurringTask.objects.create(
            interval=RecurringTask.TaskIntervals.EVERY_DAY.value,
            owner=self.user,
            database=self.sample_database,
        )
        self.request_url = f"/delete-recurring-task/{self.recurring_test_task_model.pk}"

    def assert_task_deleted(self):
        self.assertEqual(RecurringTask.objects.count(), 0)

    def assert_task_not_deleted(self):
        self.assertEqual(RecurringTask.objects.count(), 1)

    def test_successful_delete(self):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.delete(self.request_url)
        self.assertEqual(response.status_code, 302)
        self.assert_task_deleted()

    def test_successful_delete_with_post(self):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.post(self.request_url)
        self.assertEqual(response.status_code, 302)
        self.assert_task_deleted()

    def test_successful_delete_as_htmx_partial(self):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.delete(self.request_url, HTTP_X_HX_PARTIAL="true")
        self.assertEqual(response.status_code, 200)
        self.assert_task_deleted()

    def test_require_login_for_delete(self):
        response = self.client.delete(self.request_url)
        self.assertEqual(response.status_code, 302)
        self.assert_task_not_deleted()

    def test_require_delete_or_post_method_for_delete(self):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.get(self.request_url)
        self.assertEqual(response.status_code, 405)
        self.assert_task_not_deleted()

    def test_throw_not_found_when_delete(self):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.delete("/delete-recurring-task/invalid-id")
        self.assertEqual(response.status_code, 404)
        self.assert_task_not_deleted()

    def test_cannot_delete_other_users_tasks_settings(self):
        other_user_recurring_task = RecurringTask.objects.create(
            interval=RecurringTask.TaskIntervals.EVERY_DAY.value,
            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME,
            owner=get_user_model().objects.create_user(
                username="testuser2", email="test2@email.com", password="secret"
            ),
            database=self.sample_database,
        )
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.delete(
            f"/delete-recurring-task/{other_user_recurring_task.pk}"
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_also_removes_scheduler_task(self):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.delete(self.request_url)
        self.assertEqual(response.status_code, 302)
        self.assert_task_deleted()
        self.assertEqual(Schedule.objects.count(), 0)


class TestUpdateRecurringTasksProperties(TasksTestCase):
    def setUp(self):
        super().setUp()
        self.default_task_name = "name"
        self.recurring_test_task_model = RecurringTask.objects.create(
            interval=RecurringTask.TaskIntervals.EVERY_DAY.value,
            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME,
            owner=self.user,
            name=self.default_task_name,
            database=self.sample_database,
        )
        self.update_properties_payload_dict = {
            "E%3F%5EI": "cali@gmail.com",
            "not-to-be-added": "empty",
            "Fq%3Ar": datetime.now(),
            "%60moG": "cali",
            "d%60Tf": "Me",
        }
        self.request_url = reverse(
            "update-recurring-task-properties",
            kwargs={"pk": self.recurring_test_task_model.pk},
        )

    def assert_task_was_not_created(self):
        self.assertEqual(RecurringTask.objects.count(), 1)

    def assert_task_properties_was_updated(self):
        recurring_task_from_db = RecurringTask.objects.all()[0]
        properties_json_dict_list = recurring_task_from_db.properties_json
        properties_id_set = {}
        for property_dict in properties_json_dict_list:
            if (
                "id" not in property_dict
                or "name" not in property_dict
                or "type" not in property_dict
            ):
                raise Exception(
                    f"Property dict did not have the right format {property_dict}"
                )
            property_id = property_dict["id"]
            properties_id_set.add(property_id)

            # this property is a checkbox, but not in our update payload
            # value should be false
            if property_id == "Gwjd":
                self.assertEqual(property_dict["value"], False)

            if property_id == "E%3F%5EI":
                self.assertEqual(property_dict["type"], "email")
                self.assertEqual(property_dict["value"], "cali@gmail.com")
        if (
            "not-to-be-added" in properties_id_set
            or "selectedDatabaseId" in properties_id_set
            or "d%60Tf" in properties_id_set
            or "Fq%3Ar" in properties_id_set
        ):  # time field, currently ignored
            raise Exception(
                f"The task with id {property_id} should not have been added!"
            )
        self.assertTrue("%7CJhi" in properties_id_set)
        self.assertTrue("E%3F%5EI" in properties_id_set)
        self.assertTrue("Name" in properties_id_set)
        self.assertEqual(
            recurring_task_from_db.database.database_id,
            VALID_DATABASE_ID,
        )
        self.assertEqual(recurring_task_from_db.database_name, "Todo")

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=notion_db_mock.create_or_get_mocked_oauth_notion_client,
    )
    def test_missing_database_for_recurring_task_throws_404(self, m):
        NotionDatabase.objects.all().delete()
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.post(
            self.request_url, self.update_properties_payload_dict
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(NotionDatabase.objects.count(), 0)

    def check_task_was_not_updated(self):
        recurring_task_from_db = RecurringTask.objects.all()[0]
        self.assertEqual(recurring_task_from_db.properties_json, {})

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=notion_db_mock.create_or_get_mocked_oauth_notion_client,
    )
    def test_only_logged_in_user_can_update_recurring_tasks(self, m):
        # create new recurring task
        response = self.client.post(
            self.request_url, self.update_properties_payload_dict
        )
        self.assertEqual(response.status_code, 302)
        self.check_task_was_not_updated()
        self.assert_task_was_not_created()

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=notion_db_mock.create_or_get_mocked_oauth_notion_client,
    )
    def test_cannot_update_other_users_tasks_properties(self, m):
        other_user_recurring_task = RecurringTask.objects.create(
            interval=RecurringTask.TaskIntervals.EVERY_DAY.value,
            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME,
            owner=get_user_model().objects.create_user(
                username="testuser2", email="test2@email.com", password="secret"
            ),
            database=self.sample_database,
        )
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.post(
            f"/update-recurring-task-properties/{other_user_recurring_task.pk}",
            self.update_properties_payload_dict,
            HTTP_X_SELECTED_DATABASE_ID=notion_db_mock.VALID_DATABASE_ID,
        )
        self.assertEqual(response.status_code, 404)

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=notion_db_mock.create_or_get_mocked_oauth_notion_client,
    )
    def test_throw_404_when_not_found(self, m):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.post(
            f"/update-recurring-task-properties/4",
            self.update_properties_payload_dict,
            HTTP_X_SELECTED_DATABASE_ID=notion_db_mock.VALID_DATABASE_ID,
        )
        self.assertEqual(response.status_code, 404)

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=notion_db_mock.create_or_get_mocked_oauth_notion_client,
    )
    def test_recurring_task_requires_post_method(self, m):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.patch(
            self.request_url, self.update_properties_payload_dict
        )
        self.assertEqual(response.status_code, 405)
        self.assert_task_was_not_created()

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=notion_db_mock.create_or_get_mocked_oauth_notion_client,
    )
    def test_logged_in_user_successfully_updates_properties(self, m):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.post(
            self.request_url,
            self.update_properties_payload_dict,
        )
        self.assertEqual(response.status_code, 200)


class TestUpdateRecurringTasksDatabase(TasksTestCase):
    def setUp(self):
        super().setUp()
        self.default_task_name = "name"
        self.old_database = NotionDatabase.objects.create(
            database_id="old_db_id",
            database_name="old_db_name",
            properties_schema_json=dict(),
        )
        self.recurring_test_task_model = RecurringTask.objects.create(
            interval=RecurringTask.TaskIntervals.EVERY_DAY.value,
            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME,
            owner=self.user,
            name=self.default_task_name,
            database=self.old_database,
            properties_json=dict(),
        )
        self.request_url = (
            f"/update-recurring-task-database/{self.recurring_test_task_model.pk}"
        )

    def assert_task_was_not_created(self):
        self.assertEqual(RecurringTask.objects.count(), 1)

    def assert_database_was_not_updated(self):
        task_database_from_db = RecurringTask.objects.get(
            pk=self.recurring_test_task_model.pk
        ).database
        self.assertEqual(
            task_database_from_db.database_id, self.old_database.database_id
        )
        self.assertEqual(
            task_database_from_db.database_name, self.old_database.database_name
        )
        self.assertEqual(
            task_database_from_db.properties_schema_json,
            self.old_database.properties_schema_json,
        )

    def assert_database_was_updated(self):
        self.assertEqual(NotionDatabase.objects.count(), 1)
        notion_database_model = NotionDatabase.objects.all()[0]
        self.assertEqual(notion_database_model.database_id, VALID_DATABASE_ID)
        self.assertEqual(
            notion_database_model.database_name, notion_db_mock.VALID_DATABASE_NAME
        )
        self.assertGreater(len(notion_database_model.properties_schema_json), 0)
        self.assertNotEqual(RecurringTask.objects.all()[0].properties_json, dict())

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=notion_db_mock.create_or_get_mocked_oauth_notion_client,
    )
    def test_only_logged_in_user_can_update_recurring_tasks(self, m):
        # create new recurring task
        response = self.client.post(self.request_url)
        self.assertEqual(response.status_code, 302)
        self.assert_database_was_not_updated()
        self.assert_task_was_not_created()

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=notion_db_mock.create_or_get_mocked_oauth_notion_client,
    )
    def test_cannot_update_other_users_tasks_database(self, m):
        other_user_recurring_task = RecurringTask.objects.create(
            interval=RecurringTask.TaskIntervals.EVERY_DAY.value,
            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME,
            owner=get_user_model().objects.create_user(
                username="testuser2", email="test2@email.com", password="secret"
            ),
            database=self.sample_database,
        )
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.post(
            f"/update-recurring-task-database/{other_user_recurring_task.pk}",
            {"newDatabaseId": notion_db_mock.VALID_DATABASE_ID},
        )
        self.assertEqual(response.status_code, 404)
        self.assert_database_was_not_updated()

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=notion_db_mock.create_or_get_mocked_oauth_notion_client,
    )
    def test_throw_404_when_not_found(self, m):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.post(
            f"/update-recurring-task-database/4",
            {"newDatabaseId": notion_db_mock.VALID_DATABASE_ID},
        )
        self.assertEqual(response.status_code, 404)
        self.assert_database_was_not_updated()

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=notion_db_mock.create_or_get_mocked_oauth_notion_client,
    )
    def test_throw_403_when_request_header_is_missing(self, m):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.post(
            self.request_url,
        )
        self.assertEqual(response.status_code, 400)
        self.assert_database_was_not_updated()

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=notion_db_mock.create_or_get_mocked_oauth_notion_client,
    )
    def test_update_recurring_task_database_creates_database(self, m):
        NotionDatabase.objects.all().delete()
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.post(
            self.request_url,
            {"newDatabaseId": notion_db_mock.VALID_DATABASE_ID},
        )
        self.assertEqual(response.status_code, 200)
        self.assert_database_was_updated()

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=notion_db_mock.create_or_get_mocked_oauth_notion_client,
    )
    def test_update_recurring_task_does_not_create_new_db_if_already_exists(self, m):
        NotionDatabase.objects.all().delete()
        NotionDatabase.objects.create(
            database_id=VALID_DATABASE_ID,
            database_name=notion_db_mock.VALID_DATABASE_NAME,
        )
        self.assertEqual(NotionDatabase.objects.count(), 1)
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.post(
            self.request_url,
            {"newDatabaseId": notion_db_mock.VALID_DATABASE_ID},
        )
        self.assertEqual(response.status_code, 200)
        self.assert_database_was_updated()


class TestDuplicateRecurringTasksDatabase(TasksTestCase):
    def setUp(self):
        super().setUp()
        self.default_task_name = "name"
        self.old_database = NotionDatabase.objects.create(
            database_id="old_db_id",
            database_name="old_db_name",
            properties_schema_json=dict(),
        )
        self.recurring_test_task_model = RecurringTask.objects.create(
            interval=RecurringTask.TaskIntervals.EVERY_DAY.value,
            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME,
            owner=self.user,
            name=self.default_task_name,
            database=self.old_database,
            properties_json={"property": "12345"},
        )
        self.request_url = reverse(
            "duplicate-recurring-task",
            kwargs={"pk": self.recurring_test_task_model.pk},
        )

    def assert_task_was_not_duplicated(self):
        self.assertEqual(RecurringTask.objects.count(), 1)
        self.assertEqual(Schedule.objects.count(), 1)
        original_task = RecurringTask.objects.all()[0]
        self.assertEqual(original_task.pk, self.recurring_test_task_model.pk)

    def assert_task_was_duplicated(self):
        self.assertEqual(RecurringTask.objects.count(), 2)
        self.assertEqual(Schedule.objects.count(), 2)
        original_task = RecurringTask.objects.all()[0]
        duplicated_task = RecurringTask.objects.all()[1]
        self.assertEqual(original_task.name + " Copy", duplicated_task.name)
        self.assertEqual(original_task.start_time, duplicated_task.start_time)
        self.assertEqual(original_task.properties_json, duplicated_task.properties_json)
        self.assertEqual(original_task.interval, duplicated_task.interval)
        self.assertEqual(original_task.database, duplicated_task.database)

    def test_only_logged_in_user_can_duplicate_recurring_tasks(self):
        # create new recurring task
        response = self.client.post(self.request_url)
        self.assertEqual(response.status_code, 302)
        self.assert_task_was_not_duplicated()

    def test_cannot_duplicate_other_users_tasks_database(self):
        other_user_recurring_task = RecurringTask.objects.create(
            interval=RecurringTask.TaskIntervals.EVERY_DAY.value,
            start_time=DEFAULT_RECURRING_TASK_TEST_STARTIME_DATETIME,
            owner=get_user_model().objects.create_user(
                username="testuser2", email="test2@email.com", password="secret"
            ),
            database=self.sample_database,
        )
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        other_task_url = reverse(
            "duplicate-recurring-task",
            kwargs={"pk": other_user_recurring_task.pk},
        )
        response = self.client.post(other_task_url)
        self.assertEqual(response.status_code, 404)
        for task in RecurringTask.objects.all():
            self.assertFalse("Copy" in task.name)

    def test_throw_404_when_not_found(self):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        missing_task_url = reverse(
            "duplicate-recurring-task",
            kwargs={"pk": 4},
        )
        response = self.client.post(
            missing_task_url,
            {"newDatabaseId": notion_db_mock.VALID_DATABASE_ID},
        )
        self.assertEqual(response.status_code, 404)
        self.assert_task_was_not_duplicated()

    def test_update_recurring_task_database_creates_database(self):
        NotionDatabase.objects.all().delete()
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.post(
            self.request_url,
            {"newDatabaseId": notion_db_mock.VALID_DATABASE_ID},
        )
        self.assertEqual(response.status_code, 302)
        self.assert_task_was_duplicated()
