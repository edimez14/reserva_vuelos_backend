from rest_framework import serializers

class FlightSearchSerializer(serializers.Serializer):
    """
    Valida parámetros de búsqueda
    """
    origin = serializers.CharField(required=False, max_length=3, min_length=3)
    destination = serializers.CharField(required=False, max_length=3, min_length=3)
    date = serializers.DateField(required=False, input_formats=['%Y-%m-%d'])
    airline = serializers.CharField(required=False)
    direct = serializers.BooleanField(required=False)

    def validate_origin(self, value):
        return value.upper()

    def validate_destination(self, value):
        return value.upper()
    
    def validate(self, data):
        # Si no hay origen ni destino, mostramos todos (pero con límite)
        return data

class FlightOutputSerializer(serializers.Serializer):
    """
    Formato de respuesta para vuelos
    """
    flight_number = serializers.CharField()
    airline = serializers.CharField()
    origin = serializers.CharField()
    origin_iata = serializers.CharField()
    destination = serializers.CharField()
    destination_iata = serializers.CharField()
    departure_time = serializers.DateTimeField(allow_null=True)
    arrival_time = serializers.DateTimeField(allow_null=True)
    status = serializers.CharField()
    price = serializers.IntegerField()
    seats_available = serializers.IntegerField()