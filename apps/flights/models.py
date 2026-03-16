from django.db import models

# Resumen:
# Este modelo guarda vuelos en base de datos para poder relacionarlos con reservas.
# A veces vienen de API externa, pero aquí quedan en formato interno del sistema.
class Flight(models.Model):
    """Modelo que representa un vuelo (puede venir de API externa o ser propio)."""
    flight_number = models.CharField(max_length=20, unique=True, verbose_name='Número de vuelo')
    airline = models.CharField(max_length=100, verbose_name='Aerolínea')
    origin = models.CharField(max_length=100, verbose_name='Origen')
    destination = models.CharField(max_length=100, verbose_name='Destino')
    departure_time = models.DateTimeField(verbose_name='Fecha y hora de salida')
    arrival_time = models.DateTimeField(verbose_name='Fecha y hora de llegada')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio base')
    seats_available = models.PositiveIntegerField(verbose_name='Asientos disponibles')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Orden por fecha de salida para mostrar primero lo más cercano.
        verbose_name = 'Vuelo'
        verbose_name_plural = 'Vuelos'
        ordering = ['departure_time']

    def __str__(self):
        return f'{self.flight_number} - {self.origin} → {self.destination}'