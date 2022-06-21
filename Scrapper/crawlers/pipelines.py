# -*- coding: utf-8 -*-
from pytz import utc
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings
from sqlalchemy.orm import sessionmaker
from pytube import YouTube
from hashlib import sha1
import logging
from datetime import datetime
import random
import string
import os
import sys
from json import dumps

from crawlers.models import db_connect, create_tables, Document, File, Spider, AdditionalInformation


def get_session_key(length=50):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))


class SqlAlchemyPipeline(object):
    def __init__(self):
        engine = db_connect()
        create_tables(engine)
        self.Session = sessionmaker(bind=engine)

    def open_spider(self, spider):
        session = self.Session()
        settings = get_project_settings()
        spider_id = settings.get('spider_id')

        if spider_id:
            spider.spider_id = spider_id
            spider_info = session.query(Spider).filter_by(id=spider_id).first()
        else:
            spider_info = session.query(Spider).filter_by(name=spider.name).first()

            if not spider_info:
                spider_info = Spider(name=spider.name)
                session.add(spider_info)
                session.commit()

            spider.spider_id = spider_info.id

        spider.session_key = get_session_key()
        spider_info.last_session_key = spider.session_key
        spider_info.last_run_at = datetime.now().replace(tzinfo=utc)
        session.commit()

    def process_item(self, item, spider):
        session = self.Session()
        document_addit_info = AdditionalInformation(
            spider_id=spider.spider_id,
            is_file=False,
            size=item.get('size'),
            session_key=spider.session_key)

        document = Document(
            url=item.get('url'),
            published_date=item.get('date'),
            title=item.get('title'),
            author=item.get('author'),
            text=item.get('text'),
            spider_id=spider.spider_id,
            file_urls=item.get('file_urls'),
            image_urls=item.get('image_urls'),
            youtube_urls=item.get('youtube_urls'),
            info=document_addit_info
        )

        try:
            for file_info in item.get('files', []):
                file_addit_info = AdditionalInformation(
                    spider_id=spider.spider_id,
                    is_file=True,
                    size=file_info.get('size'),
                    session_key=spider.session_key)

                new_file = File(
                    spider_id=spider.spider_id,
                    url=file_info.get('url'),
                    path=file_info.get('path'),
                    checksum=file_info.get('checksum'),
                    info=file_addit_info
                )
                document.files.append(new_file)

            for image_info in item.get('images', []):
                image_addit_info = AdditionalInformation(
                    spider_id=spider.spider_id,
                    is_file=True,
                    size=image_info.get('size'),
                    session_key=spider.session_key)

                new_file = File(
                    spider_id=spider.spider_id,
                    url=image_info.get('url'),
                    path=image_info.get('path'),
                    checksum=image_info.get('checksum'),
                    info=image_addit_info,
                    type='image'
                )
                document.files.append(new_file)

            session.add(document)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item


class DuplicatesPipeline(object):
    name = None

    def __init__(self):
        engine = db_connect()
        create_tables(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()
#        document = session.query(Document).filter_by(url=item.get('url'), spider_id=spider.spider_id).first()
        document = session.query(Document).filter_by(url=item.get('url')).first()

        if document:
#            spider.crawler.engine.close_spider(self, reason='finished')
            session.close()
            raise DropItem('Duplicate item found: %s' % item)

        session.close()
        return item


class FilterYoutubeUrls(object):
    def process_item(self, item, spider):
        youtube_urls = item.get('youtube_urls')

        if not youtube_urls:
            return item

        item['youtube_urls'] = [url for url in youtube_urls if 'www.youtube.com' in url]

        return item


class YoutubePipeline(object):
    settings = get_project_settings()
    DOWNLOAD_YOUTUBE = settings.get('DOWNLOAD_YOUTUBE')
    FILES_STORE = settings.get('FILES_STORE')

    def process_item(self, item, spider):
        if not self.DOWNLOAD_YOUTUBE:
            return item

        youtube_urls = item.get('youtube_urls')

        if not youtube_urls:
            return item

        if not item.get('files'):
            item['files'] = []

        for url in youtube_urls:
            try:
                yt = YouTube(url)
                stream = yt.streams.filter(subtype='mp4').filter(progressive=True).first()
            except:
                logging.warning('%s video unavailable' % url)
                return item

            filename = sha1(url).hexdigest()
            stream.download(output_path=self.FILES_STORE, filename=filename)
            file_info = {'url': url, 'path': '%s.mp4' % filename, 'checksum': None}
            item['files'].append(file_info)
            logging.debug('Downloaded youtube video from %s' % url)

        return item


class FilterSoundcloudUrls(object):
    def process_item(self, item, spider):
        soundcloud_urls = item.get('soundcloud_urls')

        if not soundcloud_urls:
            return item

        item['soundcloud_urls'] = [url for url in soundcloud_urls if 'soundcloud.com' in url]

        return item


class SetFileSize(object):
    settings = get_project_settings()
    FILES_STORE = settings.get('FILES_STORE')

    def process_item(self, item, spider):
        files = item.get('files', [])
        updated_files = []

        for file_info in files:
            file_path = os.path.join(self.FILES_STORE, file_info.get('path'))

            if not os.path.exists(file_path):
                continue

            stat_info = os.stat(file_path)
            file_info['size'] = stat_info.st_size
            updated_files.append(file_info)

        item['files'] = updated_files

        return item


class SetImageSize(object):
    settings = get_project_settings()
    FILES_STORE = settings.get('FILES_STORE')

    def process_item(self, item, spider):
        images = item.get('images', [])
        updated_images = []

        for image in images:
            file_path = os.path.join(self.FILES_STORE, image.get('path'))

            if not os.path.exists(file_path):
                continue

            stat_info = os.stat(file_path)
            image['size'] = stat_info.st_size
            updated_images.append(image)

        item['images'] = updated_images

        return item


class SetDocumentSize(object):
    def process_item(self, item, spider):
        dict_item = dict(item)
        date = dict_item.get('date')

        if date:
            dict_item['date'] = date.isoformat()

        dumps_item = dumps(dict_item)
        item_size = sys.getsizeof(dumps_item)
        item['size'] = item_size

        return item
