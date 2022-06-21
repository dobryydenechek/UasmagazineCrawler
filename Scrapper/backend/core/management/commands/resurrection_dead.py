# -*- coding: utf-8 -*-

from django.core.management import BaseCommand
from django.conf import settings
from scrapyd_api import ScrapydAPI

from core.models import Spider
from core.services.scrapy_service import start_spider

scrapyd = ScrapydAPI(settings.SCRAPYD_URL)


class Command(BaseCommand):

    def handle(self, *args, **options):
        jobs = scrapyd.list_jobs(settings.SCRAPY_PROJECT)

        running_list = set([spider_name.get('spider') for spider_name in jobs.get('running')])
        pending_list = set([spider_name.get('spider') for spider_name in jobs.get('pending')])
        finished_list = set([spider_name.get('spider') for spider_name in jobs.get('finished')])

        spiders = Spider.objects.values('id', 'name').exclude(
            status=2,
            additional_status=Spider.ADDITIONAL_STATUS_FINISHED)

        for spider in spiders:
            if spider.get('name') in running_list:
                continue
            if spider.get('name') in pending_list:
                continue
            if spider.get('name') in finished_list:
                continue

            start_spider(spider.get('id'))
