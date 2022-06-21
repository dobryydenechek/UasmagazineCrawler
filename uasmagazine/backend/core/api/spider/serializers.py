# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_celery_beat.models import IntervalSchedule, PeriodicTask, CrontabSchedule
from rest_framework import serializers
from json import dumps
import pytz

from core.models import Spider


class SpiderCreateListSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Spider
        fields = '__all__'

    def create(self, validated_data):
        spider = Spider(**validated_data)

        if spider.start_every_amount and spider.start_every_type:
            interval, created = IntervalSchedule.objects.get_or_create(
                every=spider.start_every_amount,
                period=spider.start_every_type,
            )
            schedule, created = PeriodicTask.objects.get_or_create(
                interval=interval,
                name='%s %s' % (spider.name, interval.id),
                task='core.tasks.start_spider_task',
                args=dumps([spider.id]),
            )
        else:
            cron_tab, _ = CrontabSchedule.objects.get_or_create(
                minute='00',
                hour='5',
                day_of_week='*',
                day_of_month='*',
                month_of_year='*',
                timezone=pytz.timezone('Europe/Moscow'))
            schedule, created = PeriodicTask.objects.get_or_create(
                crontab=cron_tab,
                name='%s %s' % (spider.name, cron_tab.id),
                task='core.tasks.start_spider_task',
                args=dumps([spider.id]),
            )
        spider.schedule_id = schedule.id
        spider.status = 1
        spider.save()

        return spider


class SpiderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spider
        fields = '__all__'

    def __init__(self, **kwargs):
        super(SpiderSerializer, self).__init__()
