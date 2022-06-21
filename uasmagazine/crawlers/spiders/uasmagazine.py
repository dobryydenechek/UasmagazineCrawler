# -*- coding: utf-8 -*-
from scrapy.http import Request
from scrapy.spiders import CrawlSpider
from urlparse import urljoin
from dateutil.parser import parse
from datetime import datetime

from crawlers.items import DocumentItem


class ScrapeUasmagazine(CrawlSpider):
    name = 'uasmagazine'
    start_urls = ['http://uasmagazine.com/']

    def parse(self, response):
        articles_page_path = '//*[@class="readMoreArticles"]/a/@href'
        articles_page_url = response.xpath(articles_page_path).extract_first()

        if not articles_page_url:
            self.logger.error('Missing articles page')

        if articles_page_url:
            yield response.follow(articles_page_url, callback=self.parse_articles_page)

    def parse_articles_page(self, response):
        next_page_path = '//*[@id="browse"]/p[1]/a[@rel="next"]/@href'
        article_blocks_path = '//*[@class="newsListing"]//h2/a/@href'
        article_urls = response.xpath(article_blocks_path).extract()

        for article_url in article_urls:
            url = urljoin(response.url, article_url)
            yield Request(url, callback=self.parse_item)

        next_page_url = response.xpath(next_page_path).extract_first()

        if next_page_url and article_urls:
            yield response.follow(next_page_url, callback=self.parse_articles_page)

    def parse_item(self, response):
        item = DocumentItem()
        title_path = '//*[@class="post"]/h1/text()'
        author_path = '//*[@class="post"]/div[@class="author"]'
        text_path = '//*[@class="body"]//p//text()'
        images_path = '//*[@id="imageGallery"]//img/@src'
        item['url'] = response.request.url
        title = response.xpath(title_path).extract_first()

        if title:
            item['title'] = title.strip()
        else:
            item['title'] = ''
            self.logger.error('Missing title')

        author_block = response.xpath(author_path)

        if author_block:
            date = author_block.xpath('text()[2]').extract_first()
            date = date.replace('|', '')
            author = author_block.xpath('a/text()').extract_first()
        else:
            author_path = '//*[@class="post"]/div[@class="author"]/text()'
            author, date = response.xpath(author_path).extract_first().split('|')

            if author.startswith('By'):
                author = author[2:]

        if date:
            item['date'] = parse(date)
        else:
            item['date'] = datetime.utcnow()
            self.logger.error('Missing date')

        item['author'] = author.strip()
        text_blocks = response.xpath(text_path).extract()
        text_delimiter = self.settings.get('TEXT_DELIMITER')

        if text_blocks:
            item['text'] = text_delimiter.join([text_block.strip() for text_block in text_blocks])
        else:
            item['text'] = ''

        images_urls = [urljoin(response.url, href) for href in response.xpath(images_path).extract()]
        item['image_urls'] = images_urls

        yield item
