# Generated by Django 3.2 on 2022-03-17 17:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("notion_embeds", "0002_notionembedpropertysettings_should_be_visible"),
    ]

    operations = [
        migrations.DeleteModel(
            name="NotionEmbedPropertySettings",
        ),
    ]
