from django.contrib import admin
from .models import Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'reservation', 'payment_method', 'status', 'issued_at']
    list_filter = ['status']
