# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from core.api.file.serializers import FileSerializer
from core.api.spider.serializers import SpiderSerializer
from core.api.additional_info.serializers import AdditionalInformationSerializer
from core.models import Document, File


class DocumentExportSerializer(serializers.ModelSerializer):
    files = FileSerializer(queryset=File.objects.all(), many=True, required=False)
    spider = SpiderSerializer(source='core_spider', many=False, required=False)
    info = AdditionalInformationSerializer(source='core_size', many=False, required=False)

    class Meta:
        model = Document
        fields = '__all__'
