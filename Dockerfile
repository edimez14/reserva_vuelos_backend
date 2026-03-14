# Resumen:
# Este Dockerfile empaqueta el backend para ejecutarlo en cualquier servidor.
# Primero instala dependencias, copia el proyecto y al final levanta Django con Gunicorn.

# Usa imagen oficial de Python 3.14 slim (Debian)
FROM python:3.14-slim

# Establece variables de entorno
# - PYTHONDONTWRITEBYTECODE evita crear archivos .pyc dentro del contenedor.
# - PYTHONUNBUFFERED hace que los logs salgan en tiempo real.
# - PORT define el puerto por donde escuchará la app.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

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

# Crea un usuario no root para ejecutar la aplicación
# Buena práctica de seguridad: no correr procesos como root.
RUN addgroup --system app && adduser --system --group app
USER app

# Expone el puerto (se puede sobreescribir con variable de entorno)
EXPOSE $PORT

# Comando para ejecutar la aplicación con Gunicorn
# Ojo: el módulo apunta al objeto WSGI del proyecto.
CMD gunicorn --bind 0.0.0.0:$PORT flight_reservation.wsgi:application