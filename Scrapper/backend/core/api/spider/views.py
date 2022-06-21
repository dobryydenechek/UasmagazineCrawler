# -*- coding: utf-8 -*-

from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import JsonResponse
from rest_framework import status
from datetime import datetime, timedelta
from rest_framework.viewsets import ModelViewSet
from django.db.models import Sum
from django.db.models import Q
from operator import itemgetter
from json import dumps
import pytz

from core.api.spider.serializers import SpiderCreateListSerializer
from core.models import Spider, AdditionalInformation, Error, File
from core.services.scrapy_service import start_spider, add_egg, spiders_status, reset_spider


class SpiderViewSet(ModelViewSet):
    queryset = Spider.objects.all()
    serializer_class = SpiderCreateListSerializer
    model = Spider

    def destroy(self, request, *args, **kwargs):
        spider_id = int(kwargs['pk'])
        spider = Spider.objects.filter(pk=spider_id, status=2,
                                       additional_status=Spider.ADDITIONAL_STATUS_FINISHED).first()

        if spider:
            pt = PeriodicTask.objects.filter(id=spider.schedule_id).first()
            if pt:
                pt.delete()
            spider.delete()

        return Response(status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        PeriodicTask.objects.filter(id=instance.schedule_id).delete()
        return instance

    @action(detail=True, methods=['get'])
    def document_statistics(self, request, *args, **kwargs):
        request_sort = request.GET.get('sort')
        request_limit = request.GET.get('limit', 5)
        request_offset = request.GET.get('offset', 0)
        request_spider_name = request.GET.get('spider_name')
        sort_reverse = False

        if request_sort and request_sort.startswith('-'):
            sort_reverse = True
            request_sort = request_sort[1:]

        if request_sort and request_sort not in ['last_1_hour', 'last_12_hour', 'last_24_hour', 'last_7_days', 'name']:
            request_sort = None

        if request_limit:
            request_limit = int(request_limit)

        if request_offset:
            request_offset = int(request_offset)

        now = datetime.now()
        last_1_hour = now - timedelta(hours=1)
        last_12_hour = now - timedelta(hours=12)
        last_24_hour = now - timedelta(hours=24)
        last_7_days = now - timedelta(days=7)
        statistics_intervals = {
            'last_1_hour': last_1_hour,
            'last_12_hour': last_12_hour,
            'last_24_hour': last_24_hour,
            'last_7_days': last_7_days,
        }
        results = []

        if request_spider_name:
            spiders = Spider.objects.filter(name__icontains=request_spider_name)
        else:
            spiders = Spider.objects.filter()

        for spider in spiders:
            spider_stats = {'id': spider.id, 'name': spider.name}

            for key, interval in statistics_intervals.items():
                count = AdditionalInformation.objects.filter(spider_id=spider.id, is_file=False, created_date__gte=interval).count()
                spider_stats[key] = count

            results.append(spider_stats)

        if request_sort:
            results = sorted(results, key=itemgetter(request_sort), reverse=sort_reverse)

        count = len(results)
        to_interval = request_limit + request_offset if request_offset else request_limit

        return JsonResponse({'result': results[request_offset: to_interval], 'count': count})

    @action(detail=True, methods=['get'])
    def status(self, request, *args, **kwargs):

        color_filter = ['green', 'yellow', 'red']
        request_status = request.GET.get('status')

        request_color = request.GET.get('color')
        request_spider_name = request.GET.get('spider_name')
        request_sort = request.GET.get('sort')
        request_limit = request.GET.get('limit', 5)
        request_offset = request.GET.get('offset', 0)
        sort_reverse = False

        if request_color:
            color_filter = [request_color]

        if request_sort and request_sort.startswith('-'):
            sort_reverse = True
            request_sort = request_sort[1:]

        if request_sort and request_sort not in ['total_size', 'session_size', 'name', 'last_run_at']:
            request_sort = None

        if request_limit:
            request_limit = int(request_limit)

        if request_offset:
            request_offset = int(request_offset)

        now = datetime.now()
        last_24_hour = now - timedelta(hours=24)

        if int(request_status) == 2:
            if request_spider_name:
                spiders = Spider.objects.filter(status=2,
                                                additional_status=Spider.ADDITIONAL_STATUS_FINISHED,
                                                name=request_spider_name)
            else:
                spiders = Spider.objects.filter(status=2,
                                                additional_status=Spider.ADDITIONAL_STATUS_FINISHED)
        else:
            if request_spider_name:
                spiders = Spider.objects.filter(name=request_spider_name).exclude(
                    status=2, additional_status=Spider.ADDITIONAL_STATUS_FINISHED)
            else:
                spiders = Spider.objects.exclude(status=2,
                                                 additional_status=Spider.ADDITIONAL_STATUS_FINISHED)

        results = spiders_status(spiders, last_24_hour, color_filter)
        if not results:
            results = []

        if request_sort:
            if request_sort == 'last_run_at':
                no_last_run_at = [result for result in results if not result.get('last_run_at')]
                with_last_run_at = [result for result in results if result.get('last_run_at')]
                results = sorted(with_last_run_at, key=itemgetter(request_sort), reverse=sort_reverse)

                if sort_reverse:
                    results += no_last_run_at
                else:
                    results = no_last_run_at + results
            else:
                results = sorted(results, key=itemgetter(request_sort), reverse=sort_reverse)

        for result in results:
            if result.get('last_run_at'):
                result['last_run_at'] = result.get('last_run_at').isoformat()

        count = len(results)
        to_interval = request_limit + request_offset if request_offset else request_limit

        response = JsonResponse({'result': results[request_offset: to_interval], 'count': count})

        return response

    @action(detail=False, methods=['post'])
    def start(self, request, *args, **kwargs):
        spider_id = kwargs.get('pk')
        spider = Spider.objects.filter(id=spider_id).first()

        if not spider:
            return JsonResponse({'result': False})

        if spider.start_every_amount and spider.start_every_type:
            interval, created = IntervalSchedule.objects.get_or_create(
                every=spider.start_every_amount,
                period=spider.start_every_type,
            )
            schedule, created = PeriodicTask.objects.get_or_create(
                interval=interval,
                name='%s %s' % (spider.name, interval.id),
                task='core.tasks.start_spider_task',
                args=dumps([spider.id]),
            )
        else:
            cron_tab, _ = CrontabSchedule.objects.get_or_create(
                minute='00',
                hour='5',
                day_of_week='*',
                day_of_month='*',
                month_of_year='*',
                timezone=pytz.timezone('Europe/Moscow'))
            schedule, created = PeriodicTask.objects.get_or_create(
                crontab=cron_tab,
                name='%s %s' % (spider.name, cron_tab.id),
                task='core.tasks.start_spider_task',
                args=dumps([spider.id]),
            )

        spider.schedule_id = schedule.id
        spider.status = 1
        spider.save()
        result = start_spider(spider_id=spider_id)

        return JsonResponse({'result': result})

    @action(detail=False, methods=['post'])
    def stop(self, request, *args, **kwargs):
        spider_id = kwargs.get('pk')
        spider = Spider.objects.filter(id=spider_id).first()

        if not spider:
            return JsonResponse({'result': False})

        schedule_id = spider.schedule_id
        spider.schedule_id = None
        spider.status = Spider.STATUS_STOPPED
        spider.additional_status = Spider.ADDITIONAL_STATUS_STOPPING
        spider.save()

        pt = PeriodicTask.objects.filter(id=schedule_id).first()
        if pt:
            pt.delete()

        return JsonResponse({'result': True})

    @action(detail=False, methods=['post'])
    def reset(self, request, *args, **kwargs):
        spider_id = kwargs.get('pk')
        spider = Spider.objects.filter(id=spider_id).first()

        if not spider:
            return JsonResponse({'result': False})

        schedule_id = spider.schedule_id
        spider.schedule_id = None
        spider.status = Spider.STATUS_STOPPED
        spider.additional_status = Spider.ADDITIONAL_STATUS_STOPPING
        spider.save()

        pt = PeriodicTask.objects.filter(id=schedule_id).first()
        if pt:
            pt.delete()

        if reset_spider(spider):
            return JsonResponse({'result': True})
        else:
            return JsonResponse({'result': False})

    @action(detail=False, methods=['post'])
    def add_spiders(self, request, *args, **kwargs):
        files = request.FILES

        if 'egg' not in files:
            return JsonResponse({'result': False})

        spiders_count = add_egg(egg_file=files['egg'])

        return JsonResponse({'result': True, 'count': spiders_count})
