# Generated by Django 3.2 on 2022-02-12 19:45

import datetime

from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0008_alter_recurringtask_start_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recurringtask",
            name="start_time",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 2, 13, 19, 45, 27, 675688, tzinfo=utc)
            ),
        ),
    ]