from django.conf.urls import url
from . import consumers
from django.urls import re_path

websocket_urlpatterns = [
    url(r'^ws/test/$', consumers.TestConsumer),
    re_path(r'ws/test/(?P<username>.*)/', consumers.UserTestConsumer),
]