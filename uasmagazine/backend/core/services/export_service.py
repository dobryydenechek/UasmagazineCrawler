# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta
import tempfile
import shutil
from os import path, mkdir, remove
from django.conf import settings
from shutil import copyfile
from ujson import dumps
import subprocess
from django.core.files import File

from core.models import Export, Document, Spider


def mark_exported_documents(export, documents):
    print ("Document cols %d" % len(documents))
    for document in documents:
        document.exported_archive = export
        document.save()


def create_export(export_id=None, export_type='auto'):
    now = datetime.now()

    if export_id:
        export = Export.objects.get(id=export_id)
    else:
        export = Export.objects.create(include_files=True, type=Export.TYPE_AUTO)

    if export_type == 'auto':
        export_name = 'Export %s' % (now - timedelta(days=1)).strftime('%d.%m.%Y %H:%M')
        last_export = Export.objects.all().exclude(id=export.id).last()
    elif export_type == 'manual':
        last_export = Export.objects.all().exclude(id=export.id).last()

        if last_export:
            export_name = 'Export %s - %s' % (
                last_export.created_date.strftime('%d.%m.%Y %H:%M'), now.strftime('%d.%m.%Y %H:%M'))
        else:
            export_name = 'Export %s' % now.strftime('%d.%m.%Y %H:%M')
    else:
        export_name = 'Export %s' % now.strftime('%d.%m.%Y %H:%M')
        last_export = None

    if not export.name:
        export.name = export_name

    last_export_date = None

    if last_export:
        last_export_date = last_export.created_date

    temp_dir = tempfile.mkdtemp('export')

    if last_export_date:
        documents = Document.objects.filter(created_date__lte=now, created_date__gt=last_export_date)
    else:
        documents = Document.objects.filter(created_date__lte=now)

    if export.include_files:
        mkdir(path.join(temp_dir, 'files'))
    document_cols = len(documents)

    formatted_documents = []
    for document in documents:
        files_path = list(document.files.values_list('path', flat=True))
        files = []

        for file_path in files_path:
            head, tail = path.split(file_path)

            full_path = path.join(settings.FILES_STORE, file_path)
            if path.exists(full_path):
                try:
                    copyfile(full_path, path.join(temp_dir, 'files', tail))
                    files.append(tail)
                except Exception:
                    pass

        formatted_documents.append({
            'author': document.author,
            'published_date': document.published_date,
            'url': document.url,
            'title': document.title,
            'text': document.text,
            'size': document.info.size if document.info else 0,
            'id': document.id,
            'files': files
        })

    documents_json = dumps(formatted_documents)
    documents_file_name = path.join(temp_dir, 'documents.json')

    with open(documents_file_name, 'w') as documents_file:
        documents_file.write(documents_json)

    document_cols_json = dumps({'doc_cols': document_cols})
    document_cols_file_name = path.join(temp_dir, 'document_cols.json')

    with open(document_cols_file_name, 'w') as document_cols_file:
        document_cols_file.write(document_cols_json)

    archive_file_name = '%s.7z' % export_name
    archive_file_name = archive_file_name.replace(' ', '_')
    archive_path = path.join(settings.STATIC_ROOT, archive_file_name).encode('utf-8')
    command_arguments = ['7z', 'a', '-m0=LZMA2:d64k:fb32', '-ms=8m', '-mmt=off', '-mx=0', '-o"%s"' % temp_dir, '-r',
                         archive_path, path.join(temp_dir, '*')]

    return_code = 100

    try:
        return_code = subprocess.call(command_arguments)
    except Exception as error:
        print (error, command_arguments)
    if return_code != 0:
        export.status = Export.STATUS_FAIL
        export.save()
        return False

    with open(archive_path, 'r') as archive_file:
        export.file = File(archive_file)
        export.created_date = now
        export.status = Export.STATUS_SUCCESS
        export.save()

    shutil.rmtree(temp_dir, ignore_errors=True)
    try:
        remove(archive_path)
    except Exception as error:
        print ("Can`t remove file %s" % str(error))
    mark_exported_documents(export, documents)

    return True
