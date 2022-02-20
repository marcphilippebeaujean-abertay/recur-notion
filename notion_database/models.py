from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

# Create your models here.
from notion_properties.dto import NotionPropertyDto
from notion_properties.service import (
    get_list_of_ignored_property_names_in_notion_property_dto_list,
)


class NotionDatabase(models.Model):
    # ID used to find original task this one is being cloned from
    database_id = models.CharField(
        max_length=255, null=None, blank=None, primary_key=True
    )
    database_name = models.CharField(max_length=255, null=None, blank=None)
    properties_schema_json = models.JSONField(encoder=DjangoJSONEncoder, default=dict)

    def get_list_of_unsupported_property_names(self):
        if isinstance(self.properties_schema_json, list) is False:
            return []
        property_dto_list = [
            NotionPropertyDto.from_dto_dict(property_dict)
            for property_dict in self.properties_schema_json
        ]
        return get_list_of_ignored_property_names_in_notion_property_dto_list(
            property_dto_list
        )
