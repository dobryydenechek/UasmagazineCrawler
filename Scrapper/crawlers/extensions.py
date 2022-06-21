# -*- coding: utf-8 -*-
from sqlalchemy.orm import sessionmaker
from scrapy import signals
from scrapy.utils.reqser import request_to_dict
import time
from six import StringIO

from crawlers.models import db_connect, create_tables, Error


def response_to_dict(response, spider, include_request=True, **kwargs):
    response_dict = {
        'time': time.time(),
        'status': response.status,
        'url': response.url,
        'headers': dict(response.headers),
        'body': response.body,
    }

    if include_request:
        response_dict['request'] = request_to_dict(response.request, spider)

    return response_dict


class SaveErrorsExtension(object):
    def __init__(self, crawler):
        crawler.signals.connect(self.spider_error, signal=signals.spider_error)
        engine = db_connect()
        create_tables(engine)
        self.Session = sessionmaker(bind=engine)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_exception(self, request, exception, spider):
        pass  # TODO check later

    def process_spider_exception(self, response, exception, spider):
        pass  # TODO check later

    def spider_error(self, failure, response, spider,
                     signal=None, sender=None, *args, **kwargs):
        traceback = StringIO()
        failure.printTraceback(file=traceback)
        # traceback = '\n'.join(traceback.getvalue().split('\n')[-5:])
        traceback = traceback.getvalue()
        res_dict = response_to_dict(response, spider, include_request=True)
        exception = '%s: %s' % (type(failure.value).__name__, failure.value.message)

        session = self.Session()
        error = Error(
            url=response.url,
            spider_id=spider.spider_id,
            response=res_dict,
            traceback=traceback,
            exception=exception
        )

        session.add(error)
        session.commit()
        session.close()
