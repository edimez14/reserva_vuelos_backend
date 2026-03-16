from django.contrib import admin
from .models import Reservation, Passenger

class PassengerInline(admin.TabularInline):
    model = Passenger
    extra = 0

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'flight', 'passengers_count', 'status', 'created_at']
    list_filter = ['status']
    inlines = [PassengerInline]

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ['name', 'document', 'reservation', 'seat']