from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/flights/', include('apps.flights.urls')),
    path('api/v1/reservations/', include('apps.reservations.urls')),
    path('api/v1/tickets/', include('apps.tickets.urls')),
]