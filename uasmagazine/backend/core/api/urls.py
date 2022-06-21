from django.conf.urls import url, include
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Crawlers API')

urlpatterns = [
    url(r'^spider/', include('core.api.spider.urls')),
    url(r'^export/', include('core.api.export.urls')),
    url(r'^swagger/', schema_view),
]
