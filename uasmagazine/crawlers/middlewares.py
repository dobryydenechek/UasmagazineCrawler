class HackHostMiddleware(object):
    def process_request(self, request, spider):
        if hasattr(spider, 'hack_host'):
            url = request.url.replace(spider.public_url, spider.real_url)
            request._url = url
            request.headers.update({'Host': spider.host})

    def process_response(self, request, response, spider):
        if hasattr(spider, 'hack_host'):
            url = response.url.replace(spider.real_url, spider.public_url)
            response._url = url
            request._url = url

        return response
