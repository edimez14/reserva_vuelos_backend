from django.core.mail import send_mail
from django.conf import settings

def send_purchase_confirmation(user_email, ticket):
    subject = 'Confirmación de compra de boletos'
    message = f"""
    Hola,
    Tu compra ha sido confirmada.
    Ticket #{ticket.id}
    Reserva #{ticket.reservation.id}
    Vuelo: {ticket.reservation.flight.flight_number}
    Pasajeros: {ticket.reservation.passengers_count}
    Método de pago: {ticket.payment_method}
    Gracias por viajar con nosotros.
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )