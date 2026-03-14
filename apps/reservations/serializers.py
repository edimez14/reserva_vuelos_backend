from rest_framework import serializers
from .models import Reservation, Passenger
from apps.flights.models import Flight

# Resumen:
# Este archivo transforma datos para crear reservas y listar resultados.
# Aquí validamos la estructura del vuelo y creamos reserva + pasajeros en cadena.
class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ['name', 'document', 'seat']

class ReservationCreateSerializer(serializers.Serializer):
    # Datos del vuelo (vienen de la API)
    flight_data = serializers.DictField()
    passengers = PassengerSerializer(many=True)
    seat_selection = serializers.CharField(required=False, allow_blank=True)

    def validate_flight_data(self, value):
        # Revisamos campos mínimos para evitar crear reservas incompletas.
        # Validar que tenga los campos necesarios
        required = ['flight_number', 'airline', 'origin', 'destination',
                    'departure_time', 'arrival_time', 'price']
        for field in required:
            if field not in value:
                raise serializers.ValidationError(f"Falta campo {field}")
        return value

    def create(self, validated_data):
        # 1) Busca o crea vuelo, 2) crea reserva, 3) crea pasajeros.
        user = self.context['request'].user
        flight_data = validated_data['flight_data']
        passengers_data = validated_data['passengers']
        seat_selection = validated_data.get('seat_selection', '')

        # Buscar o crear el vuelo en la BD
        flight, created = Flight.objects.get_or_create(
            flight_number=flight_data['flight_number'],
            departure_time=flight_data['departure_time'],
            defaults={
                'airline': flight_data['airline'],
                'origin': flight_data['origin'],
                'destination': flight_data['destination'],
                'arrival_time': flight_data['arrival_time'],
                'price': flight_data['price'],
                'seats_available': 150  # valor por defecto, luego podrías actualizar
            }
        )

        # Crear reserva
        reservation = Reservation.objects.create(
            user=user,
            flight=flight,
            passengers_count=len(passengers_data),
            seat_selection=seat_selection,
            status='pending'
        )

        # Crear pasajeros
        for p_data in passengers_data:
            Passenger.objects.create(reservation=reservation, **p_data)

        return reservation

class ReservationOutputSerializer(serializers.ModelSerializer):
    # Serializer de salida para mostrar info principal de cada reserva.
    flight = serializers.StringRelatedField()  # o puedes anidar más detalles
    class Meta:
        model = Reservation
        fields = ['id', 'flight', 'passengers_count', 'seat_selection', 'status', 'created_at']