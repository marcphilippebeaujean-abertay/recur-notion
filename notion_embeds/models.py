from django.db import models

# Create your models here.
from embed_widgets_base.models import Embeddable
from notion_database.models import NotionDatabase, NotionPropertyMetaData


class NotionDatabaseEmbed(Embeddable):
    notion_database = models.ForeignKey(
        NotionDatabase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )

    @property
    def workspace(self):
        if self.notion_database is None:
            return None
        return self.notion_database.notion_workspace


class NotionEmbedPropertySettings(models.Model):
    property = models.ForeignKey(NotionPropertyMetaData, on_delete=models.CASCADE)
    database_embed = models.ForeignKey(
        NotionDatabaseEmbed,
        on_delete=models.CASCADE,
        related_name="notion_property_settings",
    )
