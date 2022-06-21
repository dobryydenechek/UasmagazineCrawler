# -*- coding: utf-8 -*-

import os
from django.conf import settings
from app.celery import app
from core.services.export_service import create_export
from core.services.scrapy_service import start_spider
from core.models import Export, Document, File


@app.task()
def start_spider_task(spider_id):
    return start_spider(spider_id)


@app.task()
def start_manual_export_task(export_id):
    create_export(export_id=export_id, export_type='manual')
    return True


@app.task()
def start_auto_export_task():
    create_export(export_id=None, export_type='auto')
    return True


@app.task()
def start_clear_storage(export_id):
    export = Export.objects.filter(id=export_id).first()
    if export:
        documents = Document.objects.filter(exported_archive=export)
        for document in documents:
            document.files.all().delete()
            document.delete()
        export.delete()
    return True
