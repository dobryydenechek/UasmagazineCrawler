# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from core.api.spider.serializers import SpiderSerializer
from core.models import File


class FileSerializer(serializers.ModelSerializer):
    spider = SpiderSerializer(source='core_spider', many=False, required=False)

    class Meta:
        model = File
        fields = '__all__'

    def __init__(self, **kwargs):
        super(FileSerializer, self).__init__()
