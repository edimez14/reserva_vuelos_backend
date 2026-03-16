from django.urls import path
from .views import FlightSearchView

# Resumen:
# Rutas de la app de vuelos. Aquí conectamos endpoint -> vista.
urlpatterns = [
    # GET /api/v1/flights/search
    path('search', FlightSearchView.as_view(), name='flight-search'),
]