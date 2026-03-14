from rest_framework import serializers
from apps.reservations.models import Reservation
from .models import Ticket

class PurchaseSerializer(serializers.Serializer):
    reservation_id = serializers.IntegerField()
    payment_method = serializers.CharField(max_length=50)  # solo simulación

    def validate_reservation_id(self, value):
        try:
            reservation = Reservation.objects.get(id=value)
        except Reservation.DoesNotExist:
            raise serializers.ValidationError("La reserva no existe.")
        if reservation.status != 'pending':
            raise serializers.ValidationError("La reserva no está pendiente.")
        if reservation.user != self.context['request'].user:
            raise serializers.ValidationError("No tienes permiso para comprar esta reserva.")
        return value

    def save(self):
        reservation = Reservation.objects.get(id=self.validated_data['reservation_id'])
        # Crear ticket
        ticket = Ticket.objects.create(
            reservation=reservation,
            payment_method=self.validated_data['payment_method'],
            status='paid'
        )
        # Actualizar estado de la reserva
        reservation.status = 'confirmed'
        reservation.save()
        return ticket