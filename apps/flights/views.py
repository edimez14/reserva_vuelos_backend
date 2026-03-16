from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .services import FlightAPIService
from .serializers import FlightSearchSerializer, FlightOutputSerializer

# Resumen:
# Esta vista recibe filtros de búsqueda, llama a la API externa y responde vuelos listos para el frontend.
class FlightSearchView(APIView):
    """
    Endpoint para buscar vuelos desde API externa
    """
    # permission_classes = [IsAuthenticated]  # Solo usuarios registrados
    permission_classes = [AllowAny]  # Permitir acceso sin autenticación
    
    def get(self, request):
        # Validar parámetros
        serializer = FlightSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Llamar al servicio externo
        # La vista no hace lógica pesada: delega al service para mantener ordenado el código.
        service = FlightAPIService()
        result = service.search_flights(**serializer.validated_data)
        
        if 'error' in result:
            return Response(
                {'detail': result['error']},
                status=status.HTTP_502_BAD_GATEWAY
            )
        
        # Formatear respuesta
        # Reconvertimos para asegurar una estructura uniforme de salida.
        output_serializer = FlightOutputSerializer(result['flights'], many=True)
        return Response({
            'count': len(result['flights']),
            'results': output_serializer.data
        })
