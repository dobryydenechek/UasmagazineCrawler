# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from rest_framework import serializers
from core.models import Export
from core.tasks import start_manual_export_task


class ExportCreateListSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    def get_file_url(self, instance):
        file_name = os.path.basename(instance.file.name)
        relative_path = os.path.join(Export.FILE_UPLOAD_PATH, file_name)
        return relative_path

    class Meta(object):
        model = Export
        exclude = ('file',)

    def create(self, validated_data):
        export = Export(**validated_data)
        export.type = Export.TYPE_MANUAL
        export.save()
        start_manual_export_task.delay(export.id)

        return export
