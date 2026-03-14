from django.contrib import admin
from django.urls import path, include

# Resumen:
# Este archivo conecta todas las rutas principales del backend.
# Piensa en esto como el "mapa grande" que manda cada URL a su app.
urlpatterns = [
    # Panel de administración de Django.
    path('admin/', admin.site.urls),
    # Módulo de autenticación/usuarios.
    path('api/v1/auth/', include('apps.users.urls')),
    # Módulo de búsqueda de vuelos.
    path('api/v1/flights/', include('apps.flights.urls')),
    # Módulo para crear y listar reservas.
    path('api/v1/reservations/', include('apps.reservations.urls')),
    # Módulo de compra y emisión de ticket.
    path('api/v1/tickets/', include('apps.tickets.urls')),
]