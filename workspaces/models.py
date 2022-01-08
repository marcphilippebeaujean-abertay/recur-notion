from django.db import models
from accounts.models import CustomUser


class NotionWorkspace(models.Model):
    name = models.CharField(max_length=255)
    # ID used by Notion to identify this Workspace
    notion_id = models.CharField(max_length=255, unique=True)
    icon_url = models.CharField(max_length=255, null=True, blank=True)


class NotionWorkspaceAccess(models.Model):
    access_token = models.CharField(max_length=255)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='workspace_access')
    workspace = models.ForeignKey(NotionWorkspace, on_delete=models.CASCADE)
