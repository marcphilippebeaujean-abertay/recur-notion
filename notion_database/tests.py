from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse_lazy

from workspaces.models import NotionWorkspace, NotionWorkspaceAccess

from .models import NotionDatabase, NotionPropertyMetaData
from .notion_mock_api import (
    VALID_ACCESS_TOKEN,
    VALID_DATABASE_ID,
    create_or_get_mocked_oauth_notion_client,
)
from .service import (
    get_or_save_notion_database_model,
    query_saved_notion_database_model_with_api_update,
    query_user_notion_databases_from_api_as_model_list,
)


# Create your tests here.
class TestDatabaseResponseConversion(TestCase):
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


class TestGetAllUserNotionDatabaseProperties(TestDatabaseResponseConversion):
    def setUp(self):
        super().setUp()
        self.request_url = reverse_lazy("search-workspace-databases-for-task-db-change")

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=create_or_get_mocked_oauth_notion_client,
    )
    def test_only_logged_in_user_can_query_their_databases(self, m):
        response = self.client.post(
            self.request_url, {"taskPk": 1, "database-search-query": VALID_DATABASE_ID}
        )
        self.assertEqual(response.status_code, 302)

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=create_or_get_mocked_oauth_notion_client,
    )
    def test_logged_in_user_successfully_queries_their_databases(self, m):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.post(
            self.request_url, {"taskPk": 1, "database-search-query": VALID_DATABASE_ID}
        )
        self.assertEqual(response.status_code, 200)

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=create_or_get_mocked_oauth_notion_client,
    )
    def test_notion_db_api_object_converted_to_model(self, m):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        db_dict_list = query_user_notion_databases_from_api_as_model_list(
            user_model=self.user, query_string=""
        )
        for db_model in db_dict_list:
            self.assertIsNotNone(db_model.database_name)


class TestGetSingleDatabaseProperties(TestDatabaseResponseConversion):
    def setUp(self):
        super().setUp()
        self.request_url = reverse_lazy("search-workspace-databases-for-task-db-change")
        self.valid_db_request_body = {
            "taskPk": 1,
            "database-search-query": VALID_DATABASE_ID,
        }

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=create_or_get_mocked_oauth_notion_client,
    )
    def test_only_logged_in_user_can_query_database_by_id(self, m):
        response = self.client.post(self.request_url, self.valid_db_request_body)
        self.assertEqual(response.status_code, 302)

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=create_or_get_mocked_oauth_notion_client,
    )
    def test_logged_in_user_queries_db_their_databases(self, m):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.post(self.request_url, self.valid_db_request_body)
        self.assertEqual(response.status_code, 200)

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=create_or_get_mocked_oauth_notion_client,
    )
    def test_convert_query_user_notion_database_by_id_api_resp_to_model(self, m):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        db_dict = query_saved_notion_database_model_with_api_update(
            self.user, VALID_DATABASE_ID
        )


class TestIgnoredPropertiesHandling(TestDatabaseResponseConversion):
    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=create_or_get_mocked_oauth_notion_client,
    )
    def test_db_schema_conversion(self, m):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        generated_db_model = query_saved_notion_database_model_with_api_update(
            self.user, VALID_DATABASE_ID
        )
        self.assertEqual(generated_db_model.database_id, VALID_DATABASE_ID)
        self.assertEqual(generated_db_model.database_name, "Todo")
        # for properties_dict in generated_db_model.notion_properties:
        #    property_dto = NotionPropertyDto.from_dto_dict(properties_dict)
        #    if property_dto.notion_type in IGNORED_PROPERTIES_SET:
        #        self.assertEqual(property_dto.value, None)
        #    else:
        #        self.assertTrue(property_dto.is_default_value)

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=create_or_get_mocked_oauth_notion_client,
    )
    def test_ignored_properties_are_included(self, m):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        generated_db_model = query_saved_notion_database_model_with_api_update(
            self.user, VALID_DATABASE_ID
        )


class TestGetOrSaveNotionDatabase(TestDatabaseResponseConversion):
    def setUp(self):
        super().setUp()
        db_model = NotionDatabase.objects.create(
            notion_id=VALID_DATABASE_ID,
            database_name="Todo",
            notion_workspace=self.init_workspace,
        )

        NotionPropertyMetaData.objects.create(
            notion_id="E%3F%5EI",
            name="Property 2",
            property_type="email",
            database=db_model,
        )
        NotionPropertyMetaData.objects.create(
            notion_id="SXQ%7B",
            name="Property 3",
            property_type="phone_number",
            database=db_model,
        )
        NotionPropertyMetaData.objects.create(
            notion_id="%60moG",
            name="Status Old",
            property_type="select",
            database=db_model,
        )

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=create_or_get_mocked_oauth_notion_client,
    )
    def test_save_when_there_is_no_one_in_database(self, m):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        generated_db_model = query_saved_notion_database_model_with_api_update(
            self.user, VALID_DATABASE_ID
        )
        self.assertEqual(NotionDatabase.objects.all().count(), 1)
        self.assertEqual(NotionPropertyMetaData.objects.all().count(), 9)

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=create_or_get_mocked_oauth_notion_client,
    )
    def test_property_updates_occur_when_calling_method(self, m):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        generated_db_model = query_saved_notion_database_model_with_api_update(
            self.user, VALID_DATABASE_ID
        )
        self.assertEqual(NotionDatabase.objects.all().count(), 1)
        self.assertEqual(NotionPropertyMetaData.objects.all().count(), 9)
        stored_db_properties_models = generated_db_model.notion_properties.all()
        for stored_property_model in stored_db_properties_models:
            if stored_property_model.name == "Status Old":
                raise Exception("Did not update name after querying database!")

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=create_or_get_mocked_oauth_notion_client,
    )
    def test_data_is_saved_if_not_exists_in_db(self, m):
        NotionDatabase.objects.all().delete()
        self.assertEqual(NotionDatabase.objects.all().count(), 0)
        self.assertEqual(NotionPropertyMetaData.objects.all().count(), 0)
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        generated_db_model = query_saved_notion_database_model_with_api_update(
            self.user, VALID_DATABASE_ID
        )
        self.assertEqual(NotionDatabase.objects.all().count(), 1)
        self.assertEqual(NotionPropertyMetaData.objects.all().count(), 9)
        stored_db_properties_models = generated_db_model.notion_properties.all()
        for stored_property_model in stored_db_properties_models:
            if stored_property_model.name == "Status Old":
                raise Exception("Did not update name after querying database!")

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=create_or_get_mocked_oauth_notion_client,
    )
    def test_data_is_saved_if_not_exists_in_db_but_other_db(self, m):
        NotionDatabase.objects.filter(notion_id=VALID_DATABASE_ID).update(
            notion_id="my-new-notion-id"
        )
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        generated_db_model = query_saved_notion_database_model_with_api_update(
            self.user, VALID_DATABASE_ID
        )
        self.assertEqual(NotionDatabase.objects.all().count(), 2)
        self.assertEqual(NotionPropertyMetaData.objects.all().count(), 12)
