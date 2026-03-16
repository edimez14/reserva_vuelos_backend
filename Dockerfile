# Resumen:
# Este Dockerfile empaqueta el backend para ejecutarlo en cualquier servidor.
# Primero instala dependencias, copia el proyecto y al final levanta Django con Gunicorn.

# Usa imagen oficial de Python 3.14 slim (Debian)
FROM python:3.14-slim

# Establece variables de entorno de Python.
# - PYTHONDONTWRITEBYTECODE evita crear archivos .pyc dentro del contenedor.
# - PYTHONUNBUFFERED hace que los logs salgan en tiempo real.
# Las variables de la aplicación (SECRET_KEY, DATABASE_URL, PORT, etc.)
# se inyectan en tiempo de ejecución mediante `fly secrets set` en Fly.io.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Establece el directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema necesarias para psycopg2 y otras herramientas
# (psycopg2 necesita libpq-dev para conectarse bien a PostgreSQL).
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copia el archivo de dependencias primero (aprovecha caché de Docker)
# Esto acelera builds futuros si no cambió requirements.txt.
COPY requirements.txt .

# Instala dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del proyecto
COPY . .

# Recolecta archivos estáticos en la imagen (WhiteNoise los sirve desde aquí).
# DJANGO_SETTINGS_MODULE y SECRET_KEY se pasan como args de build para que
# collectstatic pueda importar los settings sin una DB real disponible.
ARG SECRET_KEY=placeholder-for-build
ARG DJANGO_SETTINGS_MODULE=backend.settings
RUN SECRET_KEY=$SECRET_KEY \
    DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE \
    python manage.py collectstatic --no-input

# Crea un usuario no root para ejecutar la aplicación
# Buena práctica de seguridad: no correr procesos como root.
RUN addgroup --system app && adduser --system --group app
USER app

# Expone el puerto 8080, que es el que Fly.io inyecta automáticamente en $PORT.
EXPOSE 8080

# Comando para ejecutar la aplicación con Gunicorn.
# --workers 2: dos procesos para aprovechar la CPU compartida de Fly.
# --timeout 120: margen para requests lentos (consultas a API externa de vuelos).
CMD gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    backend.wsgi:application