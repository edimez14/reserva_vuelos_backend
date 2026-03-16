from django.db import models
from django.conf import settings
from apps.flights.models import Flight

# Resumen:
# Aquí están los modelos de reservas y pasajeros.
# Una reserva pertenece a un usuario y a un vuelo; además puede tener varios pasajeros.
class Reservation(models.Model):
    """Reserva de un vuelo realizada por un usuario."""
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        CONFIRMED = 'confirmed', 'Confirmada'
        CANCELLED = 'cancelled', 'Cancelada'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='Usuario'
    )
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='Vuelo'
    )
    passengers_count = models.PositiveIntegerField(verbose_name='Número de pasajeros')
    seat_selection = models.TextField(
        blank=True,
        help_text='Asientos seleccionados (formato libre: ej. 12A,12B)',
        verbose_name='Asientos'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Estado'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de reserva')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

    def __str__(self):
        return f'Reserva {self.id} - {self.user.email} - {self.flight.flight_number}'

class Passenger(models.Model):
    """Pasajero asociado a una reserva."""
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name='passengers',
        verbose_name='Reserva'
    )
    name = models.CharField(max_length=200, verbose_name='Nombre completo')
    document = models.CharField(max_length=50, verbose_name='Documento de identidad')
    seat = models.CharField(max_length=10, blank=True, verbose_name='Asiento asignado')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pasajero'
        verbose_name_plural = 'Pasajeros'

    def __str__(self):
        return f'{self.name} - {self.document}'