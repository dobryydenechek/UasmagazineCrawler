# -*- coding: utf-8 -*-
from scrapy.http import Request
from scrapy.spiders import CrawlSpider
from urlparse import urljoin
from dateutil.parser import parse
from lxml import etree
from urllib import urlencode
from json import loads

from crawlers.items import DocumentItem


class ScrapeNasa(CrawlSpider):
    name = 'nasa'
    host = 'https://www.nasa.gov'
    images_public = 'https://www.nasa.gov/sites/default/files/styles/ubernode_alt_horiz/public/'
    start_url = '%s/api/2/ubernode/_search' % host
    params = {
        'from': 0,
        'size': 24,
        'sort': 'promo-date-time:desc',
        'q': '(routes:1)',
        '_source_include': 'promo-date-time',
    }

    def start_requests(self):
        start_url = '%s?%s' % (self.start_url, urlencode(self.params))
        yield Request(url=start_url, callback=self.parse)

    def parse(self, response):
        json_response = loads(response.body)
        hits = json_response.get('hits')

        if not hits:
            return

        documents = hits.get('hits', [])

        if not documents:
            self.logger.error('Missing documents')

        for document in documents:
            document_id = document.get('_id')
            url = '%s/api/2/ubernode/%s' % (self.host, document_id)
            yield Request(url, callback=self.parse_item)

        if documents:
            self.params['from'] += 24
            next_url = '%s?%s' % (self.start_url, urlencode(self.params))
            yield Request(url=next_url, callback=self.parse)

    def parse_item(self, response):
        item = DocumentItem()
        text_delimiter = self.settings.get('TEXT_DELIMITER')
        json_response = loads(response.body)
        source = json_response.get('_source')

        item['url'] = urljoin(response.url, source.get('uri'))
        item['title'] = source.get('title')
        item['date'] = parse(source.get('promo-date-time'))
        item['author'] = source.get('name')
        html_body = source.get('body', '')
        html_content = '<html lang="en">%s</html>' % html_body
        parser = etree.HTMLParser(recover=True)
        content = etree.fromstring(html_content, parser=parser)
        text_blocks = content.xpath('//text()')
        item['text'] = text_delimiter.join([text_block.strip() for text_block in text_blocks])

        images = [urljoin(self.host, href.replace('\\"', '')) for href in response.xpath('//img/@src').extract()]
        iframe_urls = response.xpath('//iframe/@src').extract()
        item['youtube_urls'] = [iframe_url.replace('\\"//', '').replace('\\"', '') for iframe_url in iframe_urls]
        item['soundcloud_urls'] = [iframe_url.replace('\\"//', '').replace('\\"', '') for iframe_url in iframe_urls]
        master_image = source.get('master-image')

        if master_image:
            image_url = master_image.get('uri', '').replace('public://', self.images_public)
            images = [image_url] + images

        item['image_urls'] = images

        yield item
