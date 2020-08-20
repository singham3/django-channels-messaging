from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import re_path
from Messaging.consumers import *


application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                re_path(r'ws/chat/(?P<room_name>\w+)/(?P<method>\w+)/(?P<page>\w+)/$', ChatConsumer),
                ]
            )
        ),
    ),
})
