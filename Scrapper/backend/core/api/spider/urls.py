from django.conf.urls import url

from core.api.spider.views import SpiderViewSet

urlpatterns = [
    url(r'document-statistics/', SpiderViewSet.as_view({'get': 'document_statistics'})),
    url(r'status/', SpiderViewSet.as_view({'get': 'status'})),
    url(r'add/', SpiderViewSet.as_view({'post': 'add_spiders'})),
    url(r'^(?P<pk>[0-9]+)/start/$', SpiderViewSet.as_view({'post': 'start'})),
    url(r'^(?P<pk>[0-9]+)/stop/$', SpiderViewSet.as_view({'post': 'stop'})),
    url(r'^(?P<pk>[0-9]+)/reset/$', SpiderViewSet.as_view({'post': 'reset'})),
    url(r'(?P<pk>[0-9]+)/$',
        SpiderViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy', 'patch': 'partial_update'})),
    url(r'$', SpiderViewSet.as_view({'get': 'list', 'post': 'create'})),
]
