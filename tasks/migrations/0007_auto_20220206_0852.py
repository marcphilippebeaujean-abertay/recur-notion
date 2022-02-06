# Generated by Django 3.2 on 2022-02-06 08:52

import datetime

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tasks", "0006_recurringtask_owner_alter_recurringtask_start_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recurringtask",
            name="name",
            field=models.CharField(default="New Page", max_length=255),
        ),
        migrations.AlterField(
            model_name="recurringtask",
            name="owner",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tasks",
                to="accounts.customuser",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="recurringtask",
            name="start_time",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 2, 7, 8, 52, 22, 598630, tzinfo=utc)
            ),
        ),
    ]
