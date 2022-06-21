# -*- coding: utf-8 -*-

from rest_framework.viewsets import ModelViewSet

from core.api.export.serializers import ExportCreateListSerializer
from core.tasks import start_clear_storage
from core.models import Export
from rest_framework.response import Response
from rest_framework import status


class ExportViewSet(ModelViewSet):
    queryset = Export.objects.all()
    serializer_class = ExportCreateListSerializer
    model = Export

    def destroy(self, request, *args, **kwargs):
        export_id = int(kwargs['pk'])
        if export_id:
            export = Export.objects.filter(id=export_id).first()
            if export:
                export.deleting = True
                export.save()
                start_clear_storage.delay(export_id)

        return Response(status=status.HTTP_200_OK)

    def get_queryset(self):
        return Export.objects.filter(deleting=False)
