# -*- coding: utf-8 -*-

from scrapyd_api import ScrapydAPI
from django.conf import settings
from scrapyd_api.exceptions import ScrapydResponseError
from django_celery_beat.models import IntervalSchedule, PeriodicTask, CrontabSchedule
from json import dumps
from datetime import datetime
import pytz

from django.db.models import Sum
from core.models import Spider, Document, File, Error, AdditionalInformation

scrapyd = ScrapydAPI(settings.SCRAPYD_URL)


def add_egg(egg_file):
    try:
        project_name = settings.SCRAPY_PROJECT
        version_name = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        spiders_count = scrapyd.add_version(project_name, version_name, egg_file.read())
        sync_scrapy_spiders(project_name=project_name)
        return spiders_count
    except ScrapydResponseError:
        print('Scrapyd Error')
        return 0


def remove_scrapy_project(project_name):
    result = scrapyd.delete_project(project_name)
    return result


def sync_scrapy_projects():
    pass


def sync_scrapy_spiders(project_name):
    spiders = scrapyd.list_spiders(project_name)

    for spider in spiders:
        spider, created = Spider.objects.get_or_create(name=spider)

        if spider.status == Spider.STATUS_STOPPED:
            continue

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
                minute='*',
                hour='*/23',
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
        spider.save()
#        spider_statistic, created = SpiderStatistic.objects.get_or_create(spider_id=spider.id)

        start_spider(spider.id)

    return len(spiders)


def start_spider(spider_id):
    spider = Spider.objects.filter(id=spider_id).first()

    if not spider:
        return False

    spider_settings = {'spider_id': spider_id}

    try:
        scrapyd.schedule(settings.SCRAPY_PROJECT, spider.name, settings=spider_settings)
    except Exception as error:
        print "START CRAWLER ERROR", error
        return False

    return True


def calc_sizes(spider):
    total_size = AdditionalInformation.objects.filter(spider_id=spider.id).aggregate(Sum('size'))
    session_size = AdditionalInformation.objects.filter(
        spider_id=spider.id,
        session_key=spider.last_session_key).aggregate(Sum('size'))

    total_size = total_size.get('size__sum') if total_size.get('size__sum') else 0
    session_size = session_size.get('size__sum') if session_size.get('size__sum') else 0

    return session_size, total_size


def color(spider, last_24_hour, color_filter):
    error_count = Error.objects.filter(spider_id=spider.id, created_date__gte=last_24_hour).count()
    document_count = Document.objects.filter(spider_id=spider.id, created_date__gte=last_24_hour).count()

    spider_color = 'green'

    if not document_count:
        spider_color = 'yellow'

    if error_count:
        spider_color = 'red'

    if spider_color not in color_filter:
        return None

    return spider_color


# TODO: ДАННОЕ РЕШЕНИЕ ВРЕМЕННОЕ
# TODO: НЕОБХОДИМО ХРАНИТЬ СТАТУС В МОДЕЛЯХ
# TODO: И СЧИТЫВАТЬ ИХ ИЗ МОДЕЛЕЙ, НО
# TODO: НИКАК НЕ НА ПРЯМУЮ ИЗ SCRAPYD
def spiders_status(spiders, last_24_hour, color_filter):
    try:
        spiders_list = list(spiders)
    except Exception:
        return None
    if not len(spiders_list):
        return None

    jobs = scrapyd.list_jobs(settings.SCRAPY_PROJECT)

    running_list = set([spider_name.get('spider') for spider_name in jobs.get('running')])
    pending_list = set([spider_name.get('spider') for spider_name in jobs.get('pending')])
    finished_list = set([spider_name.get('spider') for spider_name in jobs.get('finished')])

    spiders_statuses = []

    for spider in spiders_list:
        statistic = {}

        spider_color = color(spider, last_24_hour, color_filter)
        if spider_color is None:
            continue

        session_size, total_size = calc_sizes(spider)
        statistic.update({"status": spider.status,
                          "session_size": session_size,
                          "name": spider.name,
                          "last_run_at": spider.last_run_at,
                          "total_size": total_size,
                          "color": spider_color,
                          "id": spider.id})

        spider_name = spider.name
        if spider.additional_status == Spider.ADDITIONAL_STATUS_STOPPING and spider_name in running_list:
            statistic.update({'state': Spider.ADDITIONAL_STATUS_STOPPING})

        elif spider_name in running_list:
            spider.additional_status = Spider.ADDITIONAL_STATUS_RUNNING
            statistic.update({'state': Spider.ADDITIONAL_STATUS_RUNNING})

        elif spider_name in pending_list:
            spider.additional_status = Spider.ADDITIONAL_STATUS_PENDING
            statistic.update({'state': Spider.ADDITIONAL_STATUS_PENDING})

        elif spider_name in finished_list:
            spider.additional_status = Spider.ADDITIONAL_STATUS_FINISHED
            statistic.update({'state': Spider.ADDITIONAL_STATUS_FINISHED})

        spider.save()
        spiders_statuses.append(statistic)

    return spiders_statuses


def reset_spider(spider):
    spider_name = spider.name
    jobs = scrapyd.list_jobs(settings.SCRAPY_PROJECT).get('running')

    for job in jobs:
        if job.get('spider') == spider_name:
            scrapyd.cancel(settings.SCRAPY_PROJECT, job.get('id'))

    return True
