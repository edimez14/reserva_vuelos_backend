from django.contrib import admin
from .models import Flight

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ['flight_number', 'airline', 'origin', 'destination', 'departure_time', 'price']
    list_filter = ['airline', 'origin', 'destination']
    search_fields = ['flight_number']