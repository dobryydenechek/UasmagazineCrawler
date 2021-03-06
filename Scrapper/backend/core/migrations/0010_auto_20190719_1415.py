# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-19 14:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_spiderstatistic'),
    ]

    operations = [
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_file', models.BooleanField(default=False)),
                ('size', models.IntegerField(default=0)),
                ('spider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Spider')),
            ],
        ),
        migrations.RemoveField(
            model_name='spiderstatistic',
            name='spider',
        ),
        migrations.AlterField(
            model_name='document',
            name='size',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Size'),
        ),
        migrations.AlterField(
            model_name='file',
            name='size',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Size'),
        ),
        migrations.DeleteModel(
            name='SpiderStatistic',
        ),
    ]
