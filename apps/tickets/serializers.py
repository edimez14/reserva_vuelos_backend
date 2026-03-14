from rest_framework import serializers
from apps.reservations.models import Reservation
from .models import Ticket

# Resumen:
# Este serializer valida la compra y crea el ticket de la reserva.
class PurchaseSerializer(serializers.Serializer):
    reservation_id = serializers.IntegerField()
    payment_method = serializers.CharField(max_length=50)  # solo simulación

    def validate_reservation_id(self, value):
        # Verifica que la reserva exista y siga pendiente antes de pagar.
        try:
            reservation = Reservation.objects.get(id=value)
        except Reservation.DoesNotExist:
            raise serializers.ValidationError("La reserva no existe.")

        if reservation.status != 'pending':
            raise serializers.ValidationError("La reserva no está pendiente.")

        self.context['reservation'] = reservation
        return value

    def save(self):
        # Crea ticket y deja la reserva como confirmada.
        reservation = self.context['reservation']
        ticket = Ticket.objects.create(
            reservation=reservation,
            payment_method=self.validated_data['payment_method'],
            status='paid'
        )
        reservation.status = 'confirmed'
        reservation.save()
        return ticket