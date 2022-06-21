# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from core.models import Document, File, Error, Spider, Export

admin.site.register(Document)
admin.site.register(File)
admin.site.register(Error)
admin.site.register(Spider)
admin.site.register(Export)
