from django.core import mail
from django.test import TestCase, override_settings

from apps.emails.services import (
	send_password_reset_email,
	send_purchase_confirmation,
	send_registration_email,
	send_ticket_receipt,
)
from apps.flights.models import Flight
from apps.reservations.models import Reservation
from apps.tickets.models import Ticket
from apps.users.models import User


@override_settings(
	EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
	DEFAULT_FROM_EMAIL='noreply@reserva-vuelos.com'
)
class EmailServiceTests(TestCase):
	def test_send_registration_email(self):
		send_registration_email('nuevo@correo.com', 'Nuevo Usuario')

		self.assertEqual(len(mail.outbox), 1)
		self.assertIn('Bienvenido', mail.outbox[0].subject)

	def test_send_password_reset_email(self):
		send_password_reset_email('usuario@correo.com', 'http://localhost/reset')

		self.assertEqual(len(mail.outbox), 1)
		self.assertIn('Recuperación de contraseña', mail.outbox[0].subject)

	def test_send_purchase_emails(self):
		user = User.objects.create_user(
			email='mailcompra@correo.com',
			name='Mail Compra',
			phone='3444444444',
			password='PasswordSeguro123!'
		)
		flight = Flight.objects.create(
			flight_number='VH100',
			airline='Viva',
			origin='Medellín',
			destination='Bogotá',
			departure_time='2026-06-01T12:00:00Z',
			arrival_time='2026-06-01T13:00:00Z',
			price='190.00',
			seats_available=90,
		)
		reservation = Reservation.objects.create(
			user=user,
			flight=flight,
			passengers_count=1,
			seat_selection='7C',
			status='confirmed'
		)
		ticket = Ticket.objects.create(
			reservation=reservation,
			payment_method='visa',
			status='paid'
		)

		send_purchase_confirmation(user.email, ticket)
		send_ticket_receipt(user.email, ticket)

		self.assertEqual(len(mail.outbox), 2)
		self.assertIn('Confirmación de compra', mail.outbox[0].subject)
		self.assertIn('billete electrónico', mail.outbox[1].subject)
