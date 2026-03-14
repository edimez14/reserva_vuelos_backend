"""
Resumen:
Este archivo expone la app para servidores WSGI.
Gunicorn normalmente usa esto para correr el backend en producción.

WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# `application` es el punto de entrada que usa Gunicorn/WSGI para ejecutar Django.
application = get_wsgi_application()
