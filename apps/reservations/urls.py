from django.urls import path
from .views import ReservationCreateView, UserReservationsView

# Resumen:
# Rutas de reservas: crear y consultar historial.
urlpatterns = [
    # POST para crear una nueva reserva.
    path('', ReservationCreateView.as_view(), name='reservation-create'),
    # GET para ver reservas del usuario actual.
    path('user', UserReservationsView.as_view(), name='user-reservations'),
]