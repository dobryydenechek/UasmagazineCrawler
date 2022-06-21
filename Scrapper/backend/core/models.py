# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.db import models
from django.dispatch import receiver
from django.conf import settings
from django.contrib.postgres.fields import ArrayField, JSONField
from django_celery_beat.models import PeriodicTask


class Export(models.Model):
    FILE_UPLOAD_PATH = 'static/export/'

    STATUS_IN_PROGRESS = 1
    STATUS_SUCCESS = 2
    STATUS_FAIL = 3
    STATUS_DOWNLOADED = 4

    STATUS_CHOICE = (
        (STATUS_IN_PROGRESS, 'В процессе'),
        (STATUS_SUCCESS, 'Успешно'),
        (STATUS_FAIL, 'Ошибка'),
        (STATUS_DOWNLOADED, 'Скачано'),
    )

    TYPE_AUTO = 1
    TYPE_MANUAL = 2

    TYPE_CHOICE = (
        (TYPE_AUTO, 'Автоматический'),
        (TYPE_MANUAL, 'Ручной'),
    )

    name = models.CharField(max_length=1000, null=True)
    deleting = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    file = models.FileField(upload_to=FILE_UPLOAD_PATH, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICE, null=True, default=STATUS_IN_PROGRESS)
    include_files = models.BooleanField(default=True)
    type = models.IntegerField(choices=TYPE_CHOICE, null=True, default=TYPE_AUTO)

    def __str__(self):
        return '{name} {created_date}'.format(name=self.name,
                                              created_date=self.created_date.strftime('%Y-%m-%d_%H:%M:%S'))

    def __unicode__(self):
        return u'{name} {created_date}'.format(name=self.name,
                                               created_date=self.created_date.strftime('%Y-%m-%d_%H:%M:%S'))

    def delete(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, self.file.path)
        os.remove(file_path)

        super(Export, self).delete()


class Spider(models.Model):
    EVERY_DAYS = 'days'
    EVERY_HOURS = 'hours'
    EVERY_MINUTES = 'minutes'
    EVERY_SECONDS = 'seconds'

    INTERVAL_CHOICE = (
        (EVERY_DAYS, 'Каждый день'),
        (EVERY_HOURS, 'Каждый час'),
        (EVERY_MINUTES, 'Каждую минуту'),
        (EVERY_SECONDS, 'Каждую секунду'),
    )

    STATUS_STARTED = 1
    STATUS_STOPPED = 2

    ADDITIONAL_STATUS_STOPPING = 1
    ADDITIONAL_STATUS_PENDING = 2
    ADDITIONAL_STATUS_RUNNING = 3
    ADDITIONAL_STATUS_FINISHED = 4

    STATUS_CHOICE = (
        (STATUS_STARTED, 'Запущен'),
        (STATUS_STOPPED, 'Остановлен'),
    )

    ADDITIONAL_STATUS_CHOICE = (
        (ADDITIONAL_STATUS_STOPPING, 'Останавливается'),
        (ADDITIONAL_STATUS_PENDING, 'В ожидании'),
        (ADDITIONAL_STATUS_RUNNING, 'Работает'),
        (ADDITIONAL_STATUS_FINISHED, 'Завершен'),
    )

    # Остановлен = STATUS_STOPPED & ADDITIONAL_STATUS_FINISHED
    # Запущен    = ВСЕ ОСТАЛЬНОЕ

    name = models.CharField(max_length=50)
    start_every_amount = models.IntegerField(null=True)
    start_every_type = models.CharField(choices=INTERVAL_CHOICE, max_length=20, null=True)
    schedule = models.ForeignKey(PeriodicTask, null=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICE, null=True, default=STATUS_STARTED)
    additional_status = models.IntegerField(choices=ADDITIONAL_STATUS_CHOICE, null=True,
                                            default=ADDITIONAL_STATUS_PENDING)
    last_run_at = models.DateTimeField(null=True)
    last_session_key = models.CharField(max_length=50, null=True)

    def __str__(self):
        return '{id} {name}'.format(name=self.name, id=self.id)

    def __unicode__(self):
        return u'{id} {name}'.format(name=self.name, id=self.id)


class AdditionalInformation(models.Model):
    spider = models.ForeignKey(Spider)
    is_file = models.BooleanField(default=False)
    size = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    session_key = models.CharField(max_length=50, null=True)

    def __str__(self):
        return '{spider}'.format(spider=self.spider)

    def __unicode__(self):
        return u'{spider}'.format(spider=self.spider)


class File(models.Model):
    type = models.CharField(max_length=50)
    spider = models.ForeignKey(Spider, on_delete=models.SET_NULL, null=True)
    url = models.URLField(max_length=4096, default=str(), blank=True, null=True)
    path = models.CharField(max_length=200, null=True)
    checksum = models.CharField(max_length=50, null=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    info = models.ForeignKey(AdditionalInformation, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return '{spider} {url}'.format(spider=self.spider, url=self.url)

    def __unicode__(self):
        return u'{spider} {url}'.format(spider=self.spider, url=self.url)


@receiver(models.signals.post_delete, sender=File)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.path:
        file_path = os.path.join(settings.FILES_STORE, instance.path)
        if os.path.isfile(file_path):
            os.remove(file_path)


# TODO: На будущее: заменить files = models.ManyToManyField
# TODO: на models.ForeignKey
class Document(models.Model):
    spider = models.ForeignKey(Spider, on_delete=models.SET_NULL, null=True)
    url = models.URLField(max_length=4096, default=str(), blank=True, null=True)
    author = models.CharField(max_length=300, null=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    published_date = models.DateTimeField(auto_now_add=True, null=True)
    title = models.CharField(max_length=1000, null=True)
    text = models.TextField(null=True)
    files = models.ManyToManyField(File, blank=True, related_name='files')
    exported_archive = models.ForeignKey(Export, null=True, on_delete=models.SET_NULL)
    file_urls = ArrayField(models.URLField(max_length=4096, default=str(), blank=True, null=True), null=True)
    image_urls = ArrayField(models.URLField(max_length=4096, default=str(), blank=True, null=True), null=True)
    youtube_urls = ArrayField(models.URLField(max_length=4096, default=str(), blank=True, null=True), null=True)
    soundcloud_urls = ArrayField(models.URLField(max_length=4096, default=str(), blank=True, null=True), null=True)
    info = models.ForeignKey(AdditionalInformation, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return '{spider} {title}'.format(spider=self.spider, title=self.title)

    def __unicode__(self):
        return u'{spider} {title}'.format(spider=self.spider, title=self.title)


class Error(models.Model):
    spider = models.ForeignKey(Spider)
    url = models.URLField(max_length=4096, default=str(), blank=True, null=True)
    exception = models.CharField(max_length=1000, null=True)
    traceback = models.TextField(null=True)
    response = JSONField()
    created_date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return '{spider} {exception}'.format(spider=self.spider, exception=self.exception)

    def __unicode__(self):
        return u'{spider} {exception}'.format(spider=self.spider, exception=self.exception)
