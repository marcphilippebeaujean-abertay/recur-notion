from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from notion_properties.constants import IGNORED_PROPERTIES_SET
from workspaces.models import NotionWorkspace, NotionWorkspaceAccess

from .notion_mock_api import (
    VALID_ACCESS_TOKEN,
    VALID_DATABASE_ID,
    create_or_get_mocked_oauth_notion_client,
)
from .service import (
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
        self.request_url = "/get-workspace-databases/"

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=create_or_get_mocked_oauth_notion_client,
    )
    def test_only_logged_in_user_can_query_their_databases(self, m):
        response = self.client.post(self.request_url)
        self.assertEqual(response.status_code, 302)

    @mock.patch(
        "notion_database.service.notion_client.Client",
        side_effect=create_or_get_mocked_oauth_notion_client,
    )
    def test_logged_in_user_successfully_queries_their_databases(self, m):
        self.client.force_login(
            get_user_model().objects.get_or_create(username=self.user.username)[0]
        )
        response = self.client.post(self.request_url)
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
            for property_container in db_dict["properties"]:
                if property_container.notion_type in IGNORED_PROPERTIES_SET:
                    raise Exception(
                        f"Property {property_container.notion_type} was supposed to be ignored!"
                    )


class TestGetSingleDatabaseProperties(TestDatabaseResponseConversion):
    def setUp(self):
        super().setUp()
        self.request_url = "/get-workspace-databases/"
        self.valid_db_request_body = {"selected-database-id": VALID_DATABASE_ID}

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
        for property_container in db_dict["properties"]:
            if property_container.notion_type in IGNORED_PROPERTIES_SET:
                raise Exception(
                    f"Property {property_container.notion_type} was supposed to be ignored!"
                )
