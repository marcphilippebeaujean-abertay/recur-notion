from django.core.serializers.json import DjangoJSONEncoder
from django.db import models


# Create your models here.
class NotionDatabase(models.Model):
    # ID used to find original task this one is being cloned from
    database_id = models.CharField(
        max_length=255, null=None, blank=None, primary_key=True
    )
    database_name = models.CharField(max_length=255, null=None, blank=None)
    properties_schema_json = models.JSONField(encoder=DjangoJSONEncoder, default=dict)
