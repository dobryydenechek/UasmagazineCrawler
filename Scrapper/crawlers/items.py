# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DocumentItem(scrapy.Item):
    url = scrapy.Field()
    author = scrapy.Field()
    date = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    file_urls = scrapy.Field()
    files = scrapy.Field()
    youtube_urls = scrapy.Field()
    soundcloud_urls = scrapy.Field()
    size = scrapy.Field()
