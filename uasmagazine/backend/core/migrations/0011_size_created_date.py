# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-19 14:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20190719_1415'),
    ]

    operations = [
        migrations.AddField(
            model_name='size',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
