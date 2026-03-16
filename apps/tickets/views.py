from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import PurchaseSerializer
from apps.emails.services import send_purchase_confirmation, send_ticket_receipt

# Resumen:
# Endpoint de compra: valida datos, crea ticket y dispara correos de confirmación.
class PurchaseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Flujo corto: validar -> guardar -> notificar por email -> responder al frontend.
        serializer = PurchaseSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            ticket = serializer.save()
            # Enviar emails
            send_purchase_confirmation(request.user.email, ticket)
            send_ticket_receipt(request.user.email, ticket)
            return Response({
                'message': 'Compra exitosa',
                'ticket_id': ticket.id,
                'reservation_id': ticket.reservation.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
