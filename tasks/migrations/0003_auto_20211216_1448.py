# Generated by Django 3.1.4 on 2021-12-16 14:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_alter_recurringtask_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recurringtask',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='recurringtask',
            name='start_date',
            field=models.DateField(default=datetime.datetime(2021, 12, 16, 14, 48, 4, 126079)),
        ),
    ]