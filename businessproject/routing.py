from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from cebula import routing


application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': URLRouter(
            routing.websocket_urlpatterns
        )
})