# Generated by Django 3.2 on 2022-03-22 17:30

import datetime

from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0010_auto_20220311_1544"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recurringtask",
            name="start_time",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 3, 23, 17, 30, 10, 749393, tzinfo=utc)
            ),
        ),
    ]
