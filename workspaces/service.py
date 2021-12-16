from config.settings import NOTION_CLIENT_SECRET, NOTION_CLIENT_ID, NOTION_OAUTH_CALLBACK

import requests
from requests.auth import HTTPBasicAuth

from .models import NotionWorkspace, NotionWorkspaceAccess


def create_access_workspace_from_user_code(user, code):
    auth_payload = {
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": NOTION_OAUTH_CALLBACK
    }
    response = requests.post('https://api.notion.com/v1/oauth/token',
                             json=auth_payload,
                             auth=HTTPBasicAuth(NOTION_CLIENT_ID, NOTION_CLIENT_SECRET))
    if response.status_code == 200:
        notion_workspace_auth_data = response.json()
        workspace_id = notion_workspace_auth_data["workspace_id"]
        notion_workspace = NotionWorkspace.objects.filter(notion_id=workspace_id).first()
        if notion_workspace is None:
            notion_workspace = NotionWorkspace(
                name=notion_workspace_auth_data["workspace_name"],
                notion_id=workspace_id,
                icon_url=notion_workspace_auth_data["workspace_icon"]
            )
        else:
            notion_workspace.name = notion_workspace_auth_data["workspace_name"]
            notion_workspace.icon_url = notion_workspace_auth_data["workspace_icon"]
        notion_workspace.save()
        workspace_access = NotionWorkspaceAccess.objects.filter(workspace=notion_workspace, owner=user).first()
        if workspace_access is None:
            workspace_access = NotionWorkspaceAccess.objects.create(
                access_token=notion_workspace_auth_data["access_token"],
                workspace=notion_workspace,
                owner=user
            )
        else:
            workspace_access.access_token = notion_workspace_auth_data["access_token"]
        workspace_access.save()
    else:
        raise Exception('Unexpected Error - could not add Notion workspace to Account.')
