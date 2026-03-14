"""
Resumen:
Este archivo expone la app para servidores ASGI.
Sirve para despliegues asíncronos (por ejemplo, websockets o alta concurrencia).

ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# `application` es el objeto que el servidor ASGI carga para arrancar Django.
application = get_asgi_application()
