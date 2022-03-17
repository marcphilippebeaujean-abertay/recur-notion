from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

import notion_database.notion_mock_api as notion_db_mock
from embed_widgets_base.models import Embeddable
from notion_database.models import NotionDatabase
from notion_database.notion_mock_api import VALID_ACCESS_TOKEN, VALID_DATABASE_ID
from notion_embeds.models import NotionDatabaseEmbed
from workspaces.models import NotionWorkspace, NotionWorkspaceAccess


class NotionEmbedTestCase(TestCase):
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
            notion_id=VALID_DATABASE_ID,
            database_name="The Database",
            notion_workspace=self.init_workspace,
        )

    def login_user_for_test(self):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )

    def create_sample_embed(self, init_name="12345"):
        return NotionDatabaseEmbed.objects.create(
            creator=self.user,
            name=init_name,
            notion_database=self.sample_database,
        )

    def create_random_user_embed(self):
        return NotionDatabaseEmbed.objects.create(
            creator=get_user_model().objects.create_user(
                username="testuser2", email="test2@email.com", password="secret"
            ),
            name="lino",
            notion_database=self.sample_database,
        )


class TestCreateNotionEmbed(NotionEmbedTestCase):
    def setUp(self):
        super().setUp()
        self.request_url = reverse("create-notion-embed")

    def assert_embeddable_was_created(self):
        self.assertEqual(NotionDatabaseEmbed.objects.count(), 1)
        self.assertEqual(Embeddable.objects.count(), 1)
        created_notion_db_embeddable = NotionDatabaseEmbed.objects.all()[0]
        self.assertEqual(
            created_notion_db_embeddable.name, "New Notion Database Widget"
        )
        self.assertEqual(created_notion_db_embeddable.creator, self.user)
        self.assertEqual(created_notion_db_embeddable.workspace, None)

    def assert_embeddable_was_not_created(self):
        self.assertEqual(NotionDatabaseEmbed.objects.count(), 0)
        self.assertEqual(Embeddable.objects.count(), 0)

    def test_logged_in_user_successfully_create_recurring_tasks(self):
        self.login_user_for_test()
        response = self.client.post(self.request_url)
        self.assertEqual(response.status_code, 302)
        self.assert_embeddable_was_created()

    def test_cannot_create_recurring_task_without_workspace_access(self):
        NotionWorkspaceAccess.objects.all().delete()
        self.login_user_for_test()
        response = self.client.post(self.request_url)
        self.assertEqual(response.status_code, 302)
        self.assert_embeddable_was_not_created()

    def test_create_recurring_task_requires_post_method(self):
        self.login_user_for_test()
        response = self.client.patch(self.request_url)
        self.assertEqual(response.status_code, 405)
        self.assert_embeddable_was_not_created()


class TestUpdateNotionEmbedName(NotionEmbedTestCase):
    def setUp(self):
        super().setUp()
        self.init_name = "lino"
        self.updated_name = "lino2"

        self.notion_database_embed = self.create_sample_embed(init_name=self.init_name)
        self.request_url = reverse(
            "update-notion-embed-name", kwargs={"pk": self.notion_database_embed.pk}
        )
        self.update_name_payload = {"embed-name": self.updated_name}

    def assert_embed_was_not_created(self):
        self.assertEqual(NotionDatabaseEmbed.objects.count(), 1)

    def assert_embed_was_not_updated(self):
        notion_embed_db = NotionDatabaseEmbed.objects.all()[0]
        self.assertEqual(notion_embed_db.name, self.init_name)
        self.assertEqual(notion_embed_db.creator, self.user)
        self.assertEqual(notion_embed_db.notion_database.notion_id, VALID_DATABASE_ID)

    def assert_embed_was_updated(self):
        notion_embed_db = NotionDatabaseEmbed.objects.all()[0]
        self.assertEqual(notion_embed_db.name, self.updated_name)
        self.assertEqual(notion_embed_db.creator, self.user)
        self.assertEqual(notion_embed_db.notion_database.notion_id, VALID_DATABASE_ID)

    def test_only_logged_in_user_can_update_notion_embed(self):
        # create new recurring task
        response = self.client.post(
            self.request_url,
            self.update_name_payload,
        )
        self.assertEqual(response.status_code, 302)
        self.assert_embed_was_not_updated()
        self.assert_embed_was_not_created()

    def test_cannot_update_other_users_notion_embed(self):
        other_user_recurring_task = self.create_random_user_embed()
        self.login_user_for_test()
        response = self.client.post(
            reverse(
                "update-notion-embed-name", kwargs={"pk": other_user_recurring_task.pk}
            ),
            self.update_name_payload,
        )
        self.assertEqual(response.status_code, 404)
        self.assert_embed_was_not_updated()

    def test_throw_404_when_not_found(self):
        self.login_user_for_test()
        response = self.client.post(
            reverse("update-notion-embed-name", kwargs={"pk": "4"}),
            self.update_name_payload,
        )
        self.assertEqual(response.status_code, 404)
        self.assert_embed_was_not_updated()

    def test_notion_embed_requires_post_method(self):
        self.login_user_for_test()
        response = self.client.patch(
            self.request_url,
            self.update_name_payload,
        )
        self.assertEqual(response.status_code, 405)
        self.assert_embed_was_not_created()

    def test_logged_in_user_successfully_updates_name(self):
        self.login_user_for_test()
        response = self.client.post(
            self.request_url,
            self.update_name_payload,
        )
        self.assertEqual(response.status_code, 200)
        self.assert_embed_was_not_created()
        self.assert_embed_was_updated()


class TestDeleteNotionEmbed(NotionEmbedTestCase):
    def setUp(self):
        super().setUp()
        self.notion_database_embed = self.create_sample_embed()
        self.request_reverse_url_name = f"delete-notion-embed"
        self.request_url = reverse(
            self.request_reverse_url_name, kwargs={"pk": self.notion_database_embed.pk}
        )

    def assert_embed_deleted(self):
        self.assertEqual(NotionDatabaseEmbed.objects.count(), 0)
        self.assertEqual(Embeddable.objects.count(), 0)

    def assert_embed_not_deleted(self):
        self.assertEqual(NotionDatabaseEmbed.objects.count(), 1)
        self.assertEqual(Embeddable.objects.count(), 1)

    def test_successful_delete(self):
        self.login_user_for_test()
        response = self.client.delete(self.request_url)
        self.assertEqual(response.status_code, 302)
        self.assert_embed_deleted()

    def test_successful_delete_with_post(self):
        self.login_user_for_test()
        response = self.client.post(self.request_url)
        self.assertEqual(response.status_code, 302)
        self.assert_embed_deleted()

    def test_successful_delete_as_htmx_partial(self):
        self.login_user_for_test()
        response = self.client.delete(self.request_url, HTTP_X_HX_PARTIAL="true")
        self.assertEqual(response.status_code, 200)
        self.assert_embed_deleted()

    def test_require_login_for_delete(self):
        response = self.client.delete(self.request_url)
        self.assertEqual(response.status_code, 302)
        self.assert_embed_not_deleted()

    def test_require_delete_or_post_method_for_delete(self):
        self.login_user_for_test()
        response = self.client.get(self.request_url)
        self.assertEqual(response.status_code, 405)
        self.assert_embed_not_deleted()

    def test_throw_not_found_when_delete(self):
        self.login_user_for_test()
        response = self.client.delete(
            reverse(self.request_reverse_url_name, kwargs={"pk": "1234"})
        )
        self.assertEqual(response.status_code, 404)
        self.assert_embed_not_deleted()

    def test_cannot_delete_other_users_tasks_settings(self):
        other_user_recurring_task = self.create_random_user_embed()
        self.login_user_for_test()
        response = self.client.delete(
            reverse(
                self.request_reverse_url_name,
                kwargs={"pk": other_user_recurring_task.pk},
            )
        )
        self.assertEqual(response.status_code, 404)


class TestUpdateNotionEmbedDatabase(NotionEmbedTestCase):
    def setUp(self):
        super().setUp()
        self.default_task_name = "name"
        self.old_database = NotionDatabase.objects.create(
            notion_id="old_db_id",
            database_name="old_db_name",
            notion_workspace=self.init_workspace,
        )
        self.notion_database_embed = NotionDatabaseEmbed.objects.create(
            creator=self.user,
            name="lino",
            notion_database=self.old_database,
        )
        self.request_reverse_path_name = f"update-notion-embed-database"
        self.request_url = reverse(
            self.request_reverse_path_name, kwargs={"pk": self.notion_database_embed.pk}
        )
        self.request_payload = {"newDatabaseId": notion_db_mock.VALID_DATABASE_ID}

    def assert_notion_embed_was_not_created(self):
        self.assertEqual(NotionDatabaseEmbed.objects.count(), 1)

    def assert_database_was_not_updated(self):
        task_database_from_db = NotionDatabaseEmbed.objects.get(
            pk=self.notion_database_embed.pk
        ).notion_database
        self.assertEqual(task_database_from_db.notion_id, self.old_database.notion_id)
        self.assertEqual(
            task_database_from_db.database_name, self.old_database.database_name
        )

    def assert_database_was_updated(self):
        self.assertEqual(NotionDatabase.objects.count(), 1)
        notion_database_model = NotionDatabase.objects.all()[0]
        self.assertEqual(notion_database_model.notion_id, VALID_DATABASE_ID)
        self.assertEqual(
            notion_database_model.database_name, notion_db_mock.VALID_DATABASE_NAME
        )

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=notion_db_mock.create_or_get_mocked_oauth_notion_client,
    )
    def test_only_logged_in_user_can_update(self, m):
        # create new recurring task
        response = self.client.post(self.request_url, self.request_payload)
        self.assertEqual(response.status_code, 302)
        self.assert_database_was_not_updated()
        self.assert_notion_embed_was_not_created()

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=notion_db_mock.create_or_get_mocked_oauth_notion_client,
    )
    def test_cannot_update_other_users_tasks_database(self, m):
        other_user_recurring_task = self.create_random_user_embed()
        self.login_user_for_test()
        response = self.client.post(
            reverse(
                self.request_reverse_path_name,
                kwargs={"pk": other_user_recurring_task.pk},
            ),
            self.request_payload,
        )
        self.assertEqual(response.status_code, 404)
        self.assert_database_was_not_updated()

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=notion_db_mock.create_or_get_mocked_oauth_notion_client,
    )
    def test_throw_404_when_not_found(self, m):
        self.login_user_for_test()
        response = self.client.post(
            reverse(self.request_reverse_path_name, kwargs={"pk": "4"}),
            {"newDatabaseId": notion_db_mock.VALID_DATABASE_ID},
        )
        self.assertEqual(response.status_code, 404)
        self.assert_database_was_not_updated()

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=notion_db_mock.create_or_get_mocked_oauth_notion_client,
    )
    def test_throw_403_when_request_header_is_missing(self, m):
        self.login_user_for_test()
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
        self.login_user_for_test()
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
            notion_id=VALID_DATABASE_ID,
            database_name=notion_db_mock.VALID_DATABASE_NAME,
            notion_workspace=self.init_workspace,
        )
        self.assertEqual(NotionDatabase.objects.count(), 1)
        self.login_user_for_test()
        response = self.client.post(
            self.request_url,
            {"newDatabaseId": notion_db_mock.VALID_DATABASE_ID},
        )
        self.assertEqual(response.status_code, 200)
        self.assert_database_was_updated()


class TestGetRecurringTaskView(NotionEmbedTestCase):
    def setUp(self):
        super().setUp()
        self.notion_embed_test_model = self.create_sample_embed()
        self.request_url = reverse(
            "notion-embed-view", kwargs={"pk": self.notion_embed_test_model.pk}
        )

    def test_cannot_get_task_without_login(self):
        response = self.client.get(self.request_url)
        self.assertEqual(response.status_code, 302)

    def test_cannot_get_notion_embed_without_workspace_access(self):
        NotionWorkspaceAccess.objects.all().delete()
        self.login_user_for_test()
        queried_access = NotionWorkspaceAccess.objects.filter(owner=self.user).all()
        response = self.client.get(self.request_url)
        self.assertEqual(response.status_code, 302)

    def test_cannot_view_other_users_notion_embed(self):
        NotionWorkspaceAccess.objects.all().delete()
        self.login_user_for_test()
        queried_access = NotionWorkspaceAccess.objects.filter(owner=self.user).all()
        response = self.client.get(self.request_url)
        self.assertEqual(response.status_code, 302)

    def test_can_get_task(self):
        self.login_user_for_test()
        response = self.client.get(self.request_url)
        self.assertEqual(response.status_code, 200)


class TestGetRecurringTaskListView(NotionEmbedTestCase):
    def setUp(self):
        super().setUp()
        self.notion_embed_test_model = self.create_sample_embed()
        self.request_url = reverse("notion-embeds-list-view")

    def test_cannot_get_tasks_list_without_login(self):
        response = self.client.get(self.request_url)
        self.assertEqual(response.status_code, 302)

    def test_cannot_get_tasks_list_without_workspace_access(self):
        NotionWorkspaceAccess.objects.all().delete()
        self.login_user_for_test()
        queried_access = NotionWorkspaceAccess.objects.filter(owner=self.user).all()
        response = self.client.get(self.request_url)
        self.assertEqual(response.status_code, 302)

    def test_can_get_tasks_list(self):
        self.login_user_for_test()
        response = self.client.get(self.request_url)
        self.assertEqual(response.status_code, 200)
