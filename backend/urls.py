from django.contrib import admin
from django.urls import path, include
from apps.reservations.views import ReservationCreateView, UserReservationsView
from apps.tickets.views import PurchaseView

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
    # Reservas: rutas registradas directamente para evitar problema de barra final con POST.
    # El include() con prefijo sin barra daña el matching de sub-rutas, así que las declaramos aquí.
    path('api/v1/reservations', ReservationCreateView.as_view(), name='reservation-create'),
    path('api/v1/reservations/user', UserReservationsView.as_view(), name='user-reservations'),
    # Compra y emisión de ticket.
    path('api/v1/purchase', PurchaseView.as_view(), name='purchase'),
]