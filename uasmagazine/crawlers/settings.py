# -*- coding: utf-8 -*-
import os

BOT_NAME = 'crawlers'
SPIDER_MODULES = ['crawlers.spiders']
NEWSPIDER_MODULE = 'crawlers.spiders'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36'
ROBOTSTXT_OBEY = False
TEXT_DELIMITER = ' '

DATABASE = {
    'drivername': 'postgres',
    'host': os.getenv('POSTGRES_HOSTNAME', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'username': os.getenv('POSTGRES_USERNAME', 'crawlers'),
    'password': os.getenv('POSTGRES_PASSWORD', 'qwerty123'),
    'database': os.getenv('POSTGRES_DB_NAME', 'crawlers')
}

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'
}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 10,
}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'crawlers.middlewares.HackHostMiddleware': 1,
}
# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    'crawlers.extensions.SaveErrorsExtension': 100,
}

ITEM_PIPELINES = {
    'crawlers.pipelines.DuplicatesPipeline': 1,
    'crawlers.pipelines.FilterYoutubeUrls': 10,
    'crawlers.pipelines.FilterSoundcloudUrls': 10,
    'scrapy.pipelines.images.ImagesPipeline': 50,
    'scrapy.pipelines.files.FilesPipeline': 50,
    'crawlers.pipelines.YoutubePipeline': 60,
    'crawlers.pipelines.SetFileSize': 100,
    'crawlers.pipelines.SetImageSize': 100,
    'crawlers.pipelines.SetDocumentSize': 110,
    'crawlers.pipelines.SqlAlchemyPipeline': 300,
}
IMAGES_STORE = os.getenv('FILES_STORE', '/tmp/storage')
FILES_STORE = os.getenv('FILES_STORE', '/tmp/storage')

DOWNLOAD_YOUTUBE = True  # TODO move to spider args

RETRY_ENABLED = True
RETRY_TIMES = 3

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
