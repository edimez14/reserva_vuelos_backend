from django.db import models
from apps.reservations.models import Reservation

# Resumen:
# Modelo de ticket generado cuando una reserva pasa por compra.
# Es OneToOne con reserva: una reserva confirmada tiene un solo ticket.
class Ticket(models.Model):
    """Boleto aéreo generado tras la compra de una reserva."""
    class Status(models.TextChoices):
        PAID = 'paid', 'Pagado'
        ISSUED = 'issued', 'Emitido'
        CANCELLED = 'cancelled', 'Cancelado'

    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.CASCADE,
        related_name='ticket',
        verbose_name='Reserva'
    )
    payment_method = models.CharField(max_length=50, verbose_name='Método de pago')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PAID,
        verbose_name='Estado'
    )
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de emisión')

    class Meta:
        verbose_name = 'Boleto'
        verbose_name_plural = 'Boletos'

    def __str__(self):
        return f'Boleto #{self.id} - Reserva {self.reservation.id}'