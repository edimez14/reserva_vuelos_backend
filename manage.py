#!/usr/bin/env python
# Resumen:
# Este archivo es la "puerta" para ejecutar comandos de Django.
# Se usa para levantar el servidor, hacer migraciones y correr tareas del backend.
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    # Esta función prepara Django y ejecuta el comando que escribimos en terminal.
    # Ejemplos: `python manage.py runserver` o `python manage.py migrate`.
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
