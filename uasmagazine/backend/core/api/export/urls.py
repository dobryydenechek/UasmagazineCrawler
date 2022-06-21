from django.conf.urls import url

from core.api.export.views import ExportViewSet

urlpatterns = [
    url(r'create/', ExportViewSet.as_view({'post': 'create'})),
    url(r'(?P<pk>[0-9]+)/$',
        ExportViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy', 'patch': 'partial_update'})),
    url(r'$', ExportViewSet.as_view({'get': 'list', 'post': 'create'})),
]
