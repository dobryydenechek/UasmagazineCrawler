# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os

import pytz
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('app')
app.config_from_object('app.celeryconfig')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'morning-auto-export': {
        'task': 'core.tasks.start_auto_export_task',
        'schedule': crontab(
            minute='0',
            hour='7',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*'),
    },
}


@app.task(bind=True, track_started=True)
def debug_task(self, timeout=None):
    # print('Request: {0!r}'.format(self.request))
    import time
    import random
    if timeout is None:
        timeout = random.randint(5, 30)
    time.sleep(timeout)
    return 'Success with timeout: {}'.format(timeout)


@app.task(bind=True, track_started=True)
def debug_task_cpubound(self, timeout=None):
    # print('Request: {0!r}'.format(self.request))
    import time
    import random
    if timeout is None:
        timeout = random.randint(5, 30)
    time.sleep(timeout)
    return 'Success with timeout: {}'.format(timeout)


@app.task(bind=True, track_started=True)
def debug_task_iobound(self, timeout=None):
    # print('Request: {0!r}'.format(self.request))
    import time
    import random
    if timeout is None:
        timeout = random.randint(5, 30)
    time.sleep(timeout)
    return 'Success with timeout: {}'.format(timeout)


@app.task(bind=True)
def debug_periodic_task(self, timeout=None):
    # print('Request: {0!r}'.format(self.request))
    import time
    import random
    if timeout is None:
        timeout = random.randint(5, 30)
    time.sleep(timeout)
    return 'Success with timeout: {}'.format(timeout)
