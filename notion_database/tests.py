from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse_lazy

from notion_properties.constants import IGNORED_PROPERTIES_SET
from notion_properties.dto import NotionPropertyDto
from workspaces.models import NotionWorkspace, NotionWorkspaceAccess

from .notion_mock_api import (
    VALID_ACCESS_TOKEN,
    VALID_DATABASE_ID,
    create_or_get_mocked_oauth_notion_client,
)
from .service import (
    get_or_update_database_from_simple_database_dict_returning_model,
    query_user_notion_database_with_api_by_id_as_dict,
    query_user_notion_databases_list,
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
    def test_notion_db_api_object_converted_to_simple_python_dictionary(self, m):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        db_dict_list = query_user_notion_databases_list(
            user_model=self.user, query_string=""
        )
        for db_dict in db_dict_list:
            if (
                not "name" in db_dict
                or not "properties" in db_dict
                or not "id" in db_dict
            ):
                raise Exception(
                    "Invalid conversion of a dictioanry, proeprties are missing!"
                )


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
    def test_convert_query_user_notion_database_by_id_api_resp_to_dictionary(self, m):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        db_dict = query_user_notion_database_with_api_by_id_as_dict(
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
        db_dict = query_user_notion_database_with_api_by_id_as_dict(
            self.user, VALID_DATABASE_ID
        )
        generated_db_model = (
            get_or_update_database_from_simple_database_dict_returning_model(
                simple_database_dict=db_dict
            )
        )
        self.assertEqual(generated_db_model.database_id, VALID_DATABASE_ID)
        self.assertEqual(generated_db_model.database_name, "Todo")
        for properties_dict in generated_db_model.properties_schema_json:
            property_dto = NotionPropertyDto.from_dto_dict(properties_dict)
            if property_dto.notion_type in IGNORED_PROPERTIES_SET:
                self.assertEqual(property_dto.value, None)
            else:
                self.assertTrue(property_dto.is_default_value)

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=create_or_get_mocked_oauth_notion_client,
    )
    def test_ignored_properties_are_included(self, m):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        db_dict = query_user_notion_database_with_api_by_id_as_dict(
            self.user, VALID_DATABASE_ID
        )
        generated_db_model = (
            get_or_update_database_from_simple_database_dict_returning_model(
                simple_database_dict=db_dict
            )
        )
        for properties_dict in generated_db_model.properties_schema_json:
            property_dto = NotionPropertyDto.from_dto_dict(properties_dict)
            if property_dto.notion_type in IGNORED_PROPERTIES_SET:
                return
        raise Exception(
            "Ignored properties should be included in database schema json, but none were found!"
        )

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=create_or_get_mocked_oauth_notion_client,
    )
    def test_ignored_properties_are_included_when_querying_their_names(self, m):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        db_dict = query_user_notion_database_with_api_by_id_as_dict(
            self.user, VALID_DATABASE_ID
        )
        generated_db_model = (
            get_or_update_database_from_simple_database_dict_returning_model(
                simple_database_dict=db_dict
            )
        )
        if "Assign" not in generated_db_model.get_list_of_unsupported_property_names():
            raise Exception("Missing some unsupported property name in method")

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=create_or_get_mocked_oauth_notion_client,
    )
    def test_ignored_properties_names_are_empty_array_if_schema_is_dict(self, m):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        db_dict = query_user_notion_database_with_api_by_id_as_dict(
            self.user, VALID_DATABASE_ID
        )
        generated_db_model = (
            get_or_update_database_from_simple_database_dict_returning_model(
                simple_database_dict=db_dict
            )
        )
        generated_db_model.properties_schema_json = {"hello": "world"}
        self.assertEqual(
            len(generated_db_model.get_list_of_unsupported_property_names()), 0
        )
