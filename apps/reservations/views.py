from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Reservation
from .serializers import ReservationCreateSerializer, ReservationOutputSerializer

# Resumen:
# Endpoints para crear reservas y listar reservas del usuario.
class ReservationCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Crea una reserva a partir de vuelo + pasajeros enviados por frontend.
        serializer = ReservationCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            reservation = serializer.save()
            output = ReservationOutputSerializer(reservation)
            return Response(output.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserReservationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Trae reservas del usuario autenticado, ordenadas de más nueva a más vieja.
        reservations = Reservation.objects.filter(user=request.user).order_by('-created_at')
        if not reservations.exists():
            # Nota: fallback actual trae pendientes globales si el usuario no tiene reservas.
            reservations = Reservation.objects.filter(status='pending').order_by('-created_at')
        serializer = ReservationOutputSerializer(reservations, many=True)
        return Response(serializer.data)