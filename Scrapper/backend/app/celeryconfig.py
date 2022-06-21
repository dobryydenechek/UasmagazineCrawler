# -*- coding: utf-8 -*-
from django.conf import settings

broker_url = settings.CELERY_BROKER_URL
# broker_use_ssl = False
# broker_transport_options = {}
broker_heartbeat = 30

task_default_queue = 'default'
task_default_exchange = 'default'
task_default_exchange_type = 'direct'
task_default_routing_key = 'default'

task_queues = {
    'default': {
        'exchange': 'default',
        'routing_key': 'default',
    },
    'low': {
        'exchange': 'low',
        'routing_key': 'low',
    },
    'normal': {
        'exchange': 'normal',
        'routing_key': 'normal',
    },
    'high': {
        'exchange': 'high',
        'routing_key': 'high',
    }
}

task_ignore_result = False
task_track_started = True

# Temporary disabled
# task_time_limit = 1200
# task_soft_time_limit = 300

task_acks_late = True
task_send_sent_event = True
# task_default_rate_limit = '1/s'

result_backend = 'django-db'
result_persistent = True
# result_backend_transport_options = {}
result_expires = 0

accept_content = ['json']
task_serializer = 'json'
result_serializer = 'json'
content_encoding = 'utf-8'
timezone = 'Europe/Moscow'
enable_utc = True

# TODO: Need experiment
worker_pool = 'solo'  # Don't know why recommend solo
worker_concurrency = 1
worker_prefetch_multiplier = 1

# worker_pool_restarts = False
worker_disable_rate_limits = True

worker_enable_remote_control = True
worker_send_task_events = True

worker_lost_wait = 30
worker_max_tasks_per_child = 1 #  Test
worker_max_memory_per_child = 2000 * 1024  # Test 2000mb

celery_imports = ['backend.app.tasks']
