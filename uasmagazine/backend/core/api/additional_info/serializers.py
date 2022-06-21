# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_celery_beat.models import IntervalSchedule, PeriodicTask, CrontabSchedule
from rest_framework import serializers
from json import dumps
import pytz

from core.models import AdditionalInformation


class AdditionalInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalInformation
        fields = '__all__'

    def __init__(self, **kwargs):
        super(AdditionalInformationSerializer, self).__init__()
