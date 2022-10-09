from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/processing/(?P<id>\d+)/$', consumers.MyConsumer.as_asgi()),
]
