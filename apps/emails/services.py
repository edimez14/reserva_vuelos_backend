# apps/emails/services.py
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

def send_registration_email(user_email, user_name):
    subject = 'Bienvenido a Reserva Vuelos'
    message = f"""
    Hola {user_name},
    Gracias por registrarte en nuestra plataforma.
    Tu cuenta ha sido creada exitosamente.
    Ya puedes iniciar sesión.
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )

def send_password_reset_email(user_email, reset_link):
    subject = 'Recuperación de contraseña'
    message = f"""
    Hola,
    Has solicitado restablecer tu contraseña.
    Haz clic en el siguiente enlace: {reset_link}
    Si no solicitaste este cambio, ignora este correo.
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )

def send_purchase_confirmation(user_email, ticket):
    subject = 'Confirmación de compra'
    message = f"""
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

def send_ticket_receipt(user_email, ticket):
    # Podría ser más detallado con PDF, pero por ahora texto simple
    subject = 'Tu billete electrónico'
    message = f"""
    Adjuntamos tu billete para el vuelo {ticket.reservation.flight.flight_number}.
    Puedes presentarlo en el aeropuerto.
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )