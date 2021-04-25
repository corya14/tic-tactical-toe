"""
ASGI config for ticTacticalToe project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

from channels.routing import ProtocolTypeRouter, URLRouter
import ticTacticalToe.routing
from channels.auth import AuthMiddlewareStack
import os

from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticTacticalToe.settings')
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            ticTacticalToe.routing.websocket_urlpatterns
        )
    ),
})
