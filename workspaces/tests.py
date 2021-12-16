from unittest import mock

from django.test import TestCase
from django.contrib.auth import get_user_model

from .service import create_access_workspace_from_user_code
from .models import NotionWorkspace, NotionWorkspaceAccess

OLD_WORKSPACE_CODE = '54321'
OLD_WORKSPACE_ID = 'oldworkspaceid'
OLD_WORKSPACE_NAME = 'oldworkspacename'
UPDATED_WORKSPACE_ICON = 'icon2.svg'

NEW_WORKSPACE_CODE = '12345'
NEW_WORKSPACE_ID = 'newworkspaceid'
NEW_WORKSPACE_NAME = 'newworkspacename'
NEW_ACCESS_TOKEN = 'access23423df'


def mocked_oauth_notion_api(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] != 'https://api.notion.com/v1/oauth/token':
        return MockResponse({"message": "bad request"}, 400)

    if kwargs['json']['code'] == NEW_WORKSPACE_CODE:
        return MockResponse({
            "workspace_id": NEW_WORKSPACE_ID,
            "workspace_name": NEW_WORKSPACE_NAME,
            "workspace_icon": UPDATED_WORKSPACE_ICON,
            "access_token": NEW_ACCESS_TOKEN
        }, 200)
    elif kwargs['json']['code'] == OLD_WORKSPACE_CODE:
        return MockResponse({
            "workspace_id": OLD_WORKSPACE_ID,
            "workspace_name": OLD_WORKSPACE_NAME,
            "workspace_icon": UPDATED_WORKSPACE_ICON,
            "access_token": NEW_ACCESS_TOKEN
        }, 200)

    return MockResponse(None, 404)


class NotionWorkspacesTestCase(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email.com',
            password='secret'
        )
        self.init_workspace = NotionWorkspace.objects.create(
            name=OLD_WORKSPACE_NAME,
            notion_id=OLD_WORKSPACE_ID,
            icon_url="icon.svg"
        )
        self.init_workspace_access = NotionWorkspaceAccess.objects.create(
            access_token="access",
            workspace=self.init_workspace,
            owner=self.user
        )

    @mock.patch('workspaces.service.requests.post', side_effect=mocked_oauth_notion_api)
    def test_create_new_workspace_and_access(self, m):
        create_access_workspace_from_user_code(self.user, NEW_WORKSPACE_CODE)
        self.assertNotEqual(NotionWorkspace.objects.filter(notion_id=NEW_WORKSPACE_ID).first(), None)
        self.assertNotEqual(NotionWorkspaceAccess.objects.filter(access_token=NEW_ACCESS_TOKEN).first(), None)

    @mock.patch('workspaces.service.requests.post', side_effect=mocked_oauth_notion_api)
    def test_create_workspace_but_using_bad_code(self, m):
        self.assertRaises(Exception, lambda x: create_access_workspace_from_user_code(self.user, 'bad_code'))
        self.assertEqual(NotionWorkspace.objects.filter(notion_id=NEW_WORKSPACE_ID).first(), None)
        self.assertEqual(NotionWorkspaceAccess.objects.filter(access_token=NEW_ACCESS_TOKEN).first(), None)

    @mock.patch('workspaces.service.requests.post', side_effect=mocked_oauth_notion_api)
    def test_update_existing_workspace_access(self, m):
        create_access_workspace_from_user_code(self.user, OLD_WORKSPACE_CODE)
        new_workspace = NotionWorkspace.objects.filter(notion_id=NEW_WORKSPACE_ID).first()
        self.assertEqual(new_workspace, None)
        old_workspace = NotionWorkspace.objects.filter(notion_id=OLD_WORKSPACE_ID).first()
        self.assertEqual(old_workspace.icon_url, UPDATED_WORKSPACE_ICON)
        updated_workspace_access = NotionWorkspaceAccess.objects.filter(access_token=NEW_ACCESS_TOKEN).first()
        self.assertNotEqual(updated_workspace_access, None)
        updated_workspace_access.workspace = old_workspace

    @mock.patch('workspaces.service.requests.post', side_effect=mocked_oauth_notion_api)
    def test_client_request_create_new_workspace_and_access(self, m):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.get('/notion-oauth?code=' + NEW_WORKSPACE_CODE)
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(NotionWorkspace.objects.filter(notion_id=NEW_WORKSPACE_ID).first(), None)
        self.assertNotEqual(NotionWorkspaceAccess.objects.filter(access_token=NEW_ACCESS_TOKEN).first(), None)

    @mock.patch('workspaces.service.requests.post', side_effect=mocked_oauth_notion_api)
    def test_client_request_bad_method(self, m):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.post('/notion-oauth?code=' + NEW_WORKSPACE_CODE)
        self.assertEqual(response.status_code, 405)

    @mock.patch('workspaces.service.requests.post', side_effect=mocked_oauth_notion_api)
    def test_client_request_not_logged_in(self, m):
        response = self.client.get('/notion-oauth?code=' + NEW_WORKSPACE_CODE)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(NotionWorkspace.objects.filter(notion_id=NEW_WORKSPACE_ID).first(), None)
        self.assertEqual(NotionWorkspaceAccess.objects.filter(access_token=NEW_ACCESS_TOKEN).first(), None)

    @mock.patch('workspaces.service.requests.post', side_effect=mocked_oauth_notion_api)
    def test_client_request_no_code(self, m):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.get('/notion-oauth')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(NotionWorkspace.objects.filter(notion_id=NEW_WORKSPACE_ID).first(), None)
        self.assertEqual(NotionWorkspaceAccess.objects.filter(access_token=NEW_ACCESS_TOKEN).first(), None)

    @mock.patch('workspaces.service.requests.post', side_effect=mocked_oauth_notion_api)
    def test_client_request_bad_code(self, m):
        self.client.force_login(get_user_model().objects.get_or_create(username=self.user.username)[0])
        response = self.client.get('/notion-oauth?code=bad_code')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(NotionWorkspace.objects.filter(notion_id=NEW_WORKSPACE_ID).first(), None)
        self.assertEqual(NotionWorkspaceAccess.objects.filter(access_token=NEW_ACCESS_TOKEN).first(), None)
