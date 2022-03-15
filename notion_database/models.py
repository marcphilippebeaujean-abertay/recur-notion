from django.db import models

from workspaces.models import NotionWorkspace


class NotionDatabase(models.Model):
    # ID used to find original task this one is being cloned from
    notion_id = models.CharField(max_length=255, primary_key=True, null=False)
    database_name = models.CharField(max_length=255)
    notion_workspace = models.ForeignKey(
        NotionWorkspace,
        on_delete=models.CASCADE,
        related_name="notion_databases",
        null=False,
    )


class NotionPropertyMetaData(models.Model):
    notion_id = models.CharField(max_length=255, null=False)
    name = models.CharField(max_length=255)
    property_type = models.CharField(max_length=255, null=False)
    database = models.ForeignKey(
        NotionDatabase,
        on_delete=models.CASCADE,
        related_name="notion_properties",
        null=False,
    )
