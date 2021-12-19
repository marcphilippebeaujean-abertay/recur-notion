from config.settings import NOTION_CLIENT_SECRET, NOTION_CLIENT_ID, NOTION_OAUTH_CALLBACK

import requests
from requests.auth import HTTPBasicAuth

from .models import NotionWorkspace, NotionWorkspaceAccess


def create_access_workspace_from_user_code(user_model, oauth_code):
    auth_payload_dict = {
        "code": oauth_code,
        "grant_type": "authorization_code",
        "redirect_uri": NOTION_OAUTH_CALLBACK
    }
    response = requests.post('https://api.notion.com/v1/oauth/token',
                             json=auth_payload_dict,
                             auth=HTTPBasicAuth(NOTION_CLIENT_ID, NOTION_CLIENT_SECRET))
    if response.status_code == 200:
        notion_workspace_auth_data = response.json()
        workspace_id = notion_workspace_auth_data["workspace_id"]
        notion_workspace_model = NotionWorkspace.objects.filter(notion_id=workspace_id).first()
        if notion_workspace_model is None:
            notion_workspace_model = NotionWorkspace(
                name=notion_workspace_auth_data["workspace_name"],
                notion_id=workspace_id,
                icon_url=notion_workspace_auth_data["workspace_icon"]
            )
        else:
            notion_workspace_model.name = notion_workspace_auth_data["workspace_name"]
            notion_workspace_model.icon_url = notion_workspace_auth_data["workspace_icon"]
        notion_workspace_model.save()
        workspace_access_model = NotionWorkspaceAccess.objects.filter(workspace=notion_workspace_model,
                                                                      owner=user_model).first()
        if workspace_access_model is None:
            workspace_access_model = NotionWorkspaceAccess.objects.create(
                access_token=notion_workspace_auth_data["access_token"],
                workspace=notion_workspace_model,
                owner=user_model
            )
        else:
            workspace_access_model.access_token = notion_workspace_auth_data["access_token"]
        workspace_access_model.save()
    else:
        raise Exception('Unexpected Error - could not add Notion workspace to Account.')
